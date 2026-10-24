# 🏆 The TENDRIL-1 challenge

Break it. Everything below is **public**; only the **key** is secret.

This is a **known-plaintext** attack: the first 18 bytes of the message are given,
so you get 18 bytes of keystream for free (`keystream = ciphertext XOR plaintext`
on those positions). Can you recover the key, or predict the rest of the keystream
and read the whole message?

## The data

| field | value |
|---|---|
| algorithm | TENDRIL-1 (see [README](README.md) / `tendril.py`) |
| nonce (hex) | `626c6f6f6d2d3031` |
| ciphertext (hex) | `0aaf6eab8a7dabd30eb0b5e2fb2d8d972b356b6f77be05f20220719d4df38250c495d63e15d7b8223ad14e1daa03b8cdb9ba0db7ec5b46b85857b71a180676960949a50d189d55c9334bc82e` |
| known crib | the plaintext begins with `Dear breaker, the ` (18 bytes) |
| commitment | `sha256(plaintext) = 7eab3da68b74e44411b4382e9ee20f8c244cf60ce3970dc17dd81609f44c43fb` |
| ciphertext length | 76 bytes |

## How to verify a solution

Compute `sha256` of the plaintext you recovered. If it equals the commitment
above, you solved it:

```python
import hashlib
hashlib.sha256(your_plaintext_bytes).hexdigest() == \
  "7eab3da68b74e44411b4382e9ee20f8c244cf60ce3970dc17dd81609f44c43fb"
```

## Submit

Open an issue titled `solved` with:
1. the recovered plaintext (and key, if you got it),
2. a short description of your method — that's the part everyone learns from.

Partial breaks are welcome too: a keystream distinguisher, a bias, a state-recovery
shortcut, a reduced-key-space argument. Show your work.

## Fair-play notes

- Attack the **cipher**, not the host. No brute-forcing of anything but TENDRIL-1 itself.
- The key is a short printable string. "Just brute-force all keys" is a valid break
  if you can show the cipher makes it feasible — but the interesting wins are
  structural (bias, state recovery, key-schedule weakness).
