import random
import pyperclip


def generate_password(
    num_letters: int = 6,
    num_numbers: int = 3,
    num_symbols: int = 3
) -> str:
    """
    Generate a random password with specified character counts.

    Args:
        num_letters: Number of letters in the password (default: 6)
        num_numbers: Number of numbers in the password (default: 3)
        num_symbols: Number of symbols in the password (default: 3)

    Returns:
        The generated password as a string
    """
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
               'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
               'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']

    password_letters = [random.choice(letters) for _ in range(num_letters)]
    password_symbols = [random.choice(symbols) for _ in range(num_symbols)]
    password_numbers = [random.choice(numbers) for _ in range(num_numbers)]

    password_list = password_letters + password_numbers + password_symbols
    random.shuffle(password_list)

    return "".join(password_list)


def generate_and_copy_password(
    num_letters: int = 6,
    num_numbers: int = 3,
    num_symbols: int = 3
) -> str:
    """
    Generate a random password and copy it to clipboard.

    Args:
        num_letters: Number of letters in the password (default: 6)
        num_numbers: Number of numbers in the password (default: 3)
        num_symbols: Number of symbols in the password (default: 3)

    Returns:
        The generated password as a string
    """
    password = generate_password(num_letters, num_numbers, num_symbols)
    pyperclip.copy(password)
    return password
