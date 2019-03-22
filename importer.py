#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function

import grpc
from google.protobuf.any_pb2 import Any

import gobgp_pb2
import gobgp_pb2_grpc
import attribute_pb2

import redis
r=redis.Redis(host='localhost', port=6379, db=7)

_TIMEOUT_SECONDS = 1000

def pack_nlri(route):
    nlri = Any()
    r=route.split('/')
#    prefix_len=r[1]
#    prefix=r[0]
    nlri.Pack(attribute_pb2.IPAddressPrefix(prefix_len=int(r[1]),prefix=r[0]))
    return nlri

def pack_community(suffix):
    community = Any()
    community.Pack(attribute_pb2.CommunitiesAttribute(communities=[int(suffix)]))
    return community


def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = gobgp_pb2_grpc.GobgpApiStub(channel)

#    nlri = Any()
#    nlri.Pack(attribute_pb2.IPAddressPrefix(
#        prefix_len=24,
#        prefix="10.0.0.0",
#    ))
    origin = Any()
    origin.Pack(attribute_pb2.OriginAttribute(
        origin=2,  # INCOMPLETE
    ))
    as_segment = attribute_pb2.AsSegment(
        # type=2,  # "type" causes syntax error
        numbers=[64999],
    )
    as_segment.type = 2  # SEQ
    as_path = Any()
    as_path.Pack(attribute_pb2.AsPathAttribute(
        segments=[as_segment],
    ))
    next_hop = Any()
    next_hop.Pack(attribute_pb2.NextHopAttribute(
        next_hop="127.0.0.1",
    ))
#    attributes = [origin, as_path, next_hop]
#    c=0
    while True:
        message = r.blpop('messages', timeout=0)
        if message:
            message=message[1]
#        print(message)
        transaction=message.decode('utf-8')
        data=transaction.split(':')
        path=data[3]
        action=data[2]
#        prefix=data[0]
        suffix=data[1]
        communities=pack_community(suffix)
        attributes = [origin, as_path, next_hop, communities]
        if action=='announce':
            stub.AddPath(
            gobgp_pb2.AddPathRequest(
                table_type=gobgp_pb2.GLOBAL,
                path=gobgp_pb2.Path(
                    nlri=pack_nlri(path),
                    pattrs=attributes,
                    family=gobgp_pb2.Family(afi=gobgp_pb2.Family.AFI_IP, safi=gobgp_pb2.Family.SAFI_UNICAST),
                )
            ),
            _TIMEOUT_SECONDS,
        )
        if action=='withdraw':
            stub.DeletePath(
            gobgp_pb2.DeletePathRequest(
                table_type=gobgp_pb2.GLOBAL,
                path=gobgp_pb2.Path(
                    nlri=pack_nlri(path),
                    pattrs=attributes,
                    family=gobgp_pb2.Family(afi=gobgp_pb2.Family.AFI_IP, safi=gobgp_pb2.Family.SAFI_UNICAST),
                )
            ),
            _TIMEOUT_SECONDS,
        )
if __name__ == '__main__':
    run()
