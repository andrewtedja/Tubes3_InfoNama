import random
import os
from math import gcd
from dotenv import load_dotenv

load_dotenv()
PUBLIC_N = int(os.getenv("PUBLIC_N"))
PUBLIC_E = int(os.getenv("PUBLIC_E"))
PRIVATE_N = int(os.getenv("PRIVATE_N"))
PRIVATE_D = int(os.getenv("PRIVATE_D"))


def rsa_encrypt(plaintext: str) -> str:
    """
    Encrypt plaintext string using RSA public key from .env
    Returns space-separated string of encrypted integers
    """
    return ' '.join(str(pow(ord(char), PUBLIC_E, PUBLIC_N)) for char in plaintext)

def rsa_decrypt(ciphertext: str) -> str:
    """
    Decrypt space-separated string of encrypted integers using RSA private key from .env
    Returns original plaintext string
    """
    return ''.join(chr(pow(int(chunk), PRIVATE_D, PRIVATE_N)) for chunk in ciphertext.split())

def is_prime(n, k=5):
    """Miller-Rabin primality test (probabilistic)"""
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0:
        return False

    r, d = 0, n - 1
    while d % 2 == 0:
        d //= 2
        r += 1

    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for __ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_prime(bits):
    """Generate a prime number of given bit length"""
    while True:
        p = random.getrandbits(bits)
        p |= (1 << bits - 1) | 1
        if is_prime(p):
            return p

def generate_keypair(bits=512):
    """Generate RSA public and private keypair, print as .env entries"""
    p = generate_prime(bits)
    q = generate_prime(bits)
    while p == q:
        q = generate_prime(bits)

    n = p * q
    phi = (p - 1) * (q - 1)

    e = 65537
    if gcd(e, phi) != 1:
        e = 3
        while gcd(e, phi) != 1:
            e += 2

    d = pow(e, -1, phi)

    print("=== COPY THE FOLLOWING INTO YOUR .env FILE ===\n")
    print(f"PUBLIC_N={n}")
    print(f"PUBLIC_E={e}")
    print()
    print(f"PRIVATE_N={n}")
    print(f"PRIVATE_D={d}")
    print("\n==============================================")

if __name__ == "__main__":
    generate_keypair()
