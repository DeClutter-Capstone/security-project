# DES implemented with integer-based bitwise operations (fast path).
#
# The algorithm is identical to a textbook DES; only the internal
# representation changed from '0'/'1' character strings to Python integers.


# Tables for substitutions

IP = [
    58,50,42,34,26,18,10,2,
    60,52,44,36,28,20,12,4,
    62,54,46,38,30,22,14,6,
    64,56,48,40,32,24,16,8,
    57,49,41,33,25,17, 9,1,
    59,51,43,35,27,19,11,3,
    61,53,45,37,29,21,13,5,
    63,55,47,39,31,23,15,7
]

IP_INV = [
    40,8,48,16,56,24,64,32,
    39,7,47,15,55,23,63,31,
    38,6,46,14,54,22,62,30,
    37,5,45,13,53,21,61,29,
    36,4,44,12,52,20,60,28,
    35,3,43,11,51,19,59,27,
    34,2,42,10,50,18,58,26,
    33,1,41, 9,49,17,57,25
]

E = [
    32, 1, 2, 3, 4, 5,
     4, 5, 6, 7, 8, 9,
     8, 9,10,11,12,13,
    12,13,14,15,16,17,
    16,17,18,19,20,21,
    20,21,22,23,24,25,
    24,25,26,27,28,29,
    28,29,30,31,32, 1
]

P = [
    16, 7,20,21,29,12,28,17,
     1,15,23,26, 5,18,31,10,
     2, 8,24,14,32,27, 3, 9,
    19,13,30, 6,22,11, 4,25
]

PC1 = [
    57,49,41,33,25,17, 9,
     1,58,50,42,34,26,18,
    10, 2,59,51,43,35,27,
    19,11, 3,60,52,44,36,
    63,55,47,39,31,23,15,
     7,62,54,46,38,30,22,
    14, 6,61,53,45,37,29,
    21,13, 5,28,20,12, 4
]

PC2 = [
    14,17,11,24, 1, 5,
     3,28,15, 6,21,10,
    23,19,12, 4,26, 8,
    16, 7,27,20,13, 2,
    41,52,31,37,47,55,
    30,40,51,45,33,48,
    44,49,39,56,34,53,
    46,42,50,36,29,32
]

SHIFT_SCHEDULE = [1,1,2,2,2,2,2,2,1,2,2,2,2,2,2,1]

S_BOXES = [
    # S1
    [[14,4,13,1,2,15,11,8,3,10,6,12,5,9,0,7],
     [0,15,7,4,14,2,13,1,10,6,12,11,9,5,3,8],
     [4,1,14,8,13,6,2,11,15,12,9,7,3,10,5,0],
     [15,12,8,2,4,9,1,7,5,11,3,14,10,0,6,13]],
    # S2
    [[15,1,8,14,6,11,3,4,9,7,2,13,12,0,5,10],
     [3,13,4,7,15,2,8,14,12,0,1,10,6,9,11,5],
     [0,14,7,11,10,4,13,1,5,8,12,6,9,3,2,15],
     [13,8,10,1,3,15,4,2,11,6,7,12,0,5,14,9]],
    # S3
    [[10,0,9,14,6,3,15,5,1,13,12,7,11,4,2,8],
     [13,7,0,9,3,4,6,10,2,8,5,14,12,11,15,1],
     [13,6,4,9,8,15,3,0,11,1,2,12,5,10,14,7],
     [1,10,13,0,6,9,8,7,4,15,14,3,11,5,2,12]],
    # S4
    [[7,13,14,3,0,6,9,10,1,2,8,5,11,12,4,15],
     [13,8,11,5,6,15,0,3,4,7,2,12,1,10,14,9],
     [10,6,9,0,12,11,7,13,15,1,3,14,5,2,8,4],
     [3,15,0,6,10,1,13,8,9,4,5,11,12,7,2,14]],
    # S5
    [[2,12,4,1,7,10,11,6,8,5,3,15,13,0,14,9],
     [14,11,2,12,4,7,13,1,5,0,15,10,3,9,8,6],
     [4,2,1,11,10,13,7,8,15,9,12,5,6,3,0,14],
     [11,8,12,7,1,14,2,13,6,15,0,9,10,4,5,3]],
    # S6
    [[12,1,10,15,9,2,6,8,0,13,3,4,14,7,5,11],
     [10,15,4,2,7,12,9,5,6,1,13,14,0,11,3,8],
     [9,14,15,5,2,8,12,3,7,0,4,10,1,13,11,6],
     [4,3,2,12,9,5,15,10,11,14,1,7,6,0,8,13]],
    # S7
    [[4,11,2,14,15,0,8,13,3,12,9,7,5,10,6,1],
     [13,0,11,7,4,9,1,10,14,3,5,12,2,15,8,6],
     [1,4,11,13,12,3,7,14,10,15,6,8,0,5,9,2],
     [6,11,13,8,1,4,10,7,9,5,0,15,14,2,3,12]],
    # S8
    [[13,2,8,4,6,15,11,1,10,9,3,14,5,0,12,7],
     [1,15,13,8,10,3,7,4,12,5,6,11,0,14,9,2],
     [7,11,4,1,9,12,14,2,0,6,10,13,15,3,5,8],
     [2,1,14,7,4,10,8,13,15,12,9,0,3,5,6,11]]
]

