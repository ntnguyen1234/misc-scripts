from icecream import ic
from reformat import Reformatter
from ubo_utils import load_text, write_json, write_text
from yaml import dump


def main():
    reformatter = Reformatter()
    # reformatter.load_template(load_text('test.txt'))
    text = input('>>> ').replace('\\"', '"')
    reformatter.load_template(text)
    
    for key in reformatter.troubleshoot:
        key: str

        if key.startswith(('Chromium', 'Firefox', 'uBlock Origin')):
            continue

        match key:
            case 'filterset (summary)':
                reformatter.summary(key)
            case 'listset (total-discarded, last-updated)':
                reformatter.listset(key)
            case _:
                reformatter.others(key)

    yaml_str: str = dump(reformatter.troubleshoot, sort_keys=False)
    yaml_str = yaml_str.replace("'", '').replace('  - ', '    ')
    # print('\n')
    # ic(reformatter.troubleshoot)
    print('\n')
    print(yaml_str)
    yaml_reddit = '\n'.join([f'    {line}' for line in yaml_str.split('\n')])
    print('\n')
    print(yaml_reddit)
    # write_text(yaml_str, 'temp.yaml')
    # write_json(reformatter.troubleshoot, 'temp.json')


if __name__ == "__main__":
    main()