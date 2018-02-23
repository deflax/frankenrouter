#!/bin/bash

. /root/frankenrouter/config.sh

mkdir -p /root/fr-vlanconf
mkdir -p /root/fr-workscripts

ip addr add $TRANSPORT_IP dev $PUBIF
sleep 5
ip route add default via $TRANSPORT_GW

python3 /root/frankenrouter/frankenrouter.py init

sysctl -p

