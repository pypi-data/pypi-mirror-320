# simon_crypto/simon.py

# Импортируем необходимые библиотеки
from typing import List

SIMON_CONST_C = 0xfffffffc
SIMON_KEY_WORDS_96 = 3
SIMON_ROUNDS_96 = 42
SIMON_KEY_WORDS_128 = 4
SIMON_ROUNDS_128 = 44

# Вспомогательные функции для сдвигов
def rol32(x: int, n: int) -> int:
    """Левый побитовый сдвиг на n бит."""
    return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF

def ror32(x: int, n: int) -> int:
    """Правый побитовый сдвиг на n бит."""
    return ((x >> n) | (x << (32 - n))) & 0xFFFFFFFF

# Функция f
def f(x: int) -> int:
    return (rol32(x, 1) & rol32(x, 8)) ^ rol32(x, 2)

# Генерация раундовых ключей для SIMON-64-96
def simon_64_96_key_schedule(input_key: List[int]) -> List[int]:
    keys = input_key[:]
    z2 = [
        1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0,
        1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1,
        1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1
    ]

    for i in range(SIMON_KEY_WORDS_96, SIMON_ROUNDS_96):
        temp = ror32(keys[i-1], 3)
        temp ^= ror32(temp, 1)
        keys.append(SIMON_CONST_C ^ keys[i-SIMON_KEY_WORDS_96] ^ temp)
        if z2[(i - SIMON_KEY_WORDS_96) % 62] == 1:
            keys[i] ^= 0x1
    return keys

# Генерация раундовых ключей для SIMON-64-128
def simon_64_128_key_schedule(input_key: List[int]) -> List[int]:
    keys = input_key[:]
    z3 = [
        1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1,
        1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1,
        0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1
    ]

    for i in range(SIMON_KEY_WORDS_128, SIMON_ROUNDS_128):
        temp = ror32(keys[i-1], 3)
        temp ^= keys[i-3]
        temp ^= ror32(temp, 1)
        keys.append(SIMON_CONST_C ^ keys[i-SIMON_KEY_WORDS_128] ^ temp)
        if z3[(i - SIMON_KEY_WORDS_128) % 62] == 1:
            keys[i] ^= 0x1
    return keys

# Шифрование для SIMON-64-96
def simon_64_96_encrypt(plain_text: List[int], keys: List[int]) -> List[int]:
    plain = plain_text[:]
    for i in range(0, SIMON_ROUNDS_96, 2):
        plain[0] ^= keys[i] ^ f(plain[1])
        plain[1] ^= keys[i+1] ^ f(plain[0])
    return plain

# Шифрование для SIMON-64-128
def simon_64_128_encrypt(plain_text: List[int], keys: List[int]) -> List[int]:
    plain = plain_text[:]
    for i in range(0, SIMON_ROUNDS_128, 2):
        plain[0] ^= keys[i] ^ f(plain[1])
        plain[1] ^= keys[i+1] ^ f(plain[0])
    return plain

# Дешифрование для SIMON-64-96
def simon_64_96_decrypt(cipher_text: List[int], keys: List[int]) -> List[int]:
    cipher = cipher_text[:]
    for i in range(SIMON_ROUNDS_96-1, -1, -2):
        cipher[1] ^= keys[i] ^ f(cipher[0])
        cipher[0] ^= keys[i-1] ^ f(cipher[1])
    return cipher

# Дешифрование для SIMON-64-128
def simon_64_128_decrypt(cipher_text: List[int], keys: List[int]) -> List[int]:
    cipher = cipher_text[:]
    for i in range(SIMON_ROUNDS_128-1, -1, -2):
        cipher[1] ^= keys[i] ^ f(cipher[0])
        cipher[0] ^= keys[i-1] ^ f(cipher[1])
    return cipher
