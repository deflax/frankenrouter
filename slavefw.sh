#!/bin/bash

. /root/frankenrouter/config.sh

mkdir -p /root/fr-vlanconf
mkdir -p /root/fr-workscripts

ip addr add $TRANSPORT_IP/$TRANSPORT_MASK dev $PUBIF
sleep 3
ip route add default via $TRANSPORT_GW

python3 /root/frankenrouter/frankenrouter.py init
python3 /root/frankenrouter/frankenrouter.py allipadd


sysctl -p

