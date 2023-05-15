from icecream import ic
from reformat import Reformatter
from ubo_utils import load_text


def main():
    reformatter = Reformatter()
    reformatter.load_template(load_text('test.txt'))
    
    for key in reformatter.troubleshoot:
        key: str

        if key.startswith(('Chromium', 'Firefox', 'uBlock Origin')):
            continue

        match key:
            case 'filterset (summary)':
                reformatter.summary(key)
            case 'listset (total-discarded, last-updated)':
                reformatter.listset(key)
            case 'popupPanel':
                continue
            case _:
                reformatter.others(key)
    
    ic(reformatter.troubleshoot)


if __name__ == "__main__":
    main()