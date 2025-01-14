# speck_cipher/utils.py

def rol32(x, n):
    """Циклический сдвиг влево для 32-битного числа"""
    return ((x << n) & 0xFFFFFFFF) | (x >> (32 - n))

def ror32(x, n):
    """Циклический сдвиг вправо для 32-битного числа"""
    return (x >> n) | ((x << (32 - n)) & 0xFFFFFFFF)
