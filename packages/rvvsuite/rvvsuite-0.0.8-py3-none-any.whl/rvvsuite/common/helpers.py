from random import random, randint, choice, choices
import re


def ask_user(prompt: str):
    res = input(f'{prompt} [Y/n] ').strip().lower()
    if res in ['y', 'yes', '']:
        return True
    elif res in ['n', 'no']:
        return False
    else:
        print('Invalid option.')
        return ask_user(prompt)
    

def repeated_random(min, max, used_set: set, repeat_rate):
    r = random()
    if r <= repeat_rate and len(used_set) > 0:
        return choice(list(used_set))
    else:
        return randint(min, max)
    
    
def random_imm(width, data_variant_weights): # TODO: Test sign of result
    if width == 8:
        variant = choices(['zero', 'neg', 'pos'], data_variant_weights[:-1])[0]
        if variant == 'zero':
            return 0, False
        elif variant == 'neg':
            return 2 ** 7 + randint(0, 2 ** 7 - 1), False
        else:
            return randint(0, 2 ** 7 - 1), False
    
    elif width == 16:
        variant = choices(['zero', 'neg', 'pos', 'big_num'], data_variant_weights)[0]
        if variant == 'zero':
            return 0, False
        elif variant == 'neg':
            return 2 ** 11 + randint(0, 2 ** 11 - 1), True
        elif variant == 'pos':
            return randint(0, 2 ** 11 - 1), False
        else:
            return randint(2 ** 12, 2 ** 16 - 1), True

    elif width == 32:
        variant = choices(['zero', 'neg', 'pos', 'big_num'], data_variant_weights)[0]
        if variant == 'zero':
            return 0, False
        elif variant == 'neg':
            return 2 ** 11 + randint(0, 2 ** 11 - 1), True
        elif variant == 'pos':
            return randint(0, 2 ** 11 - 1), False
        else:
            return randint(2 ** 12, 2 ** 32 - 1), True

    else:
        pass
        # TODO: Raise error here


def split_imm(imm):
    hi20b = imm // (2 ** 12)
    lo12b = imm % (2 ** 12)
    if lo12b >= 2 ** 11:
        hi20b += 1

    return hi20b, lo12b


def sign_mag_2_two_comp(value, width):
    if value > 0:
        two_comp = value
    else:
        two_comp = (~abs(value) | (1 << (width - 1))) + 1

    return two_comp % (2 ** width)


def code_number(number_as_str: str, width):
    '''
    Convert number as string into int coded (two-comp) binary.
    Return a non-negative int
    '''
    number_match = re.match(r'(?P<bin>0b[01]+)|(?P<hex>0x[0-9a-fA-F]+)|(?P<dec>-?\d+)', number_as_str)

    if not number_match:
        return -1 # Error code

    if number_match.group('bin'):
        return int(number_match.group('bin'), 2)
    elif number_match.group('hex'):
        return int(number_match.group('hex'), 16)
    elif number_match.group('dec'):
        return sign_mag_2_two_comp(int(number_match.group('dec')), width)


def print_error_and_exit(line_number, statement, error_descs):
    print(f'SyntaxError at {line_number}: {statement}')
    for desc in error_descs:
        print(desc)
    exit(1)