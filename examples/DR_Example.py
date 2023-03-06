from doubleratchet1 import DoubleRatchet as DR
from doubleratchet1.function import hkdf, b64

from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey

class X3DH:
    def x3dh_b(KEYa, KEYb):
        # perform the 4 Diffie Hellman exchanges (X3DH)
        dh1 = KEYb.get("SPK").exchange(KEYa.get("IK").public_key())
        dh2 = KEYb.get("IK").exchange(KEYa.get("EK").public_key())
        dh3 = KEYb.get("SPK").exchange(KEYa.get("EK").public_key())
        dh4 = KEYb.get("OPK").exchange(KEYa.get("EK").public_key())

        # the shared key is KDF(DH1||DH2||DH3||DH4)
        sk = hkdf(dh1 + dh2 + dh3 + dh4, 32)
        print('[Bob]\tShared key:', b64(sk))
        return sk

    def x3dh_a(KEYa, KEYb):
        # perform the 4 Diffie Hellman exchanges (X3DH)
        dh1 = KEYa.get("IK").exchange(KEYb.get("SPK").public_key())
        dh2 = KEYa.get("EK").exchange(KEYb.get("IK").public_key())
        dh3 = KEYa.get("EK").exchange(KEYb.get("SPK").public_key())
        dh4 = KEYa.get("EK").exchange(KEYb.get("OPK").public_key())

        # the shared key is KDF(DH1||DH2||DH3||DH4)
        sk = hkdf(dh1 + dh2 + dh3 + dh4, 32)
        print('[Alice]\tShared key:', b64(sk))
        return sk

def generateKeys():
    return {
        "IK": X25519PrivateKey.generate(),
        "SPK": X25519PrivateKey.generate(),
        "OPK": X25519PrivateKey.generate(),
        "EK": X25519PrivateKey.generate(),
    }


# generate Bob's keys
KEYb = generateKeys()
# generate Alice's keys
KEYa = generateKeys()  

def main():
    # Alice performs an X3DH while Bob is offline, using his uploaded keys
    sk_a = X3DH.x3dh_a(KEYa, KEYb)

    # Bob comes online and performs an X3DH using Alice's public keys
    sk_b = X3DH.x3dh_b(KEYa, KEYb)

    print("===========Example1===========")
    example1(sk_a, sk_b)
    print("\n===========Example2===========")
    example2(sk_a, sk_b)

'''
    Alice initiate the conversation
'''
def example1(sk_a, sk_b):
    alice = DR.DoubleRatchet()
    bob = DR.DoubleRatchet()

    bob.init_DHratchets()
    # Initialize their symmetric ratchets
    alice.init_ratchets(sk_a)
    bob.init_ratchets(sk_b)

    # Initialise Alice's sending ratchet with Bob's public key
    alice.dh_ratchet(bob.DHratchet.public_key())

    # Encrypt Alice message 
    cipher = alice.encrypt(b'Hello Bob!')
    print('Ciphertext:', b64(cipher))

    # Bob Decrypt Alice message 
    msg = bob.decrypt(cipher, alice.DHratchet.public_key())
    print('Decrypted Message:', msg)

    # Bob uses that information to sync with Alice and send her a message
    cipher = bob.encrypt(b'Hello to you too, Alice!')
    print('Ciphertext:', b64(cipher))

    # Bob Decrypt Alice message 
    msg = alice.decrypt(cipher, bob.DHratchet.public_key())
    print('Decrypted Message:', msg)


'''
    Bob initiate the conversation
'''
def example2(sk_a, sk_b):
    alice = DR.DoubleRatchet()
    bob = DR.DoubleRatchet()
    
    alice.init_DHratchets()
    # Initialize their symmetric ratchets
    alice.init_ratchets(sk_a)
    bob.init_ratchets(sk_b)

    # Initialise Bob's sending ratchet with Alice's public key
    bob.dh_ratchet(alice.DHratchet.public_key())

    # Encrypt Bob message 
    cipher = bob.encrypt(b'Hello Alice!')
    print('Ciphertext:', b64(cipher))

    # Alice Decrypt Bob message 
    msg = alice.decrypt(cipher, bob.DHratchet.public_key())
    print('Decrypted Message:', msg)

    # Encrypt Alice message 
    cipher = alice.encrypt(b'Hello to you too, Bob!')
    print('Ciphertext:', b64(cipher))

    # Bob Decrypt Alice message 
    msg = bob.decrypt(cipher, alice.DHratchet.public_key())
    print('Decrypted Message:', msg)

if __name__ == "__main__":
    main()