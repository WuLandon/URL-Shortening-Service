BASE62_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def encode_base62(number):
    if not isinstance(number, int):
        raise TypeError("number must be an integer")

    if number < 0:
        raise ValueError("number must be non-negative")

    if number == 0:
        return BASE62_ALPHABET[0]

    encoded = []
    while number > 0:
        number, remainder = divmod(number, len(BASE62_ALPHABET))
        encoded.append(BASE62_ALPHABET[remainder])

    return "".join(reversed(encoded))
