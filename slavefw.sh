#!/bin/bash

PUBIF=ens18
TRANSPORT_IP="87.120.110.252/24"
TRANSPORT_GW="87.120.110.1"

mkdir -p /root/fr-vlanconf
mkdir -p /root/fr-workscripts

ip addr add $TRANSPORT_IP dev $PUBIF
sleep 5
ip route add default via $TRANSPORT_GW

sysctl -p

python3 /root/frankenrouter/frankenrouter.py init
python3 /root/frankenrouter/frankenrouter.py apply

