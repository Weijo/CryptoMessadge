from axolotl.state.signedprekeystore import SignedPreKeyStore
from axolotl.state.signedprekeyrecord import SignedPreKeyRecord
from axolotl.invalidkeyidexception import InvalidKeyIdException
from axolotl.ecc.djbec import *
import sys

class LiteSignedPreKeyStore(SignedPreKeyStore):
    def __init__(self, dbConn):
        """
        :type dbConn: Connection
        """
        self.dbConn = dbConn
        dbConn.execute("CREATE TABLE IF NOT EXISTS signed_prekeys (_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                       "registration_id INTEGER, prekey_id INTEGER UNIQUE, timestamp INTEGER, record BLOB);")


    def loadSignedPreKey(self, signedPreKeyId):
        q = "SELECT record FROM signed_prekeys WHERE prekey_id = ?"

        cursor = self.dbConn.cursor()
        cursor.execute(q, (signedPreKeyId,))

        result = cursor.fetchone()
        if not result:
            raise InvalidKeyIdException("No such signedprekeyrecord! %s " % signedPreKeyId)

        return SignedPreKeyRecord(serialized=result[0])

    def loadSignedPreKeys(self):
        q = "SELECT record FROM signed_prekeys"

        cursor = self.dbConn.cursor()
        cursor.execute(q,)
        result = cursor.fetchall()
        results = []
        for row in result:
            results.append(SignedPreKeyRecord(serialized=row[0]))

        return results

    def storeSignedPreKey(self, registration_id, signedPreKeyId, signedPreKeyRecord):
        q = "INSERT OR IGNORE INTO signed_prekeys (registration_id, prekey_id, record) VALUES(?,?,?)"
        cursor = self.dbConn.cursor()

        record = DjbECPublicKey(signedPreKeyRecord[1:]).serialize()

        cursor.execute(q, (registration_id, signedPreKeyId, record))
        self.dbConn.commit()

    def containsSignedPreKey(self, signedPreKeyId):
        q = "SELECT record FROM signed_prekeys WHERE prekey_id = ?"
        cursor = self.dbConn.cursor()
        cursor.execute(q, (signedPreKeyId,))
        return cursor.fetchone() is not None

    def removeSignedPreKey(self, signedPreKeyId):
        q = "DELETE FROM signed_prekeys WHERE prekey_id = ?"
        cursor = self.dbConn.cursor()
        cursor.execute(q, (signedPreKeyId,))
        self.dbConn.commit()
