import base64

from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from Crypto.Cipher import AES
from doubleratchet1.function import SymmRatchet, pad, unpad

class DoubleRatchet(object):
    def __init__(self):
        self.DHratchet = None

    def init_DHratchets(self):
        # initialise DH ratchet
        self.DHratchet = X25519PrivateKey.generate()

    def init_ratchets(self, sk):
        # initialise the root chain with the shared key
        self.root_ratchet = SymmRatchet(sk)
        # initialise the sending and recving chains
        self.send_ratchet = SymmRatchet(self.root_ratchet.next()[0])
        self.recv_ratchet = SymmRatchet(self.root_ratchet.next()[0])

    def dh_ratchet(self, pk):
        # perform a DH ratchet rotation using sender's public key
        if self.DHratchet is not None:
            # the first time we don't have a DH ratchet yet
            dh_recv = self.DHratchet.exchange(pk)
            shared_recv = self.root_ratchet.next(dh_recv)[0]
            # use sender's public and our old private key
            # to get a new recv ratchet
            self.recv_ratchet = SymmRatchet(shared_recv)
        # generate a new key pair and send ratchet
        # our new public key will be sent with the next message to recipient
        self.DHratchet = X25519PrivateKey.generate()
        dh_send = self.DHratchet.exchange(pk)
        shared_send = self.root_ratchet.next(dh_send)[0]
        self.send_ratchet = SymmRatchet(shared_send)

    def encrypt(self, msg):
        key, iv = self.send_ratchet.next()
        cipher = AES.new(key, AES.MODE_CBC, iv).encrypt(pad(msg))
        return cipher

    def decrypt(self, cipher, pk):
        # receive sender's new public key and use it to perform a DH
        self.dh_ratchet(pk)
        key, iv = self.recv_ratchet.next()
        # decrypt the message using the new recv ratchet
        msg = unpad(AES.new(key, AES.MODE_CBC, iv).decrypt(cipher))
        return msg