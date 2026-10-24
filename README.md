# 🪷 TENDRIL-1

An original, hand-made **stream cipher** — a climbing vine over a ring of nodes,
twisting by a rolling wheel — published so people can **try to break it**.

> ⚠️ **NOT SECURE.** This is a learning toy / break-me challenge, **not** real
> cryptography. Do not protect anything real with it. For that, use
> **ML-KEM (Kyber) + AES-256-GCM**.

**Live page & challenge:** https://hriprsd.github.io/tendril-cipher/

## What it is

TENDRIL-1 is an **ARX** (add-rotate-xor) stream cipher — the same toolkit as
ChaCha and BLAKE — but the engine is original: an ARX **ring-walk** with a
**golden-angle** pointer (phyllotaxis) and **cycloid-driven** rotations. It is
not RC4 (swap-based) and not ChaCha (fixed matrix).

## Spec (Kerckhoffs: everything public; only the key is secret)

State: 32 bytes `S[0..31]` on a ring (the vine). Movers: growth pointer `p`,
cycloid phase `θ`. `GOLD = 157` (odd, coprime to 256; ≈0.613 turn).

```
init: S[i] = (i*157 + key[i % |key|] + nonce[i % |nonce|]) mod 256
      then run 64 warmup steps (discard output)

per output byte:
  θ = (θ + 157) mod 256            # the wheel rolls
  p = (p + 1 + (θ >> 6)) mod 32    # tendril creeps forward, stride 1..4
  b = S[(p + 7)  mod 32]           # reach to older growth
  c = S[(p + 19) mod 32]
  r = 1 + (θ & 7)                  # twist amount 1..8
  m = rotl8((S[p] + b) mod 256, r) XOR c XOR θ
  S[p] = m                         # grow the node
  out  = m XOR S[m mod 32]         # nonlinear tap

encrypt = plaintext XOR keystream   (decrypt is identical)
```

**Hard rule for any stream cipher** (true even for secure ones): never reuse a
`(key, nonce)` pair. Reuse ⇒ XOR of two ciphertexts leaks both plaintexts.

## Run

```bash
python3 tendril.py          # self-test + test vectors
```

Or just open `index.html` in a browser (no build, no dependencies).

## Test vectors

| key | nonce | keystream (hex) |
|---|---|---|
| `k` | `n` | `78ec4c66679827a7733bc86c487ef1cb` |
| `tendril` | `vine` | `1c2e2fb518da4e1851f5eea8c71a3aee` |
| `TENDRIL-1` | `cycloid1` | `e6ae762c19f5a1940ed6303e479edf39c30350fadf436f26` |

## The challenge

Break it: recover the key (or the full plaintext) from a known-plaintext
ciphertext. Details, data, and a `sha256` commitment in **[CHALLENGE.md](CHALLENGE.md)**.
Found something? Open an issue describing your method.

## Where to attack

- **Keystream bias** — generate lots of output, look for byte/positional bias (how RC4/WEP fell).
- **Tiny state** — 32 bytes + two pointers; short cycles or internal collisions?
- **Arbitrary constants** — offsets 7 and 19, state size 32, rotation scheme were *chosen*, not justified; weak diffusion is likely.
- **Key schedule** — simple/linear before warmup; related-key / related-nonce correlations?

## Honest note

If TENDRIL-1 breaks, that's the lesson. If it survives a while, that only means
no one has broken it *yet* — which is **not** the same as secure. Reliability in
cryptography comes from years of public attack on standardized designs, not from
cleverness. Use ML-KEM + AES for anything real.

## License

MIT — see [LICENSE](LICENSE).
