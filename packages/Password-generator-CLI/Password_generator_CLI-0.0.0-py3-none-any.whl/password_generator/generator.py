import random
import string

def generate_password(min_length, numbers = True, special_characters = True):
    digits = string.digits
    letters = string.ascii_letters
    special_characters = string.punctuation

    password_characters = []
    characters = letters
    if numbers:
        characters += digits
        password_characters.append(random.choice(digits))
    if special_characters:
        characters += special_characters
        password_characters.append(random.choice(special_characters))

    while len(password_characters) < min_length:
        password_characters.append(random.choice(characters))

    random.shuffle(password_characters)     # reorganize the order of the password_characters item
    return ''.join(password_characters)