# --------------------------------------------------------------------------- #
# Integer bit primitives
# --------------------------------------------------------------------------- #

def permute(value, in_bits, table):
    """Permute an integer of `in_bits` bits according to `table`.

    DES bit numbering is 1-based from the most significant bit, matching the
    original string version `''.join(bits[t-1] for t in table)`.  This is the
    general (per-bit) version, used only for the rare paths (key schedule and
    the self-test).  The hot path uses precomputed byte-lookup tables below.
    """
    out = 0
    for pos in table:
        out = (out << 1) | ((value >> (in_bits - pos)) & 1)
    return out


def _rotl28(value, n):
    """Left circular shift of a 28-bit value."""
    return ((value << n) | (value >> (28 - n))) & 0x0FFFFFFF


# --------------------------------------------------------------------------- #
# Precomputed lookup tables for the hot path
# --------------------------------------------------------------------------- #
# A permutation from `in_bits` (multiple of 8) to len(table) bits is computed
# as a sum of per-input-byte lookups: 8 lookups instead of 64 bit operations.

def _build_perm_tables(table, in_bits):
    out_bits = len(table)
    n_bytes = in_bits // 8
    tabs = [[0] * 256 for _ in range(n_bytes)]
    for out_idx, src in enumerate(table):     # out_idx 0 -> MSB of output
        src0 = src - 1                         # 0-indexed from MSB of input
        byte_i, bit_in_byte = divmod(src0, 8)
        out_shift = out_bits - 1 - out_idx     # output position from LSB
        for b in range(256):
            if (b >> (7 - bit_in_byte)) & 1:
                tabs[byte_i][b] |= (1 << out_shift)
    return tabs


_IP_T = _build_perm_tables(IP, 64)
_IPINV_T = _build_perm_tables(IP_INV, 64)
_E_T = _build_perm_tables(E, 32)


def _permute64(value, tabs):
    return (
        tabs[0][(value >> 56) & 0xFF]
        | tabs[1][(value >> 48) & 0xFF]
        | tabs[2][(value >> 40) & 0xFF]
        | tabs[3][(value >> 32) & 0xFF]
        | tabs[4][(value >> 24) & 0xFF]
        | tabs[5][(value >> 16) & 0xFF]
        | tabs[6][(value >> 8) & 0xFF]
        | tabs[7][value & 0xFF]
    )


def _expand(value, tabs):  # 32 -> 48
    return (
        tabs[0][(value >> 24) & 0xFF]
        | tabs[1][(value >> 16) & 0xFF]
        | tabs[2][(value >> 8) & 0xFF]
        | tabs[3][value & 0xFF]
    )


