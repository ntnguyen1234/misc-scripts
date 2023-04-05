import asyncio
import contextlib
import csv
import functools
import html
import json
import re
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path, PosixPath, WindowsPath
from time import perf_counter, sleep
from typing import Any, Callable, Coroutine, Generator, Literal, Self
from urllib.parse import parse_qsl, unquote, urlparse, urlunparse

import httpx
import joblib
import pandas as pd
import tldextract
from bs4 import BeautifulSoup, Comment, Tag
from orjson import loads
from pandas.core.frame import DataFrame
from rich_dataframe import prettify
from tqdm import std, tqdm
from unidecode import unidecode


def multireplace(string: str, replacements: dict) -> str:
    """
    Given a string and a replacement map, it returns the replaced string.

    :param str string: string to execute replacements on
    :param dict replacements: replacement dictionary {value to find: value to replace}
    :rtype: str

    """
    if not replacements:
        return string
        
    # Place longer ones first to keep shorter substrings from matching
    # where the longer ones should take place
    # For instance given the replacements {'ab': 'AB', 'abc': 'ABC'} against 
    # the string 'hey abc', it should produce 'hey ABC' and not 'hey ABc'
    substrs = sorted(replacements, key=len, reverse=True)

    # Create a big OR regex that matches any of the substrings to replace
    regexp = re.compile('|'.join(map(re.escape, substrs)))

    # For each match, look up the new string in the replacements
    return regexp.sub(lambda match: replacements[match.group(0)], string)


def clean_split(
    text: str, 
    seps: str, 
    verbose: bool = False
) -> Generator[str | Any, None, None]:
    """Split string, strip and clean empty part
    
    text (str): string to split
    sep (str): separator"""

    if verbose is True:
        print(seps, re.split(seps, text))

    for part in re.split(seps, text):
        if (item := part.strip()):
            yield item


@dataclass
class CurlContext:
    method: str
    url: str
    params: dict
    data: str | None
    data_binary: str | None
    headers: dict
    cookies: dict | None
    json: dict | None


def split_header(header_str: str, key: str) -> str:
    """Tach header trong moi phan cua cURL
    
    header_str (str): doan string trong moi phan cua cURL can tach
    key (str): string bat dau trong moi phan"""

    if (header_strip := header_str.split(key)[-1].strip()).startswith(("'", '"')):
        return header_strip.replace(header_strip[0], '')
    else:
        return header_strip


def get_cookies(part_header: str) -> dict:
    """Lay cookies tu header
    
    part_header (str): header lay tu cURL"""

    # Khoi tao cookies
    cookies = dict()

    # Tach moi cookie, lay key va value
    for cookie_str in split_header(part_header, 'Cookie:').split(';'):
        cookie_split = cookie_str.split('=')
        # cookies[unquote(cookie_split[0].strip())] = unquote('='.join(cookie_split[1:]).strip())
        cookies[cookie_split[0].strip()] = '='.join(cookie_split[1:]).strip()

    return cookies


