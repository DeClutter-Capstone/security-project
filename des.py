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

# Functions to switch bits to different types

def text_to_bin(text):
    """Convert ASCII text to binary string"""
    return ''.join(format(ord(c), '08b') for c in text)

def bin_to_text(binary):
    """Convert binary string back to ASCII text"""
    return ''.join(chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8))

def hex_to_bin(hex_str):
    return bin(int(hex_str, 16))[2:].zfill(len(hex_str) * 4)

def bin_to_hex(binary):
    return hex(int(binary, 2))[2:].zfill(len(binary) // 4)

def permute(bits, table):
    """Apply a permutation table to a bit string"""
    return ''.join(bits[t - 1] for t in table)

def xor(a, b):
    """XOR two equal-length bit strings"""
    return ''.join('0' if x == y else '1' for x, y in zip(a, b))

def left_shift(bits, n):
    """Left circular shift"""
    return bits[n:] + bits[:n]

# Round key generation

def generate_round_keys(key_64bit):
    """
    Generate 16 round keys from a 64-bit key string.
    2.4.1 PC-1, 2.4.2 left shifts, 2.4.3 PC-2
    """
    # Take key from 64 to 56 bits here
    key_56 = permute(key_64bit, PC1)
    C, D = key_56[:28], key_56[28:]

    round_keys = []
    for i in range(16):
        C = left_shift(C, SHIFT_SCHEDULE[i])
        D = left_shift(D, SHIFT_SCHEDULE[i])
        CD = C + D
        # PC2 takes round keys from 56 to 48 bits
        round_keys.append(permute(CD, PC2))

    return round_keys

# Mangler function F and S box

def s_box_substitution(bits_48):
    """Apply all 8 S-boxes to 48-bit input -> 32-bit output"""
    output = ''
    for i in range(8):
        chunk = bits_48[i*6:(i+1)*6]
        row = int(chunk[0] + chunk[5], 2)
        col = int(chunk[1:5], 2)
        val = S_BOXES[i][row][col]
        output += format(val, '04b')
    return output

def f_function(R, K):
    """DES F function: expand R, XOR with key, S-boxes, permute P"""
    expanded = permute(R, E)          # Expansion
    xored = xor(expanded, K)          # XOR with round key
    substituted = s_box_substitution(xored)  # S-boxes
    return permute(substituted, P)    # Permutation P

# Main DES function 

def des_encrypt_block(plaintext_64bit, key_64bit):
    """Encrypt a single 64-bit block"""
    round_keys = generate_round_keys(key_64bit)

    #  Initial Permutation
    permuted = permute(plaintext_64bit, IP)
    L, R = permuted[:32], permuted[32:]

    for i in range(16):
        f_out = f_function(R, round_keys[i])
        new_R = xor(L, f_out)          #  XOR with left half
        L = R                           #  Swap halves
        R = new_R

    # Final swap then IP_INV
    combined = R + L
    #  Inverse Initial Permutation
    return permute(combined, IP_INV)

def des_decrypt_block(ciphertext_64bit, key_64bit):
    """Decrypt a single 64-bit block (same as encrypt but reversed round keys)"""
    round_keys = generate_round_keys(key_64bit)
    round_keys.reverse()

    permuted = permute(ciphertext_64bit, IP)
    L, R = permuted[:32], permuted[32:]

    for i in range(16):
        f_out = f_function(R, round_keys[i])
        new_R = xor(L, f_out)
        L = R
        R = new_R

    combined = R + L
    return permute(combined, IP_INV)

# Padding to keep a length multiple of 8

def pad(text):
    """ padding to make length multiple of 8 bytes"""
    pad_len = 8 - (len(text) % 8)
    return text + chr(pad_len) * pad_len

def unpad(text):
    """Remove padding"""
    pad_len = ord(text[-1])
    return text[:-pad_len]

# Functions to encrypt and decrypt a message

def encrypt_message(message, key_text):
    """
    Encrypt a plaintext string with an 8-character key.
    Returns hex string.
    """
    key_bin = text_to_bin(key_text[:8].ljust(8))
    padded = pad(message)
    ciphertext_bin = ''
    for i in range(0, len(padded), 8):
        block = text_to_bin(padded[i:i+8])
        ciphertext_bin += des_encrypt_block(block, key_bin)
    return bin_to_hex(ciphertext_bin)

def decrypt_message(encrypted_hex, key_text):
    """
    Decrypt a hex string with an 8-character key.
    Returns plaintext string.
    """
    key_bin = text_to_bin(key_text[:8].ljust(8))
    ciphertext_bin = hex_to_bin(encrypted_hex).zfill(
        len(encrypted_hex) * 4
    )
    plaintext = ''
    for i in range(0, len(ciphertext_bin), 64):
        block = ciphertext_bin[i:i+64]
        plaintext += bin_to_text(des_decrypt_block(block, key_bin))
    return unpad(plaintext)

# testing all transformations used

def run_tests():
    key_text = "12345678"
    plaintext = "Hello123"
    key_bin = text_to_bin(key_text)
    plain_bin = text_to_bin(plaintext)

    print(f"Key: {key_text}  |  Plaintext: {plaintext}\n")

    ip_out = permute(plain_bin, IP)
    print(f"[2.1] IP:         {ip_out[:32]}...")

    ip_inv_out = permute(ip_out, IP_INV)
    print(f"[2.2] IP Inverse: Match = {ip_inv_out == plain_bin}")

    R0 = ip_out[32:]
    expanded = permute(R0, E)
    print(f"[2.3] Expansion:  {expanded[:32]}...")

    round_keys = generate_round_keys(key_bin)
    print(f"[2.4] Round Key1: {round_keys[0]}")

    xor_out = xor(expanded, round_keys[0])
    print(f"[2.5] XOR:        {xor_out[:32]}...")

    sbox_out = s_box_substitution(xor_out)
    print(f"[2.6] S-Boxes:    {sbox_out}")

    p_out = permute(sbox_out, P)
    print(f"[2.7] Perm P:     {p_out}")

    L0 = ip_out[:32]
    xor_left = xor(L0, p_out)
    print(f"[2.8] XOR Left:   {xor_left}")

    print(f"[2.9] Swap:       new L = R0, new R = XOR result")

    encrypted = encrypt_message(plaintext, key_text)
    decrypted = decrypt_message(encrypted, key_text)
    print(f"\n[2.10] Encrypted: {encrypted}")
    print(f"[2.11] Decrypted: {decrypted}  |  Match = {decrypted == plaintext}")

if __name__ == "__main__":
    run_tests()