# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: proto/signalc_group.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x19proto/signalc_group.proto\x12\rsignalc_group\"\x1f\n\x0c\x42\x61seResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\"s\n\x1dGroupRegisterSenderKeyRequest\x12\x0f\n\x07groupId\x18\x01 \x01(\t\x12\x10\n\x08\x63lientId\x18\x02 \x01(\t\x12\x10\n\x08\x64\x65viceId\x18\x03 \x01(\x05\x12\x1d\n\x15senderKeyDistribution\x18\x04 \x01(\x0c\"1\n\x1eGroupRegisterSenderKeyResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\"Y\n\x14GroupSenderKeyObject\x12\x10\n\x08senderId\x18\x02 \x01(\t\x12\x10\n\x08\x64\x65viceId\x18\x03 \x01(\x05\x12\x1d\n\x15senderKeyDistribution\x18\x04 \x01(\x0c\"=\n\x18GroupGetSenderKeyRequest\x12\x0f\n\x07groupId\x18\x01 \x01(\t\x12\x10\n\x08senderId\x18\x02 \x01(\t\"d\n\x19GroupGetSenderKeyResponse\x12\x0f\n\x07groupId\x18\x01 \x01(\t\x12\x36\n\tsenderKey\x18\x02 \x01(\x0b\x32#.signalc_group.GroupSenderKeyObject\".\n\x1bGroupGetAllSenderKeyRequest\x12\x0f\n\x07groupId\x18\x01 \x01(\t\"j\n\x1cGroupGetAllSenderKeyResponse\x12\x0f\n\x07groupId\x18\x01 \x01(\t\x12\x39\n\x0c\x61llSenderKey\x18\x02 \x03(\x0b\x32#.signalc_group.GroupSenderKeyObject\"I\n\x13GroupPublishRequest\x12\x10\n\x08senderId\x18\x01 \x01(\t\x12\x0f\n\x07groupId\x18\x02 \x01(\t\x12\x0f\n\x07message\x18\x03 \x01(\x0c\"2\n\x1eGroupSubscribeAndListenRequest\x12\x10\n\x08\x63lientId\x18\x01 \x01(\t\"F\n\x10GroupPublication\x12\x10\n\x08senderId\x18\x01 \x01(\t\x12\x0f\n\x07groupId\x18\x02 \x01(\t\x12\x0f\n\x07message\x18\x03 \x01(\x0c\x32\xf1\x04\n\x1aGroupSenderKeyDistribution\x12u\n\x16RegisterSenderKeyGroup\x12,.signalc_group.GroupRegisterSenderKeyRequest\x1a-.signalc_group.GroupRegisterSenderKeyResponse\x12h\n\x13GetSenderKeyInGroup\x12\'.signalc_group.GroupGetSenderKeyRequest\x1a(.signalc_group.GroupGetSenderKeyResponse\x12q\n\x16GetAllSenderKeyInGroup\x12*.signalc_group.GroupGetAllSenderKeyRequest\x1a+.signalc_group.GroupGetAllSenderKeyResponse\x12W\n\tSubscribe\x12-.signalc_group.GroupSubscribeAndListenRequest\x1a\x1b.signalc_group.BaseResponse\x12Z\n\x06Listen\x12-.signalc_group.GroupSubscribeAndListenRequest\x1a\x1f.signalc_group.GroupPublication0\x01\x12J\n\x07Publish\x12\".signalc_group.GroupPublishRequest\x1a\x1b.signalc_group.BaseResponseb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'proto.signalc_group_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _BASERESPONSE._serialized_start=44
  _BASERESPONSE._serialized_end=75
  _GROUPREGISTERSENDERKEYREQUEST._serialized_start=77
  _GROUPREGISTERSENDERKEYREQUEST._serialized_end=192
  _GROUPREGISTERSENDERKEYRESPONSE._serialized_start=194
  _GROUPREGISTERSENDERKEYRESPONSE._serialized_end=243
  _GROUPSENDERKEYOBJECT._serialized_start=245
  _GROUPSENDERKEYOBJECT._serialized_end=334
  _GROUPGETSENDERKEYREQUEST._serialized_start=336
  _GROUPGETSENDERKEYREQUEST._serialized_end=397
  _GROUPGETSENDERKEYRESPONSE._serialized_start=399
  _GROUPGETSENDERKEYRESPONSE._serialized_end=499
  _GROUPGETALLSENDERKEYREQUEST._serialized_start=501
  _GROUPGETALLSENDERKEYREQUEST._serialized_end=547
  _GROUPGETALLSENDERKEYRESPONSE._serialized_start=549
  _GROUPGETALLSENDERKEYRESPONSE._serialized_end=655
  _GROUPPUBLISHREQUEST._serialized_start=657
  _GROUPPUBLISHREQUEST._serialized_end=730
  _GROUPSUBSCRIBEANDLISTENREQUEST._serialized_start=732
  _GROUPSUBSCRIBEANDLISTENREQUEST._serialized_end=782
  _GROUPPUBLICATION._serialized_start=784
  _GROUPPUBLICATION._serialized_end=854
  _GROUPSENDERKEYDISTRIBUTION._serialized_start=857
  _GROUPSENDERKEYDISTRIBUTION._serialized_end=1482
# @@protoc_insertion_point(module_scope)