def uncurl(curl: str, un_quote: bool = False) -> CurlContext:
    """Phan tich lenh cURL
    
    curl (str): lenh cURL dang POSIX tu Firefox"""

    # Khoi tao headers
    curl_context = {key: None for key in ['method', 'url', 'params', 'data', 'data_binary', 'headers', 'cookies', 'json']}
    curl_context['headers'] = dict()
    curl_context['method'] = 'GET'

    # URL and params
    pattern = re.compile(r"""(?<=curl ')(?:.*?)(?=')|(?<=curl \")(?:.*?)(?=\")|(?<=--url \')(?:.*?)(?=\')|(?<=--url \")(?:.*?)(?=\")""")
    parsed_url = urlparse(re.search(pattern, curl)[0])
    curl_context['url'] = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
    curl_context['params'] = dict(parse_qsl(parsed_url.query))

    # Method
    pattern = re.compile(r"""(?:(?<=-X )(?:.*?)(?= )|(?<=--request )(?:.*?)(?= ))""")
    if (curl_method := re.search(pattern, curl)):
        curl_context['method'] = curl_method[0]        

    # Headers
    pattern = re.compile(r"""(?:(?<=-H ')(?:.*?)(?=')|(?<=-H \")(?:.*?)(?=\")|(?<=--header \')(?:.*?)(?=\')|(?<=--header \")(?:.*?)(?=\"))""")
    for item in re.findall(pattern, curl):
        item: str
        parts = tuple(clean_split(item, ':'))
        parts_1 = ':'.join(parts[1:])

        if item.lower().startswith('cookie'):
            curl_context['cookies'] = get_cookies(parts_1)
        else:
            if 'accept-encoding' in parts[0].lower():
                continue

            curl_context['headers'][parts[0]] = parts_1

    # data
    pattern = re.compile(r"""(?:(?<=--data-raw ')(?:.*?)(?='))""", re.DOTALL)
    if (data := re.search(pattern, curl)):
        curl_context['method'] = 'POST'
        curl_context['data'] = data[0]
        if un_quote:
            curl_context['data'] = unquote(curl_context['data'])
        if '{' in data[0]:
            curl_context['json'] = json.loads(curl_context['data'], strict=False)

    # data-binary
    pattern = re.compile(r"""(?:(?<=--data-binary \$')(?:.*?)(?=')|(?<=--data-binary \$\")(?:.*?)(?=\"))""", re.DOTALL)
    if (data_binaries := re.search(pattern, curl)):
        curl_context['method'] = 'POST'
        curl_context['data_binary'] = data_binaries[0]

    # Return
    return CurlContext(
        method=curl_context['method'],
        url=curl_context['url'],
        params=curl_context['params'],
        data=curl_context['data'],
        data_binary=curl_context['data_binary'],
        headers=curl_context['headers'],
        cookies=curl_context['cookies'],
        json=curl_context['json']
    )


@contextlib.contextmanager
def tqdm_joblib(tqdm_object: std.tqdm) -> Generator[tqdm, None, None]:
    """Context manager to patch joblib to report into tqdm progress bar given as argument"""
    class TqdmBatchCompletionCallback(joblib.parallel.BatchCompletionCallBack):
        def __call__(self, *args, **kwargs):
            tqdm_object.update(n=self.batch_size)
            return super().__call__(*args, **kwargs)

    old_batch_callback = joblib.parallel.BatchCompletionCallBack
    joblib.parallel.BatchCompletionCallBack = TqdmBatchCompletionCallback
    try:
        yield tqdm_object
    finally:
        joblib.parallel.BatchCompletionCallBack = old_batch_callback
        tqdm_object.close()


def rate_limited(
    max_concurrent: int, 
    duration: float
) -> Callable[..., Callable[..., Coroutine]]:
    def decorator(func) -> Callable[..., Coroutine]:
        semaphore = asyncio.Semaphore(max_concurrent)

        async def dequeue():
            try:
                await asyncio.sleep(duration)
            finally:
                semaphore.release()

        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            await semaphore.acquire()
            asyncio.create_task(dequeue())
            return await func(*args, **kwargs)

        return wrapper
    return decorator


def clean_file(text: str) -> str:
    return multireplace(
        html.unescape(text), 
        {
            '/': '-',
            '|': '-',
            '*': '-',
            '\\': '-',
            ':': ' -',
            '<': '',
            '>': '',
            '?': '',
            '"': '\'',
            '...': ''
        }
    ).strip()


def clean_text(file_path: str | PosixPath | WindowsPath) -> str:
    escapes = {
        '&a;': '&',
        '&q;': '"',
        '&s;': '\'',
        '&l;': '<',
        '&g;': '>',
    }
    try:
        text = load_text(file_path).strip()
        return unquote(
            multireplace(text, escapes).
            encode(encoding='utf-8').
            decode('unicode-escape')
        )
    except UnicodeDecodeError:
        with open(file_path, 'rb') as fr:
            text = fr.read().decode('unicode-escape').strip()
        
        return unquote(multireplace(text, escapes))


