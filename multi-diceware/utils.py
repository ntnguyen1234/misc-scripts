import re


def clean_split(
    text: str, 
    seps: str, 
    verbose: bool = False
):
    """Split string, strip and clean empty part
    
    text (str): string to split
    sep (str): separator"""

    if verbose is True:
        print(seps, re.split(seps, text))

    for part in re.split(seps, text):
        if (item := part.strip()):
            yield item


def load_text(file_path, is_list: bool = False):
    with open(file_path, 'r', encoding='utf-8') as fr:
        fr_read = fr.read().strip()
        
    if is_list is True:
        return clean_split(fr_read, '\n')
    else:
        return fr_read