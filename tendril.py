"""TENDRIL-1 — an ORIGINAL break-me stream cipher. NOT SECURE. A learning toy.

Do NOT use this to protect anything real. It is a hand-made cipher published so
people can try to break it. For real, quantum-safe encryption use ML-KEM + AES.

The image: a climbing vine creeping over a ring of nodes, reaching sideways to
older growth, twisting by an amount set by a rolling wheel.

Design (Kerckhoffs: everything here is public; only the key is secret). It is an
ARX (add-rotate-xor) cipher, the same toolkit as ChaCha/BLAKE, but the engine is
original: an ARX *ring-walk* with a golden-angle pointer and cycloid-driven
rotations. It is not RC4 (swap-based) and not ChaCha (fixed matrix).

  State: 32 bytes S[0..31] on a ring (the vine).
  Movers: growth pointer p, cycloid phase theta.
  GOLD = 157 (odd, coprime to 256; ~0.613 of a turn, the golden-ratio conjugate).

  Per output byte:
    theta = (theta + GOLD) mod 256            # the wheel rolls
    p     = (p + 1 + (theta >> 6)) mod 32     # tendril creeps, stride 1..4
    b     = S[(p + 7)  mod 32]                # reach to older growth
    c     = S[(p + 19) mod 32]
    r     = 1 + (theta & 7)                   # twist amount 1..8
    m     = rotl8((S[p] + b) mod 256, r) XOR c XOR theta
    S[p]  = m                                 # grow the node
    out   = m XOR S[m mod 32]                 # nonlinear tap

  Encrypt = plaintext XOR keystream. Decrypt is identical.

WHERE IT WILL PROBABLY BREAK (the whole point): the constants 7, 19, state size
32, and the rotation scheme were CHOSEN, not justified by diffusion analysis.
Expect keystream bias, slow avalanche, and maybe key-schedule correlations.

HARD RULE for any stream cipher (true even for secure ones): never reuse a
(key, nonce) pair. Reuse => XOR of two ciphertexts leaks both plaintexts.
"""

from __future__ import annotations

GOLD = 157
N = 32            # ring size (power of two so mod is a mask)
MASK = N - 1
WARMUP = 64       # discarded steps so key/nonce diffuse before output


def _rotl8(x: int, r: int) -> int:
    x &= 0xFF
    return ((x << r) | (x >> (8 - r))) & 0xFF


class Tendril:
    def __init__(self, key: bytes, nonce: bytes):
        if not key or not nonce:
            raise ValueError("key and nonce must be non-empty")
        self.S = [0] * N
        for i in range(N):
            self.S[i] = (i * GOLD + key[i % len(key)] + nonce[i % len(nonce)]) & 0xFF
        self.p = 0
        self.theta = 0
        for _ in range(WARMUP):
            self._step()

    def _step(self) -> int:
        self.theta = (self.theta + GOLD) & 0xFF
        self.p = (self.p + 1 + (self.theta >> 6)) & MASK
        b = self.S[(self.p + 7) & MASK]
        c = self.S[(self.p + 19) & MASK]
        r = 1 + (self.theta & 7)
        m = (_rotl8((self.S[self.p] + b) & 0xFF, r) ^ c ^ self.theta) & 0xFF
        self.S[self.p] = m
        return m ^ self.S[m & MASK]

    def keystream(self, n: int) -> bytes:
        return bytes(self._step() for _ in range(n))


def keystream(key: bytes, nonce: bytes, n: int) -> bytes:
    return Tendril(key, nonce).keystream(n)


def crypt(key: bytes, nonce: bytes, data: bytes) -> bytes:
    ks = keystream(key, nonce, len(data))
    return bytes(a ^ b for a, b in zip(data, ks))


encrypt = crypt
decrypt = crypt  # XOR stream: same operation both ways


if __name__ == "__main__":
    key, nonce = b"tendril-key-1", b"vine2024"
    msg = b"the vine climbs toward the morning light"
    ct = encrypt(key, nonce, msg)
    assert decrypt(key, nonce, ct) == msg, "roundtrip failed"
    print("roundtrip OK\n")

    print("--- TEST VECTORS (reproduce these to verify your reimplementation) ---")
    for k, n_, ln in [(b"k", b"n", 16), (b"tendril", b"vine", 16),
                      (b"TENDRIL-1", b"cycloid1", 24)]:
        print(f"key={k!r} nonce={n_!r} keystream[{ln}]={keystream(k, n_, ln).hex()}")

    # The public challenge (nonce, ciphertext, crib, commitment) lives in
    # CHALLENGE.md. Its key and plaintext are intentionally NOT in this repo.
