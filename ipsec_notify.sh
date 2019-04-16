#!/bin/bash

set -o nounset
set -o errexit

VTI_IF="vti${PLUTO_UNIQUEID}"

case "${PLUTO_VERB}" in
    up-client)
        ip tunnel add "${VTI_IF}" mode vti \
                        local "${PLUTO_ME}" remote "${PLUTO_PEER}" \
            okey "${PLUTO_MARK_OUT%%/*}" ikey "${PLUTO_MARK_IN%%/*}"
        ip link set "${VTI_IF}" up
        ip addr add ${PLUTO_MY_SOURCEIP} dev "${VTI_IF}"
        iptables -t nat -A POSTROUTING -o "${VTI_IF}" -j MASQUERADE
        ip route add default dev "${VTI_IF}" table vpn
        ip rule add from all fwmark 0x100 lookup vpn
        sysctl -w "net.ipv4.conf.${VTI_IF}.disable_policy=1"
        ;;
    down-client)
        ip rule del from all fwmark 0x100 lookup vpn
        ip route del default dev "${VTI_IF}" table vpn
        iptables -t nat -D POSTROUTING -o "${VTI_IF}" -j MASQUERADE
        ip tunnel del "${VTI_IF}"
        ;;
esac
