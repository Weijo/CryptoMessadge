# CryptoMessadge

## Overall idea
Messaging app that uses a couple of cryptographic algorithms

- OPAQUE (aPAKE Authentication)
- X3DH (Client-Client key exchange)
- Double Ratchet (End-to-End message encryption)

## How to run
The libopaque library uses python bindings to a c compiled opaque library found [here](https://github.com/stef/libopaque)

I have included a 64 bit linux shared object `libopaque.so` to the repository but you will need to run the following for it to work.

A Makefile is included for ease of running
```
# If proto folder is empty
make init

# Run server
make server

# Run client
make client
```
