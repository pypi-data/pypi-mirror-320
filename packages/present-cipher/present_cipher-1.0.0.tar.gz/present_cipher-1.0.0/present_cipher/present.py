# PRESENT_64_80 in Python

PRESENT_BLOCK_SIZE = 64
PRESENT_KEY_SIZE_80 = 80
PRESENT_KEY_SIZE_128 = 128
PRESENT_ROUNDS = 31

sbox = [0xc, 0x5, 0x6, 0xb, 0x9, 0x0, 0xa, 0xd, 0x3, 0xe, 0xf, 0x8, 0x4, 0x7, 0x1, 0x2]
invsbox = [0x5, 0xe, 0xf, 0x8, 0xc, 0x1, 0x2, 0xd, 0xb, 0x4, 0x6, 0x3, 0x0, 0x7, 0x9, 0xa]


def ror64(value, n):
    """Rotate value right by n bits."""
    return ((value >> n) | (value << (64 - n))) & 0xFFFFFFFFFFFFFFFF


def present_64_80_key_schedule(key):
    keylow = int.from_bytes(key[:8], 'little')
    highBytes = int.from_bytes(key[8:], 'little')
    keyhigh = (highBytes << 48) | (keylow >> 16)
    round_keys = [0] * (PRESENT_ROUNDS + 1)
    round_keys[0] = keyhigh

    for i in range(PRESENT_ROUNDS):
        # 61-bit left shift
        temp = keyhigh
        keyhigh = (keyhigh << 61) | (keylow >> 3)
        keylow = (temp >> 3) & 0xFFFF

        # S-Box application
        keyhigh &= 0x0FFFFFFFFFFFFFFF
        keyhigh |= sbox[keyhigh >> 60] << 60

        # round counter addition
        keylow ^= (((i + 1) & 0x01) << 15)
        keyhigh ^= ((i + 1) >> 1)

        round_keys[i + 1] = keyhigh

    return round_keys


def present_64_128_key_schedule(key):
    keylow = int.from_bytes(key[:8], 'little')
    keyhigh = int.from_bytes(key[8:], 'little')
    round_keys = [0] * (PRESENT_ROUNDS + 1)
    round_keys[0] = keyhigh

    for i in range(PRESENT_ROUNDS):
        # 61-bit left shift
        temp = (keyhigh << 61) | (keylow >> 3)
        keylow = (keylow << 61) | (keyhigh >> 3)
        keyhigh = temp

        # S-Box application
        temp = (sbox[keyhigh >> 60] << 4) ^ sbox[(keyhigh >> 56) & 0xf]
        keyhigh &= 0x00FFFFFFFFFFFFFF
        keyhigh |= temp << 56

        # round counter addition
        temp = ((keyhigh << 2) | (keylow >> 62)) ^ (i + 1)
        keyhigh = (keyhigh & 0xFFFFFFFFFFFFFFF8) ^ (temp & 0x7)
        keylow = (keylow & 0x3FFFFFFFFFFFFFFF) ^ (temp << 62)

        round_keys[i + 1] = keyhigh

    return round_keys


def present_encrypt(plain_text, round_keys):
    state = int.from_bytes(plain_text, 'little')
    result = 0
    for i in range(PRESENT_ROUNDS):
        state ^= round_keys[i]

        # S-box
        for _ in range(PRESENT_BLOCK_SIZE // 4):
            s_input = state & 0xF
            state &= 0xFFFFFFFFFFFFFFF0
            state |= sbox[s_input]
            state = ror64(state, 4)

        # P-layer
        result = 0
        for k in range(PRESENT_BLOCK_SIZE):
            state_bit = state & 0x1
            state >>= 1
            p_layer_index = (16 * k) % 63 if k != 63 else 63
            result |= state_bit << p_layer_index

        state = result

    state ^= round_keys[PRESENT_ROUNDS]
    return state.to_bytes(8, 'little')


def present_decrypt(cipher_text, round_keys):
    state = int.from_bytes(cipher_text, 'little')
    result = 0
    for i in range(PRESENT_ROUNDS, 0, -1):
        state ^= round_keys[i]

        # P-layer
        result = 0
        for k in range(PRESENT_BLOCK_SIZE):
            state_bit = state & 0x1
            state >>= 1
            p_layer_index = (4 * k) % 63 if k != 63 else 63
            result |= state_bit << p_layer_index

        state = result

        # S-box
        for _ in range(PRESENT_BLOCK_SIZE // 4):
            s_input = state & 0xF
            state &= 0xFFFFFFFFFFFFFFF0
            state |= invsbox[s_input]
            state = ror64(state, 4)

    state ^= round_keys[0]
    return state.to_bytes(8, 'little')
