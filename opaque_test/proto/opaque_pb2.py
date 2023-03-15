# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: proto/opaque.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x12proto/opaque.proto\x12\x06opaque\"8\n\x13RegistrationRequest\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\x0c\"9\n\x14RegistrationResponse\x12\x10\n\x08response\x18\x01 \x01(\x0c\x12\x0f\n\x07\x63ontext\x18\x02 \x01(\x0c\"D\n\x0f\x46inalizeRequest\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x0e\n\x06record\x18\x02 \x01(\x0c\x12\x0f\n\x07\x63ontext\x18\x03 \x01(\x0c\"&\n\x10\x46inalizeResponse\x12\x12\n\nregistered\x18\x01 \x01(\x08\"6\n\x11\x43redentialRequest\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x0f\n\x07request\x18\x02 \x01(\x0c\"7\n\x12\x43redentialResponse\x12\x10\n\x08response\x18\x01 \x01(\x0c\x12\x0f\n\x07\x63ontext\x18\x02 \x01(\x0c\"H\n\x15\x41uthenticationRequest\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x0c\n\x04\x61uth\x18\x02 \x01(\x0c\x12\x0f\n\x07\x63ontext\x18\x03 \x01(\x0c\"\'\n\x16\x41uthenticationResponse\x12\r\n\x05token\x18\x01 \x01(\t\"5\n\x12VerifyTokenRequest\x12\r\n\x05token\x18\x01 \x01(\t\x12\x10\n\x08username\x18\x02 \x01(\t\"\'\n\x13VerifyTokenResponse\x12\x10\n\x08is_valid\x18\x01 \x01(\x08\x32\x87\x03\n\x14OpaqueAuthentication\x12I\n\x0cRegisterUser\x12\x1b.opaque.RegistrationRequest\x1a\x1c.opaque.RegistrationResponse\x12@\n\x0bStoreRecord\x12\x17.opaque.FinalizeRequest\x1a\x18.opaque.FinalizeResponse\x12K\n\x12RequestCredentials\x12\x19.opaque.CredentialRequest\x1a\x1a.opaque.CredentialResponse\x12M\n\x0c\x41uthenticate\x12\x1d.opaque.AuthenticationRequest\x1a\x1e.opaque.AuthenticationResponse\x12\x46\n\x0bVerifyToken\x12\x1a.opaque.VerifyTokenRequest\x1a\x1b.opaque.VerifyTokenResponseb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'proto.opaque_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _REGISTRATIONREQUEST._serialized_start=30
  _REGISTRATIONREQUEST._serialized_end=86
  _REGISTRATIONRESPONSE._serialized_start=88
  _REGISTRATIONRESPONSE._serialized_end=145
  _FINALIZEREQUEST._serialized_start=147
  _FINALIZEREQUEST._serialized_end=215
  _FINALIZERESPONSE._serialized_start=217
  _FINALIZERESPONSE._serialized_end=255
  _CREDENTIALREQUEST._serialized_start=257
  _CREDENTIALREQUEST._serialized_end=311
  _CREDENTIALRESPONSE._serialized_start=313
  _CREDENTIALRESPONSE._serialized_end=368
  _AUTHENTICATIONREQUEST._serialized_start=370
  _AUTHENTICATIONREQUEST._serialized_end=442
  _AUTHENTICATIONRESPONSE._serialized_start=444
  _AUTHENTICATIONRESPONSE._serialized_end=483
  _VERIFYTOKENREQUEST._serialized_start=485
  _VERIFYTOKENREQUEST._serialized_end=538
  _VERIFYTOKENRESPONSE._serialized_start=540
  _VERIFYTOKENRESPONSE._serialized_end=579
  _OPAQUEAUTHENTICATION._serialized_start=582
  _OPAQUEAUTHENTICATION._serialized_end=973
# @@protoc_insertion_point(module_scope)