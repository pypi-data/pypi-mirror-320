# simon_crypto/__init__.py

__version__ = "0.2.1"
__author__ = "Azaliya"
__email__ = "azakhabi19@gmail.com"

from .simon import (
    simon_64_96_key_schedule,
    simon_64_96_encrypt,
    simon_64_96_decrypt,
    simon_64_128_key_schedule,
    simon_64_128_encrypt,
    simon_64_128_decrypt,
)
