import argparse
from password_generator.generator import generate_password

def main():
    parser = argparse.ArgumentParser(description = 'Generate a secure, random password.')

    parser.add_argument('min_length', type = int, help = 'The minimum length of the password.')
    parser.add_argument('-n', '--numbers', action = 'store_true', help = 'Include numbers in the password.')
    parser.add_argument('-s', '--special', action = 'store_true', help = 'Include special character in the password.')

    args = parser.parse_args()

    password = generate_password(min_length = args.min_length, numbers = args.numbers, special_characters = args.special)

    print('Generated password: ', password)