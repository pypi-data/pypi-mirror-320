# speck_cipher/cipher.py

from .utils import rol32, ror32

SPECK_BLOCK_SIZE = 64
SPECK_WORD_SIZE = 32
SPECK_A = 8
SPECK_B = 3
SPECK_KEY_WORDS_96 = 3
SPECK_ROUNDS_96 = 26
SPECK_KEY_WORDS_128 = 4
SPECK_ROUNDS_128 = 27


class SpeckCipher:
    def __init__(self, key):
        if len(key) not in [12, 16]:
            raise ValueError("Key must be either 96-bit (12 bytes) or 128-bit (16 bytes)")
        self.key = key
        self.round_keys = self._generate_round_keys(key)

    def _generate_round_keys(self, key):
        """Генерация ключей для раундов"""
        if len(key) == 12:  # 96-bit key
            return self._speck_64_96_key_schedule(key)
        elif len(key) == 16:  # 128-bit key
            return self._speck_64_128_key_schedule(key)

    def _speck_64_96_key_schedule(self, input_key):
        """Генерация раундовых ключей для Speck 64/96"""
        keys = [0] * SPECK_ROUNDS_96
        l = [0] * (SPECK_ROUNDS_96 + SPECK_KEY_WORDS_96 - 2)

        rk = keys
        ik = list(input_key)

        # Инициализация
        rk[0] = ik[0]
        l[0] = ik[1]
        l[1] = ik[2]

        # Генерация ключей
        for i in range(SPECK_ROUNDS_96 - 1):
            l[i + SPECK_KEY_WORDS_96 - 1] = (rk[i] + ror32(l[i], SPECK_A)) ^ i
            rk[i + 1] = rol32(rk[i], SPECK_B) ^ l[i + SPECK_KEY_WORDS_96 - 1]

        return keys

    def _speck_64_128_key_schedule(self, input_key):
        """Генерация раундовых ключей для Speck 64/128"""
        keys = [0] * SPECK_ROUNDS_128
        l = [0] * (SPECK_ROUNDS_128 + SPECK_KEY_WORDS_128 - 2)

        rk = keys
        ik = list(input_key)

        # Инициализация
        rk[0] = ik[0]
        l[0] = ik[1]
        l[1] = ik[2]
        l[2] = ik[3]

        # Генерация ключей
        for i in range(SPECK_ROUNDS_128 - 1):
            l[i + SPECK_KEY_WORDS_128 - 1] = (rk[i] + ror32(l[i], SPECK_A)) ^ i
            rk[i + 1] = rol32(rk[i], SPECK_B) ^ l[i + SPECK_KEY_WORDS_128 - 1]

        return keys

    def encrypt(self, plaintext):
        """Шифрование одного блока текста"""
        if len(plaintext) != 8:
            raise ValueError("Plaintext must be a 8-byte block")

        # Преобразуем plaintext в список 32-битных чисел
        block = list(plaintext)
        x, y = (block[0] << 24) | (block[1] << 16) | (block[2] << 8) | block[3], \
               (block[4] << 24) | (block[5] << 16) | (block[6] << 8) | block[7]

        # Шифрование
        for i in range(len(self.round_keys)):
            x = ror32(x, SPECK_A)
            x += y
            x ^= self.round_keys[i]
            y = rol32(y, SPECK_B)
            y ^= x

        ciphertext = bytes([(x >> (8 * i)) & 0xFF for i in range(4)] +
                           [(y >> (8 * i)) & 0xFF for i in range(4)])

        return ciphertext

    def decrypt(self, ciphertext):
        """Расшифровка одного блока текста"""
        if len(ciphertext) != 8:
            raise ValueError("Ciphertext must be a 8-byte block")

        # Преобразуем ciphertext в список 32-битных чисел
        block = list(ciphertext)
        x, y = (block[0] << 24) | (block[1] << 16) | (block[2] << 8) | block[3], \
               (block[4] << 24) | (block[5] << 16) | (block[6] << 8) | block[7]

        # Расшифровка
        for i in range(len(self.round_keys) - 1, -1, -1):
            y ^= x
            y = ror32(y, SPECK_B)
            x ^= self.round_keys[i]
            x -= y
            x = rol32(x, SPECK_A)

        decrypted = bytes([(x >> (8 * i)) & 0xFF for i in range(4)] +
                          [(y >> (8 * i)) & 0xFF for i in range(4)])

        return decrypted