def clean_text_2(text: str) -> str:
    escapes = {
        '&a;': '&',
        '&q;': '"',
        '&s;': '\'',
        '&l;': '<',
        '&g;': '>',
    }
    return unquote(
        multireplace(text, escapes)
        .encode(encoding='utf-8')
        .decode('unicode-escape')
    )


def str_contain(text: str, substrings: list[str] | set[str]) -> bool:
    return any((substring in text for substring in substrings))


def strip_str(text: str) -> str:
    return re.sub(r'^\W+|\W+$', '', text)


def clean_lines(text: str, removals: list[str]) -> str:
    new_text = text.strip()
    for removal in removals:
        while (double_r := f'{removal}{removal}') in new_text:
            new_text = new_text.replace(double_r, removal)

    return new_text


def duplicates(sequence: list | tuple) -> list:
    seen = set()
    return [x for x in sequence if x in seen or seen.add(x)]


def uniques(sequence) -> list:
    return list(dict.fromkeys(sequence))


def append_text(text: str | int, file_path: str | PosixPath | WindowsPath):
    with open(file_path, 'a', encoding='utf-8') as fa:
        fa.write(f'{text}\n')

        
def load_csv(
    file_path: str | PosixPath | WindowsPath,
    is_list: bool = True
) -> list[dict[str | Any, str | Any]]:
    with open(file_path, 'r', encoding='utf-8', errors='surrogateescape') as fr:
        csv_reader = csv.DictReader(fr)

        if is_list:
            return list(csv_reader)
        else:
            for line in csv_reader:
                yield line


def load_df(
    file_path: str | PosixPath | WindowsPath, 
    usecols: list[str] = None,
    dtypes: dict[str, str] = None
) -> DataFrame:
    if isinstance(file_path, str):
        new_path = Path(file_path).resolve()
    else:
        new_path = file_path

    if new_path.suffix in {'.xls', '.xlsx'}:
        df: DataFrame = pd.read_excel(new_path, 
        usecols=usecols, 
        use_nullable_dtypes=True, 
        dtype='string[pyarrow]'
    )
    else:
        df: DataFrame = pd.read_csv(
            new_path, 
            usecols=usecols, 
            encoding='utf-8', 
            engine='pyarrow',
            dtype='string[pyarrow]', 
        )
    
    if dtypes is not None:
        for key, value in dtypes.items():
            if value.lower().startswith('int'):
                df[key] = df[key].astype(float).round().astype(value)
            else:
                df[key] = df[key].astype(value)
    return df


def load_json(file_path: str | PosixPath | WindowsPath) -> list | dict:
    with open(file_path, 'r', encoding='utf-8') as fr:
        return json.load(fr)


def load_text(
    file_path: str | PosixPath | WindowsPath, 
    is_list: bool = False
) -> Generator[str | Any, None, None] | str:
    with open(file_path, 'r', encoding='utf-8') as fr:
        fr_read = fr.read().strip()
        
    if is_list is True:
        return clean_split(fr_read, '\n')
    else:
        return fr_read


def orload_json(file_path: str | PosixPath | WindowsPath) -> list | dict:
    with open(file_path, 'r', encoding='utf-8') as fr:
        return loads(fr.read())


def save_csv(df: DataFrame, csv_path: str | PosixPath | WindowsPath):
    df.to_csv(csv_path, encoding='utf-8', index=False, na_rep=None, escapechar='\\')


