from axolotl.util.keyhelper import KeyHelper
from axolotl.identitykeypair import IdentityKeyPair
from axolotl.groups.senderkeyname import SenderKeyName
from axolotl.axolotladdress import AxolotlAddress
from axolotl.sessioncipher import SessionCipher
from axolotl.groups.groupcipher import GroupCipher
from axolotl.groups.groupsessionbuilder import GroupSessionBuilder
from axolotl.sessionbuilder import SessionBuilder
from axolotl.protocol.prekeywhispermessage import PreKeyWhisperMessage
from axolotl.protocol.whispermessage import WhisperMessage
from axolotl.state.prekeybundle import PreKeyBundle
from axolotl.untrustedidentityexception import UntrustedIdentityException
from axolotl.invalidmessageexception import InvalidMessageException
from axolotl.duplicatemessagexception import DuplicateMessageException
from axolotl.invalidkeyidexception import InvalidKeyIdException
from axolotl.nosessionexception import NoSessionException
from axolotl.protocol.senderkeydistributionmessage import SenderKeyDistributionMessage
from axolotl.state.axolotlstore import AxolotlStore
import random, sys
import logging
from Util.ClientStore.sqlite.liteaxolotstore import LiteAxolotlStore


logger = logging.getLogger(__name__)

class AxolotlManager(object):

    COUNT_GEN_PREKEYS = 100
    THRESHOLD_REGEN = 10
    MAX_SIGNED_PREKEY_ID = 16777215

    def __init__(self, store, username):
        """
        :param store:
        :type store: AxolotlStore
        :param username:
        :type username: str
        """
        self._username = username # type: str
        self._store = store # type: LiteAxolotlStore
        self._identity = self._store.getIdentityKeyPair() # type: IdentityKeyPair
        self._registration_id = self._store.getLocalRegistrationId() # type: int | None

        assert self._registration_id is not None
        assert self._identity is not None

        self._group_session_builder = GroupSessionBuilder(self._store) # type: GroupSessionBuilder
        self._session_ciphers = {} # type: dict[str, SessionCipher]
        self._group_ciphers = {} # type: dict[str, GroupCipher]
        logger.debug("Initialized AxolotlManager [username=%s, db=%s]" % (self._username, store))

    def level_prekeys(self, force=False):
        logger.debug("level_prekeys(force=%s)" % force)
        len_pending_prekeys = len(self._store.loadPreKeys())
        logger.debug("len(pending_prekeys) = %d" % len_pending_prekeys)
        if force or len_pending_prekeys < self.THRESHOLD_REGEN:
            count_gen = self.COUNT_GEN_PREKEYS
            max_prekey_id = self._store.preKeyStore.loadMaxPreKeyId()
            logger.info("Generating %d prekeys, current max_prekey_id=%d" % (count_gen, max_prekey_id))
            prekeys = KeyHelper.generatePreKeys(max_prekey_id + 1, count_gen)
            logger.info("Storing %d prekeys" % len(prekeys))
            for i in range(0, len(prekeys)):
                key = prekeys[i]
                if logger.level <= logging.DEBUG:
                    sys.stdout.write("Storing prekey %d/%d \r" % (i + 1, len(prekeys)))
                    sys.stdout.flush()
                self._store.storePreKey(key.getId(), key)
            return prekeys
        return []
    
    def generate_signed_prekey(self):
        logger.debug("generate_signed_prekey")
        latest_signed_prekey = self.load_latest_signed_prekey(generate=False)
        if latest_signed_prekey is not None:
            if latest_signed_prekey.getId() == self.MAX_SIGNED_PREKEY_ID:
                new_signed_prekey_id = (self.MAX_SIGNED_PREKEY_ID / 2) + 1
            else:
                new_signed_prekey_id = latest_signed_prekey.getId() + 1
        else:
            new_signed_prekey_id = 0
        signed_prekey = KeyHelper.generateSignedPreKey(self._identity, new_signed_prekey_id)
        self._store.storeSignedPreKey(signed_prekey.getId(), signed_prekey)
        return signed_prekey
    
    def load_latest_signed_prekey(self, generate=False):
        logger.debug("load_latest_signed_prekey")
        signed_prekeys = self._store.loadSignedPreKeys()
        if len(signed_prekeys):
            return signed_prekeys[-1]
        
        return self.generate_signed_prekey() if generate else None