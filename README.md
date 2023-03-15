# CryptoMessadge

## Overall idea
Messaging app that uses a couple of cryptographic algorithms

- OPAQUE (Authenticated Key Exchange)
- ChaCha20poly1305 (Message encryption)
- X3DH (Client-Client key exchange)
- Double Ratchet (End-to-End message encryption)

## How to run
The libopaque library uses python bindings to a c compiled opaque library found [here](https://github.com/stef/libopaque)

I have included a 64 bit linux shared object `libopaque.so` to the repository but you will need to run the following for it to work.

Assumming libopaque.so is in current directory:
```
export LD_LIBRARY_PATH=$(readlink -m .)
python3 client.py
```
