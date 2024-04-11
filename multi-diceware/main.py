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
    print('Password length')
    if (password_length := int(input('>>> '))) < 1:
        exit()

    print(
        """
Choose your lists
0. Normal lists
1. EFF short 1
2. EFF short 2"""
    )
    list_choice = int(input('>>> '))

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
    num_position = randbelow(password_length) + 1
    num_value = randbelow(num_max)
    title_position = randbelow(password_length) + 1

    if src_names:
        print()
        for src_name in src_names:
            print(src_name, end='\t')

    print('\n')

    for dice in dices:
        dice_dict: dict = worddict[dice]

        for word in dice_dict.values():
            end_line = ''
            if len(dice_dict) > 1:
                end_line = ' '*(16 - len(word))

            print(word, end=end_line)
        print()

    print(f'\n{num_position = }')
    print(f'{num_value = }')
    print(f'{title_position = }\n')


if __name__ == "__main__":
    main()