from icecream import ic
from reformat import Reformatter
from ubo_utils import load_text


def main():
    reformatter = Reformatter()
    reformatter.load_template(load_text('test.txt'))
    reformatter.summary('filterset (summary)')
    reformatter.listset('listset (total-discarded, last-updated)')

    for ruleset in ['switchRuleset', 'hostRuleset', 'urlRuleset']:
        if ruleset not in reformatter.troubleshoot:
            continue
        
        reformatter.ruleset(ruleset)

    for key in ['modifiedUserSettings', 'modifiedHiddenSettings']:
        reformatter.user_hidden(key)
    
    ic(reformatter.troubleshoot)


if __name__ == "__main__":
    main()