# Combined S-box + P permutation: for each S-box i and 6-bit input, the final
# 32-bit contribution after the P permutation. Collapses S-boxes and P into one
# lookup per S-box.
def _build_sp_tables():
    sp = [[0] * 64 for _ in range(8)]
    for i in range(8):
        for inp in range(64):
            row = ((inp >> 5) & 1) << 1 | (inp & 1)
            col = (inp >> 1) & 0x0F
            val = S_BOXES[i][row][col]              # 4-bit S-box output
            pre_p = val << (28 - 4 * i)             # placed in 32-bit pre-P word
            sp[i][inp] = permute(pre_p, 32, P)      # apply P (one-time cost)
    return sp


_SP = _build_sp_tables()


# --------------------------------------------------------------------------- #
# Round key generation
# --------------------------------------------------------------------------- #

def generate_round_keys(key_64):
    """Generate the 16 round keys (ints) from a 64-bit integer key."""
    key_56 = permute(key_64, 64, PC1)        # 64 -> 56 bits
    C = (key_56 >> 28) & 0x0FFFFFFF
    D = key_56 & 0x0FFFFFFF

    round_keys = []
    for shift in SHIFT_SCHEDULE:
        C = _rotl28(C, shift)
        D = _rotl28(D, shift)
        CD = (C << 28) | D                   # 56 bits
        round_keys.append(permute(CD, 56, PC2))  # 56 -> 48 bits
    return round_keys


# --------------------------------------------------------------------------- #
# Mangler function F (with S-boxes)
# --------------------------------------------------------------------------- #

def s_box_substitution(bits_48):
    """Apply the 8 S-boxes to a 48-bit integer -> 32-bit integer.

    Kept for the self-test / demonstration; the hot path uses the combined
    S-box+P tables in f_function instead.
    """
    output = 0
    for i in range(8):
        chunk = (bits_48 >> (42 - 6 * i)) & 0x3F
        row = ((chunk >> 5) & 1) << 1 | (chunk & 1)
        col = (chunk >> 1) & 0x0F
        output = (output << 4) | S_BOXES[i][row][col]
    return output


def f_function(R, K):
    """DES F function on 32-bit integer R with 48-bit round key K (fast path)."""
    x = _expand(R, _E_T) ^ K                 # expand to 48 bits, XOR round key
    sp = _SP
    return (
        sp[0][(x >> 42) & 0x3F]
        | sp[1][(x >> 36) & 0x3F]
        | sp[2][(x >> 30) & 0x3F]
        | sp[3][(x >> 24) & 0x3F]
        | sp[4][(x >> 18) & 0x3F]
        | sp[5][(x >> 12) & 0x3F]
        | sp[6][(x >> 6) & 0x3F]
        | sp[7][x & 0x3F]
    )


# --------------------------------------------------------------------------- #
# Block encryption / decryption (64-bit integers)
# --------------------------------------------------------------------------- #

def _crypt_block(block_64, round_keys):
    """Run the 16-round Feistel network with the given (ordered) round keys."""
    p = _permute64(block_64, _IP_T)
    L = (p >> 32) & 0xFFFFFFFF
    R = p & 0xFFFFFFFF
    for K in round_keys:
        L, R = R, L ^ f_function(R, K)
    return _permute64((R << 32) | L, _IPINV_T)   # final swap + IP^-1


def des_encrypt_block(block_64, key_64):
    """Encrypt a single 64-bit integer block."""
    return _crypt_block(block_64, generate_round_keys(key_64))


def des_decrypt_block(block_64, key_64):
    """Decrypt a single 64-bit integer block (reversed round keys)."""
    return _crypt_block(block_64, generate_round_keys(key_64)[::-1])


# --------------------------------------------------------------------------- #
# Key / padding helpers
# --------------------------------------------------------------------------- #

def _key_to_int(key_text):
    """Turn an 8-char key string into a 64-bit integer (latin-1 bytes)."""
    key_bytes = key_text[:8].ljust(8).encode("latin-1")
    return int.from_bytes(key_bytes, "big")


