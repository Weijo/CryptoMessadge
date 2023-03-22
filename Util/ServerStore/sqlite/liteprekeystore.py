from axolotl.state.prekeystore import PreKeyStore
from axolotl.state.prekeyrecord import PreKeyRecord
from axolotl.ecc.djbec import *
import sys


class LitePreKeyStore(PreKeyStore):
    def __init__(self, dbConn):
        """
        :type dbConn: Connection
        """
        self.dbConn = dbConn
        dbConn.execute("CREATE TABLE IF NOT EXISTS prekeys (_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                       "registration_id INTEGER, prekey_id INTEGER, public_key BLOB);")

    def loadPreKey(self, preKeyId):
        q = "SELECT public_key FROM prekeys WHERE prekey_id = ?"

        cursor = self.dbConn.cursor()
        cursor.execute(q, (preKeyId,))

        result = cursor.fetchone()
        if not result:
            pass

        return PreKeyRecord(serialized = result[0])

    def storePreKey(self, registration_id, preKeyId, preKey_publicKey):
        #self.removePreKey(preKeyId)
        q = "INSERT INTO prekeys (registration_id, prekey_id, public_key) VALUES(?, ?,?)"
        cursor = self.dbConn.cursor()
        serialized = DjbECPublicKey(preKey_publicKey[1:]).serialize()
        
        cursor.execute(q, (registration_id, preKeyId, serialized))
        
        self.dbConn.commit()
