from axolotl.state.signedprekeystore import SignedPreKeyStore
from axolotl.state.signedprekeyrecord import SignedPreKeyRecord
from axolotl.invalidkeyidexception import InvalidKeyIdException


class MySignedPreKeyStore(SignedPreKeyStore):
    def __init__(self):
        self.store = {}

    def loadSignedPreKey(self, signedPreKeyId):
        if signedPreKeyId not in self.store:
            raise InvalidKeyIdException("No such signedprekeyrecord! %s " % signedPreKeyId)

        return SignedPreKeyRecord(serialized=self.store[signedPreKeyId])

    def loadSignedPreKeys(self):
        results = []
        for serialized in self.store.values():
            results.append(SignedPreKeyRecord(serialized=serialized))

        return results

    def storeSignedPreKey(self, signedPreKeyId, signedPreKeyRecord):
        self.store[signedPreKeyId] = signedPreKeyRecord.serialize()

    def containsSignedPreKey(self, signedPreKeyId):
        return signedPreKeyId in self.store

    def removeSignedPreKey(self, signedPreKeyId):
        del self.store[signedPreKeyId]