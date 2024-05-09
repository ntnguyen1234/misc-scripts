from pathlib import Path
from secrets import randbelow

from utils import load_text


def general_dict(file: Path, worddict: dict, src_names: list[str], dice_length: int | None = None):
    src_names.append(src_name := file.stem)

    for line in load_text(file, True):
        if line.startswith('#'):
            continue

        line_pair = line.split()
        if line_pair[0] not in worddict:
            worddict[line_pair[0]] = {}

        worddict[line_pair[0]][src_name] = line_pair[1]
        
        if not dice_length:
            dice_length = len(line_pair[0])

    return worddict, dice_length, src_names


def normal_dict() -> dict[str, dict]:
    worddict = {}
    src_names = []
    dice_length = None

    for file in Path('normal').resolve().iterdir():
        worddict, dice_length, src_names = general_dict(file, worddict, src_names, dice_length)

    return worddict, dice_length, sorted(src_names)

def short_dict(file):
    worddict = {}
    src_names = []
    dice_length = None

    worddict, dice_length, src_names = general_dict(file, worddict, src_names, dice_length)
    return worddict, dice_length, src_names

def main():
    while True:
        if (password_length := int(input('\nPassword length (default 5)\n>>> ').strip() or '5')) < 1:
            exit()

        print(
"""
Choose your lists
0. Normal lists (default)
1. EFF short 1
2. EFF short 2
"""
        )
        list_choice = int(input('>>> ').strip() or '0')

        num_max = 100

        match list_choice:
            case 0:
                worddict, dice_length, src_names = normal_dict()
            case 1 | 2:
                worddict, dice_length, src_names = short_dict(Path('sources') / f'eff_short_wordlist_{list_choice}.txt')
            case _: 
                exit()

        dices = [
            ''.join(str(randbelow(6) + 1) for _ in range(dice_length)) 
            for _ in range(password_length)
        ]
        num_value = randbelow(num_max)
        num_position, title_position, special_position = (randbelow(password_length) + 1 for _ in range(3))

        if src_names:
            print()
            for src_name in src_names:
                print(src_name, end='\t')

        print('\n')

        combined: list[list[str]] = [[] for _ in range(max(1, len(src_names)))]
        for dice in dices:
            dice_dict: dict = worddict[dice]

            for i, word in enumerate(dice_dict.values()):
                combined[i].append(word)
                end_line = ''
                if len(dice_dict) > 1:
                    end_line = ' '*(16 - len(word))

                print(word, end=end_line)
            print()

        print(f'\n{num_position = }')
        print(f'{num_value = }')
        print(f'{title_position = }')
        print(f'{special_position = }\n')

        for word_list in combined:
            word_lists = [word_list]

            if list_choice == 2:
                word_lists.append([letter[:3] for letter in word_list])

            for wlist in word_lists:
                wlist[title_position - 1] = wlist[title_position - 1].title()
                wlist[num_position - 1] += str(num_value)
                print('.'.join(wlist), end='\n\n')
        
        if (input('Continue?\n>>> ').lower() in ['n', 'no']):
            exit()
        

if __name__ == "__main__":
    main()