def pad_bytes(data):
    """PKCS7 padding on bytes to make the length a multiple of 8."""
    pad_len = 8 - (len(data) % 8)
    return data + bytes([pad_len]) * pad_len


def unpad_bytes(data):
    """Remove PKCS7 padding from bytes."""
    pad_len = data[-1]
    return data[:-pad_len]


# --------------------------------------------------------------------------- #
# Public byte API (used by the application)
# --------------------------------------------------------------------------- #

def encrypt_bytes(data, key_text):
    """Encrypt raw bytes with an 8-character key. Returns encrypted bytes."""
    round_keys = generate_round_keys(_key_to_int(key_text))  # computed once
    padded = pad_bytes(data)
    frm = int.from_bytes
    out = bytearray()
    for i in range(0, len(padded), 8):
        block = frm(padded[i:i + 8], "big")
        out += _crypt_block(block, round_keys).to_bytes(8, "big")
    return bytes(out)


def decrypt_bytes(data, key_text):
    """Decrypt raw bytes with an 8-character key. Returns the original bytes."""
    round_keys = generate_round_keys(_key_to_int(key_text))[::-1]  # computed once
    frm = int.from_bytes
    out = bytearray()
    for i in range(0, len(data), 8):
        block = frm(data[i:i + 8], "big")
        out += _crypt_block(block, round_keys).to_bytes(8, "big")
    return unpad_bytes(bytes(out))


# --------------------------------------------------------------------------- #
# Public text API (kept for compatibility; built on the byte API)
# --------------------------------------------------------------------------- #

def encrypt_message(message, key_text):
    """Encrypt a plaintext string with an 8-character key. Returns hex."""
    return encrypt_bytes(message.encode("latin-1"), key_text).hex()


def decrypt_message(encrypted_hex, key_text):
    """Decrypt a hex string with an 8-character key. Returns plaintext."""
    return decrypt_bytes(bytes.fromhex(encrypted_hex), key_text).decode("latin-1")


# --------------------------------------------------------------------------- #
# Self-test / demonstration of each transformation
# --------------------------------------------------------------------------- #

def _bits(value, n):
    return format(value, "0{}b".format(n))


def run_tests():
    key_text = "12345678"
    plaintext = "Hello123"
    key_64 = _key_to_int(key_text)
    plain_64 = int.from_bytes(plaintext.encode("latin-1"), "big")

    print(f"Key: {key_text}  |  Plaintext: {plaintext}\n")

    ip_out = permute(plain_64, 64, IP)
    print(f"[2.1] IP:         {_bits(ip_out, 64)[:32]}...")

    ip_inv_out = permute(ip_out, 64, IP_INV)
    print(f"[2.2] IP Inverse: Match = {ip_inv_out == plain_64}")

    R0 = ip_out & 0xFFFFFFFF
    expanded = permute(R0, 32, E)
    print(f"[2.3] Expansion:  {_bits(expanded, 48)[:32]}...")

    round_keys = generate_round_keys(key_64)
    print(f"[2.4] Round Key1: {_bits(round_keys[0], 48)}")

    xor_out = expanded ^ round_keys[0]
    print(f"[2.5] XOR:        {_bits(xor_out, 48)[:32]}...")

    sbox_out = s_box_substitution(xor_out)
    print(f"[2.6] S-Boxes:    {_bits(sbox_out, 32)}")

    p_out = permute(sbox_out, 32, P)
    print(f"[2.7] Perm P:     {_bits(p_out, 32)}")

    L0 = (ip_out >> 32) & 0xFFFFFFFF
    xor_left = L0 ^ p_out
    print(f"[2.8] XOR Left:   {_bits(xor_left, 32)}")

    print(f"[2.9] Swap:       new L = R0, new R = XOR result")

    encrypted = encrypt_message(plaintext, key_text)
    decrypted = decrypt_message(encrypted, key_text)
    print(f"\n[2.10] Encrypted: {encrypted}")
    print(f"[2.11] Decrypted: {decrypted}  |  Match = {decrypted == plaintext}")


if __name__ == "__main__":
    run_tests()
