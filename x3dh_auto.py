import asyncio

from x3dh import KeyAgreementException
from x3dh.state import State
from x3dh.types import IdentityKeyFormat, Bundle
from x3dh.crypto_provider import HashFunction

import base64
import json
import os
import random
import time
from typing import Any, Dict, Iterator, List, Optional, Type, Union
from unittest import mock


def main():
    x3dh = x3dh_auto()
    asyncio.run(x3dh.test_key_agreements())


bundles: Dict[bytes, Bundle] = {}
THREE_DAYS = 3 * 24 * 60 * 60
EIGHT_DAYS = 8 * 24 * 60 * 60


class CustomState(State):
    """
    A state implementation for testing, which simulates bundle uploads by storing them in a global variable,
    and does some fancy public key encoding.
    """

    def _publish_bundle(self, bundle: Bundle) -> None:
        bundles[bundle.identity_key] = bundle

    @staticmethod
    def _encode_public_key(key_format: IdentityKeyFormat, pub: bytes) -> bytes:
        return b"\x42" + pub + b"\x13\x37" + key_format.value.encode("ASCII")


class x3dh_auto:

    def get_bundle(self, state: CustomState):
        """
        Retrieve a bundle from the simulated server.
        Args:
            state: The state to retrieve the bundle for.
        Returns:
            The bundle.
        """

        if state.bundle.identity_key in bundles:
            return bundles[state.bundle.identity_key]

    def create_state(self, state_settings: Dict[str, Any]):
        state = CustomState.create(**state_settings)
        # state = CustomState.create(IdentityKeyFormat.CURVE_25519, HashFunction.SHA_512, b"MyApp", None, 604800, 99,
        # 100)

        self.get_bundle(state)

        return state

    def generate_settings(self,
                          info: bytes,
                          signed_pre_key_rotation_period=7 * 24 * 60 * 60,  # 7 days
                          pre_key_refill_threshold=25,
                          pre_key_refill_target=100
                          ):
        """
        Generate state creation arguments.
        Args:
            info: The info to use constantly.
            signed_pre_key_rotation_period: The signed pre key rotation period to use constantly.
            pre_key_refill_threshold: The pre key refill threshold to use constantly.
            pre_key_refill_target. The pre key refill target to use constantly.
        Returns:
            State settings
        """

        state_settings: Dict[str, Any] = {
            "identity_key_format": IdentityKeyFormat.CURVE_25519,
            "hash_function": HashFunction.SHA_512,
            "info": info,
            "signed_pre_key_rotation_period": signed_pre_key_rotation_period,
            "pre_key_refill_threshold": pre_key_refill_threshold,
            "pre_key_refill_target": pre_key_refill_target
        }

        return state_settings

    # Treat a (Alice) as the active party, and b (Bob) as the passive party.
    async def test_key_agreements(self):
        """
        Test the general key agreement functionality.
        """

        state_settings = self.generate_settings("ict2205".encode("ASCII"))

        print("-" * 80)
        print(state_settings)
        state_a = self.create_state(state_settings)
        state_b = self.create_state(state_settings)

        # Get bundles before key agreement.
        bundle_a_before = self.get_bundle(state_a)
        bundle_b_before = self.get_bundle(state_b)

        # print("Alice's Identity Key (Before Key Agreement): ", bundle_a_before.identity_key)
        # print("Alice's Pre Keys (Before Key Agreement): ", bundle_a_before.pre_keys)
        print("Alice's Signed Pre Key (Before Key Agreement): ", bundle_a_before.signed_pre_key)
        # print("Alice's Signed Pre Key Signature (Before Key Agreement): ", bundle_a_before.signed_pre_key_sig)
        #
        # print("Bob's Identity Key (Before Key Agreement): ", bundle_b_before.identity_key)
        # print("Bob's Pre Keys (Before Key Agreement): ", bundle_b_before.pre_keys)
        print("Bob's Signed Pre Key (Before Key Agreement): ", bundle_b_before.signed_pre_key)
        # print("Bob's Signed Pre Key Signature (Before Key Agreement): ", bundle_b_before.signed_pre_key_sig)

        # Only rotate if signed pre-keys exceed 7 days in age.
        state_a.rotate_signed_pre_key()
        state_b.rotate_signed_pre_key()

        # Perform the first, active half of the key agreement
        shared_secret_active, associated_data_active, header = await state_a.get_shared_secret_active(
            bundle_b_before,
            "ad appendix".encode("ASCII")
        )

        # Perform the second, passive half of the key agreement
        shared_secret_passive, associated_data_passive, _ = await state_b.get_shared_secret_passive(
            header,
            "ad appendix".encode("ASCII")
        )

        # Get bundles after key agreement.
        bundle_a_after = self.get_bundle(state_a)
        bundle_b_after = self.get_bundle(state_b)

        # The bundle of the active party (Alice) should remain unmodified:
        assert bundle_a_after == bundle_a_before

        # The bundle of the passive party (Bob) should have been modified and published again:
        assert bundle_b_after != bundle_b_before

        # To be exact, only one pre key should have been removed from the bundle:
        assert bundle_b_after.identity_key == bundle_b_before.identity_key
        assert bundle_b_after.signed_pre_key == bundle_b_before.signed_pre_key
        assert bundle_b_after.signed_pre_key_sig == bundle_b_before.signed_pre_key_sig
        assert len(bundle_b_after.pre_keys) == len(bundle_b_before.pre_keys) - 1
        assert all(pre_key in bundle_b_before.pre_keys for pre_key in bundle_b_after.pre_keys)

        # Both parties should have derived the same shared secret and built the same
        # associated data:
        assert shared_secret_active == shared_secret_passive
        assert associated_data_active == associated_data_passive

        print("Alice's shared secret: ", shared_secret_active)
        print("Bob's shared secret: ", shared_secret_passive)

        print("Alice's associated data (ad): ", shared_secret_active)
        print("Bob's associated data (ad): ", shared_secret_passive)

        # print("Alice's Identity Key (after Key Agreement): ", bundle_a_after.identity_key)
        # print("Alice's Pre Keys (after Key Agreement): ", bundle_a_after.pre_keys)
        print("Alice's Signed Pre Key (after Key Agreement): ", bundle_a_after.signed_pre_key)
        # print("Alice's Signed Pre Key Signature (after Key Agreement): ", bundle_a_after.signed_pre_key_sig)

        # print("Bob's Identity Key (after Key Agreement): ", bundle_b_after.identity_key)
        # print("Bob's Pre Keys (after Key Agreement): ", bundle_b_after.pre_keys)
        print("Bob's Signed Pre Key (after Key Agreement): ", bundle_b_after.signed_pre_key)
        # print("Bob's Signed Pre Key Signature (after Key Agreement): ", bundle_b_after.signed_pre_key_sig)



if __name__ == '__main__':
    main()
