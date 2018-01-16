#!/bin/bash

PUBIF=ens18
TRANSPORT_IP="1.2.3.252/24"
TRANSPORT_GW="1.2.3.1"

ip addr add $TRANSPORT_IP dev $PUBIF
sleep 5
ip route add default via $TRANSPORT_GW

python3 /root/frankenrouter.py