def write_csv(data, file_path: str | PosixPath | WindowsPath, fieldnames: list = None):
    if (
        (fieldnames is None) 
        and isinstance(data, list)
        and isinstance(data[0], dict)
    ):
        fieldnames = list(data[0].keys())

    with open(file_path, 'w', newline='', encoding='utf-8', errors='surrogateescape') as fw:
        csv_writer = csv.DictWriter(fw, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(data)


def write_json(data, file_path: str | PosixPath | WindowsPath):
    with open(file_path, 'w', encoding='utf-8', errors='surrogateescape') as fw:
        json.dump(data, fw, indent=4, ensure_ascii=False)


def write_text(data, file_path: str | PosixPath | WindowsPath):
    with open(file_path, 'w', encoding='utf-8', errors='surrogateescape') as fw:
        if isinstance(data, str):
            fw.write(data.strip())
        else:
            for item in data:
                fw.write(f'{item}\n')


def unique_path(pathname: str | PosixPath | WindowsPath) -> PosixPath | WindowsPath:
    if isinstance(pathname, str):
        path_name = Path(pathname).resolve()
    else:
        path_name = pathname

    path_temp = path_name
    idx = 1
    while path_temp.is_dir() or path_temp.is_file():
        path_temp = path_name.parent / f'{path_name.stem}_{idx}{path_name.suffix}'
        idx += 1

    return path_temp


def name_combinations(full_name: str) -> list[tuple[str, str]]:
    name_split = list(clean_split(unidecode(full_name).lower(), '[^a-zA-Z]'))
    return list(combinations(name_split, 2))


def removeprefixes(text: str, prefixes: list[str] | Generator[str, None, None]) -> str:
    new_text = text
    for prefix in prefixes:
        new_text = new_text.removeprefix(prefix)
    return new_text


def extract_domain(text: str) -> str | None:
    tld_res = tldextract.extract(text.split()[0].strip())
    if tld_res.registered_domain:
        return removeprefixes('.'.join(tld_res), ['.', 'www.'])


def extract_domain_2(element: str) -> tuple[str, ...]:
    low_element = element.lower()
    tld_domain = tldextract.extract(low_element).registered_domain

    if '@' in low_element:
        domain = list(clean_split(low_element, '@'))[-1]
        domain = re.sub(r'^\W+|\W+$', '', domain)
        return tuple(uniques((domain, tld_domain)))

    elif '://' in low_element:
        element_split = list(clean_split(low_element, r'\/|\?|#'))
        if len(element_split) <= 1:
            return ()
        original_domain = element_split[1].replace('www.', '')
        original_domain = re.sub(r'^\W+|\W+$', '', original_domain)
        return tuple(uniques((original_domain, tld_domain)))
        
    return tuple(uniques((low_element, tld_domain)))


def forward_domain(domain: str) -> list[str]:
    results = [domain]
    
    temp_domain = domain
    while len(temp_domain.split('.')) > 2:
        temp_domain = '.'.join(temp_domain.split('.')[:-1])
        results.append(temp_domain)

    return results


def backward_domain(domain: str) -> list[str]:
    results = [domain]
    
    temp_domain = domain
    while len(temp_domain.split('.')) > 3:
        temp_domain = '.'.join(temp_domain.split('.')[1:])
        results.append(temp_domain)

    return results


def extract_sub_domain(website: str) -> tuple[str, list[str]]:
    website = website.lower()

    if not (tld_domain := tldextract.extract(website).registered_domain):
        return None, None

    match len(domain_split := list(clean_split(website, r'\/|\?|#'))):
        case 0:
            return None, None
        case 1:
            pos = 0
        case _:
            pos = 1

    original_domain = strip_str(domain_split[pos]).replace('www.', '')
    results = (
        forward_domain(original_domain) + backward_domain(original_domain) 
        + forward_domain(tld_domain) + backward_domain(tld_domain)
    )

    return original_domain, list(set(results))


def is_website(website: str) -> bool:
    return tldextract.extract(website.lower()).registered_domain != ''


def combine_list(original_list: list[list]) -> list:
    new_list = []
    for item in original_list:
        if isinstance(item, list):
            new_list.extend(item)
        else:
            new_list.append(item)

    return new_list


def extract_emails_text(text: str) -> Generator[str, None, None]:
    extensions = ['jpeg', 'jpg', 'gif', 'png', 'svg', 'webp']
    pattern = r'(?:[a-z0-9](?:\.|\-|\_|\+)?)*[a-z0-9]@[a-z0-9](?:(?:\.|\-)?[a-z0-9]+)*\.(?:[a-z]{2,})+'
    for mail_address in uniques(re.findall(pattern, text.lower())):
        mail_address: str
        if mail_address.split('.')[-1] in extensions:
            continue

        yield mail_address


def extract_emails(response_content: bytes | str) -> list[str]:
    soup = BeautifulSoup(response_content, features='lxml')
    for tag in soup.select('script, noscript, svg, img, style, [placeholder], input'):
        tag.extract()

    for element in soup(text=lambda text: isinstance(text, Comment)):
        element: Tag
        element.extract()

    for tag in soup.select('[href], [src], [srcset], meta[content]'):
        del tag['src']
        del tag['srcset']
        del tag['content']

        if ('href' in tag) and ('mailto' not in tag['href']):
            del tag['href']

    return extract_emails_text(str(soup))


def is_mail(mail_address: str) -> bool:
    mail_extract = next(extract_emails_text(mail_address))
    if mail_extract and (mail_extract == mail_address):
        return True
    else:
        return False


def print_df(df: DataFrame, cols: int = 10, rows: int = 20):
    prettify(df, delay_time=1e-6, clear_console=False, col_limit=cols, row_limit=rows)


def count_lines(file_path: str | PosixPath | WindowsPath) -> int:
    with open(file_path, 'r', encoding='utf-8') as fr:
        return sum(1 for _ in fr)


def count_file(dir_path: str | PosixPath | WindowsPath, pattern: str = '*') -> int:
    if isinstance(dir_path, str) is True:
        new_folder = Path(dir_path).resolve()
    else:
        new_folder = dir_path

    return sum(1 for _ in new_folder.glob(pattern))


class catchtime:
    def __enter__(self) -> Self:
        self.time = perf_counter()
        return self

    def __exit__(self, type, value, traceback):
        self.time = perf_counter() - self.time
        self.readout = f'Time: {self.time:.6f} seconds'
        print(self.readout)


def list_2_dict(all_data, key_ex: str) -> dict:
    data_dict = dict()
    for data in all_data:
        data: dict
        data_dict[data[key_ex]] = dict()

        for key, value in data.items():
            if key == key_ex:
                continue

            data_dict[data[key_ex]][key] = value

    return data_dict


def create_dir(dir_name: str | PosixPath | WindowsPath) -> PosixPath | WindowsPath:
    (dir_path := Path(dir_name).resolve()).mkdir(exist_ok=True)
    return dir_path


def clone_soup(soup: BeautifulSoup, selectors: list[str]) -> Tag:
    new_soup = soup.new_tag('html')
    head = soup.new_tag('head')

    for tag in soup.select('head > *'):
        head.insert(len(head.contents), tag)
    
    new_soup.insert(0, head)

    body = soup.select_one('body')

    for selector in selectors:
        body.insert(len(body.contents), soup.select_one(selector))

    return new_soup


def verify_mail(
    mails,
    curl: str,
    time_sleep: float = 0
) -> bool | Generator[tuple[str, Literal[True]] | tuple[str, Literal[False]], None, None]:
    v_context = uncurl(curl, True)
    current_mail = next(extract_emails_text(v_context.data))

    with httpx.Client(
        headers=v_context.headers,
        cookies=v_context.cookies,
        http2=True,
        timeout=httpx.Timeout(10),
        follow_redirects=True
    ) as client:
        if isinstance(mails, str):
            if not mails:
                return False
                
            response = client.post(
                url=v_context.url,
                params=v_context.params,
                data=v_context.data.replace(current_mail, mails)
            )
            if 'googleusercontent' in response.text:
                return True
            else:
                return False
        else:
            for mail in mails:
                if not mail:
                    return (mail, False)

                response = client.post(
                    url=v_context.url,
                    params=v_context.params,
                    data=v_context.data.replace(current_mail, mail)
                )

                if 'googleusercontent' in response.text:
                    yield (mail, True)
                else:
                    yield (mail, False)

                sleep(time_sleep)