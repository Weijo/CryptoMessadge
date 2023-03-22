from axolotl.state.identitykeystore import IdentityKeyStore
from axolotl.ecc.curve import Curve
from axolotl.identitykey import IdentityKey
from axolotl.util.keyhelper import KeyHelper
from axolotl.identitykeypair import IdentityKeyPair
from axolotl.ecc.curve import ECKeyPair
from axolotl.ecc.djbec import DjbECPublicKey, DjbECPrivateKey

from os.path import exists
import json, base64

class MyIdentityKeyStore(IdentityKeyStore):
    def __init__(self, name):
        CLIENT_STORE_FILEPATH = name + ".json"

        self.trustedKeys = {}

        file_exists = exists(CLIENT_STORE_FILEPATH)

        if file_exists:
            with open(CLIENT_STORE_FILEPATH) as json_file:
                data = json.load(json_file)

            # Remove one extra byte (\x05) added for some reason
            public_key = base64.b64decode(data["identity_key_public"]).replace(b'\x05', b'')

            private_key = base64.b64decode(data["identity_key_private"])

            # Reconstruct long-term identity key from json file
            identityKeyPairKeys = ECKeyPair(DjbECPublicKey(public_key), DjbECPrivateKey(private_key))
            self.identityKeyPair = IdentityKeyPair(IdentityKey(identityKeyPairKeys.getPublicKey()),
                                                identityKeyPairKeys.getPrivateKey())

            # Retrieve registration id from json file
            self.localRegistrationId = data["registration_id"]
        else:
            # Generate new long-term identity key
            identityKeyPairKeys = Curve.generateKeyPair()
            self.identityKeyPair = IdentityKeyPair(IdentityKey(identityKeyPairKeys.getPublicKey()),
                                                identityKeyPairKeys.getPrivateKey())
            
            # Generate new registration id
            self.localRegistrationId = KeyHelper.generateRegistrationId()

    def getIdentityKeyPair(self):
        return self.identityKeyPair

    def getLocalRegistrationId(self):
        return self.localRegistrationId

    def saveIdentity(self, recepientId, identityKey):
        self.trustedKeys[recepientId] = identityKey

    def isTrustedIdentity(self, recepientId, identityKey):
        if recepientId not in self.trustedKeys:
            return True
        return self.trustedKeys[recepientId] == identityKey