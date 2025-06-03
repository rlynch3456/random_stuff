import argparse
import random
import string

def generate_password(length=12, use_uppercase=True, use_digits=True, use_symbols=True):
    characters = string.ascii_lowercase
    if use_uppercase:
        characters += string.ascii_uppercase
    if use_digits:
        characters += string.digits
    if use_symbols:
        characters += string.punctuation
    
    if not characters:
       return "Please select at least one character type."
    
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--length', default = 12, help='Length of password')
    parser.add_argument('-u', '--upper', help='Include upper case', action='store_true', default = False)
    parser.add_argument('-d', '--digits', help='Include digits', action='store_true', default = False)
    parser.add_argument('-s', '--special', help='Include special characters', action='store_true', default = False)

    args = parser.parse_args()
    password_length = int(getattr(args, 'length'))

    if password_length < 1:
        print(f'{password_length} is too short')
    elif password_length > 64:
        print(f'{password_length} seems a bit excessive don\'t you think?')
    else:
        use_uppercase = getattr(args,'upper')
        use_digits = getattr(args,'digits')
        use_symbols = getattr(args,'special')

        password = generate_password(password_length, use_uppercase, use_digits, use_symbols)
        print("Generated password:", password)
