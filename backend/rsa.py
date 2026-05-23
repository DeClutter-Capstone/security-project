"""
RSA implemented entirely from scratch for the IEA project.

No cryptography libraries, no PyCryptodome, no math shortcuts from libraries.
Only Python's built-in `random` and `math` modules are used.

Keys: public_key = (e, n), private_key = (d, n)
Each prime is 256 bits, so the modulus n is ~512 bits.
"""

import random


def is_prime(n, k=5):
    """Miller-Rabin probabilistic primality test with k rounds."""
    if n < 2:
        return False
    # Quick check against the first few small primes.
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p

    # Write n - 1 as 2^r * d with d odd.
    r = 0
    d = n - 1
    while d % 2 == 0:
        d //= 2
        r += 1

    # Witness loop.
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def generate_prime(bits=256):
    """Generate a random prime of the given bit length using is_prime."""
    while True:
        # Force the top bit (full bit length) and the low bit (odd).
        candidate = random.getrandbits(bits) | (1 << (bits - 1)) | 1
        if is_prime(candidate):
            return candidate


def _extended_gcd(a, b):
    """Return (g, x, y) such that a*x + b*y = g = gcd(a, b)."""
    if a == 0:
        return b, 0, 1
    g, x1, y1 = _extended_gcd(b % a, a)
    return g, y1 - (b // a) * x1, x1


def _modinv(a, m):
    """Modular inverse of a mod m via the extended Euclidean algorithm."""
    g, x, _ = _extended_gcd(a % m, m)
    if g != 1:
        raise ValueError("modular inverse does not exist")
    return x % m


def generate_keypair():
    """Generate an RSA keypair. Returns ((e, n), (d, n))."""
    p = generate_prime(256)
    q = generate_prime(256)
    while q == p:
        q = generate_prime(256)

    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537
    # In the extremely unlikely event e shares a factor with phi, regenerate.
    if phi % e == 0:
        return generate_keypair()
    d = _modinv(e, phi)
    return (e, n), (d, n)


def _int_to_bytes(value, length=None):
    """Serialize an int to big-endian bytes (minimum length 1)."""
    if length is None:
        length = max(1, (value.bit_length() + 7) // 8)
    return value.to_bytes(length, "big")


def rsa_encrypt(data, public_key):
    """Encrypt raw bytes (smaller than n) with the public key."""
    e, n = public_key
    m = int.from_bytes(data, "big")
    if m >= n:
        raise ValueError("data too large for modulus")
    c = pow(m, e, n)
    # Fixed width based on n so ciphertext length is predictable.
    return _int_to_bytes(c, (n.bit_length() + 7) // 8)


def rsa_decrypt(data, private_key):
    """Decrypt raw bytes with the private key, stripping leading zero padding."""
    d, n = private_key
    c = int.from_bytes(data, "big")
    m = pow(c, d, n)
    return _int_to_bytes(m)  # leading zero bytes are naturally dropped


def rsa_sign(data, private_key):
    """Sign data by encrypting it with the private key: pow(m, d, n)."""
    d, n = private_key
    m = int.from_bytes(data, "big")
    s = pow(m, d, n)
    return _int_to_bytes(s, (n.bit_length() + 7) // 8)


def rsa_verify(data, signature, public_key):
    """Verify a signature: decrypt with public key, compare to original data."""
    e, n = public_key
    s = int.from_bytes(signature, "big")
    recovered = pow(s, e, n)
    return recovered == int.from_bytes(data, "big")


def key_to_hex(key):
    """Serialize (e_or_d, n) as 'hex_e_or_d:hex_n'."""
    a, n = key
    return f"{a:x}:{n:x}"


def hex_to_key(hex_str):
    """Deserialize 'hex_e_or_d:hex_n' back to (int, int)."""
    a_hex, n_hex = hex_str.split(":")
    return int(a_hex, 16), int(n_hex, 16)


if __name__ == "__main__":
    import secrets

    pub, priv = generate_keypair()
    print("n bits:", priv[1].bit_length())

    des_key = secrets.token_bytes(8)
    enc = rsa_encrypt(des_key, pub)
    dec = rsa_decrypt(enc, priv).rjust(8, b"\x00")
    print("encrypt/decrypt ok:", dec == des_key)

    sig = rsa_sign(des_key, priv)
    print("verify ok:", rsa_verify(des_key, sig, pub))
    print("verify tampered:", rsa_verify(b"xxxxxxxx", sig, pub))

    hx = key_to_hex(pub)
    print("hex roundtrip ok:", hex_to_key(hx) == pub)
