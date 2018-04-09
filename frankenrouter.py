# frankenrouter.py by afx (c) 2018 deflax.net

import subprocess
import requests
import json
import datetime
import os
import sys
import re

clientiface = 'ens19'
workscriptpath = '/root/fr-workscripts/'

###

def writefile(filename, data):
    wr = open(filename, 'w')
    wr.write(data)
    wr.close()

def bashexec(workfile, data):
    today = int(datetime.datetime.now().strftime("%s")) * 1000
    script = """
#!/bin/bash
#
# {0} generated at {1}
#

IPT="/sbin/iptables"
SYSCTL="/sbin/sysctl -w"

# Internet Interface
INET_IFACE="ens18"

# Localhost Interface
LO_IFACE="lo"
LO_IP="127.0.0.1"

{2}""".format(workfile, today, data)
    filename = os.path.join(workscriptpath, workfile + '.sh')
    #prevfile = os.path.join(workscriptpath, workfile + '-{}'.format(today) + '.bak')
    #subprocess.call('mv {0} {1}'.format(filename, prevfile), shell=True)
    subprocess.call('rm {0}'.format(filename), shell=True)
    writefile(filename, script)
    subprocess.call('chmod +x {}'.format(filename), shell=True)
    subprocess.call('{}'.format(filename), shell=True)

def initfw():
    data = """
echo "Loading kernel modules ..."
/sbin/modprobe ip_tables
/sbin/modprobe ip_conntrack
# /sbin/modprobe iptable_filter
# /sbin/modprobe iptable_mangle
# /sbin/modprobe iptable_nat
# /sbin/modprobe ipt_LOG
# /sbin/modprobe ipt_limit
# /sbin/modprobe ipt_MASQUERADE
# /sbin/modprobe ipt_owner
# /sbin/modprobe ipt_REJECT
# /sbin/modprobe ipt_mark
# /sbin/modprobe ipt_tcpmss
# /sbin/modprobe multiport
# /sbin/modprobe ipt_state
# /sbin/modprobe ipt_unclean
/sbin/modprobe ip_nat_ftp
/sbin/modprobe ip_conntrack_ftp
/sbin/modprobe ip_conntrack_irc

if [ "$SYSCTL" = "" ]
then
    echo "1" > /proc/sys/net/ipv4/ip_forward
else
    $SYSCTL net.ipv4.ip_forward="1"
fi

if [ "$SYSCTL" = "" ]
then
    echo "1" > /proc/sys/net/ipv4/tcp_syncookies
else
$SYSCTL net.ipv4.tcp_syncookies="1"
fi

if [ "$SYSCTL" = "" ]
then
    echo "1" > /proc/sys/net/ipv4/conf/all/rp_filter
else
    $SYSCTL net.ipv4.conf.all.rp_filter="1"
fi

if [ "$SYSCTL" = "" ]
then
    echo "1" > /proc/sys/net/ipv4/icmp_echo_ignore_broadcasts
else
    $SYSCTL net.ipv4.icmp_echo_ignore_broadcasts="1"
fi

if [ "$SYSCTL" = "" ]
then
    echo "0" > /proc/sys/net/ipv4/conf/all/accept_source_route
else
    $SYSCTL net.ipv4.conf.all.accept_source_route="0"
fi

if [ "$SYSCTL" = "" ]
then
    echo "1" > /proc/sys/net/ipv4/conf/all/secure_redirects
else
    $SYSCTL net.ipv4.conf.all.secure_redirects="1"
fi

#if [ "$SYSCTL" = "" ]
#then
#    echo "1" > /proc/sys/net/ipv4/conf/all/log_martians
#else
#    $SYSCTL net.ipv4.conf.all.log_martians="1"
#fi

echo "Flushing Tables ..."
# Reset Default Policies
$IPT -P INPUT ACCEPT
$IPT -P FORWARD ACCEPT
$IPT -P OUTPUT ACCEPT
$IPT -t nat -P PREROUTING ACCEPT
$IPT -t nat -P POSTROUTING ACCEPT
$IPT -t nat -P OUTPUT ACCEPT
$IPT -t mangle -P PREROUTING ACCEPT
$IPT -t mangle -P OUTPUT ACCEPT
$IPT -F
$IPT -t nat -F
$IPT -t mangle -F
$IPT -X
$IPT -t nat -X
$IPT -t mangle -X

if [ "$1" = "stop" ]
then
    echo "Firewall completely flushed!  Now running with no firewall."
exit 0
fi
$IPT -P INPUT DROP
$IPT -P OUTPUT DROP
$IPT -P FORWARD DROP

$IPT -N bad_packets
$IPT -N bad_tcp_packets
$IPT -N icmp_packets
$IPT -N udp_inbound
$IPT -N udp_outbound
$IPT -N tcp_inbound
$IPT -N tcp_outbound

#DEFAULT
#$IPT -A bad_packets -p ALL -i $INET_IFACE -s $LOCAL_NET -j LOG --log-prefix "fp=bad_packets:2 a=DROP "
#$IPT -A bad_packets -p ALL -i $INET_IFACE -s $LOCAL_NET -j DROP
#$IPT -A bad_packets -p ALL -m state --state INVALID -j LOG --log-prefix "fp=bad_packets:1 a=DROP "
$IPT -A bad_packets -p ALL -m state --state INVALID -j DROP
$IPT -A bad_packets -p tcp -j bad_tcp_packets
$IPT -A bad_packets -p ALL -j RETURN
#$IPT -A bad_tcp_packets -p tcp -i $LOCAL_IFACE -j RETURN
#$IPT -A bad_tcp_packets -p tcp ! --syn -m state --state NEW -j LOG --log-prefix "fp=bad_tcp_packets:1 a=DROP "
$IPT -A bad_tcp_packets -p tcp ! --syn -m state --state NEW -j DROP
#$IPT -A bad_tcp_packets -p tcp --tcp-flags ALL NONE -j LOG --log-prefix "fp=bad_tcp_packets:2 a=DROP "
$IPT -A bad_tcp_packets -p tcp --tcp-flags ALL NONE -j DROP
#$IPT -A bad_tcp_packets -p tcp --tcp-flags ALL ALL -j LOG --log-prefix "fp=bad_tcp_packets:3 a=DROP "
$IPT -A bad_tcp_packets -p tcp --tcp-flags ALL ALL -j DROP
#$IPT -A bad_tcp_packets -p tcp --tcp-flags ALL FIN,URG,PSH -j LOG --log-prefix "fp=bad_tcp_packets:4 a=DROP "
$IPT -A bad_tcp_packets -p tcp --tcp-flags ALL FIN,URG,PSH -j DROP
#$IPT -A bad_tcp_packets -p tcp --tcp-flags ALL SYN,RST,ACK,FIN,URG -j LOG --log-prefix "fp=bad_tcp_packets:5 a=DROP "
$IPT -A bad_tcp_packets -p tcp --tcp-flags ALL SYN,RST,ACK,FIN,URG -j DROP
#$IPT -A bad_tcp_packets -p tcp --tcp-flags SYN,RST SYN,RST -j LOG --log-prefix "fp=bad_tcp_packets:6 a=DROP "
$IPT -A bad_tcp_packets -p tcp --tcp-flags SYN,RST SYN,RST -j DROP
#$IPT -A bad_tcp_packets -p tcp --tcp-flags SYN,FIN SYN,FIN -j LOG --log-prefix "fp=bad_tcp_packets:7 a=DROP "
$IPT -A bad_tcp_packets -p tcp --tcp-flags SYN,FIN SYN,FIN -j DROP
$IPT -A bad_tcp_packets -p tcp -j RETURN

### ICMP
#$IPT -A icmp_packets --fragment -p ICMP -j LOG --log-prefix "fp=icmp_packets:1 a=DROP "
#$IPT -A icmp_packets --fragment -p ICMP -j DROP
#$IPT -A icmp_packets -p ICMP -s 0/0 --icmp-type 8 -j DROP
#$IPT -A icmp_packets -p ICMP -s 0/0 --icmp-type 11 -j ACCEPT
#$IPT -A icmp_packets -p ICMP -j RETURN
$IPT -A icmp_packets -p ICMP -j ACCEPT

#LOCAL
$IPT -A udp_inbound -p UDP -s 0/0 --destination-port 137 -j DROP
$IPT -A udp_inbound -p UDP -s 0/0 --destination-port 138 -j DROP
$IPT -A udp_inbound -p UDP -s 0/0 --source-port 67 --destination-port 68 -j ACCEPT
$IPT -A udp_inbound -p UDP -s 0/0 --destination-port 53 -j ACCEPT
$IPT -A udp_inbound -p UDP -j RETURN
$IPT -A tcp_inbound -p TCP -s 0/0 --destination-port 60022 -j ACCEPT
$IPT -A tcp_inbound -p TCP -j RETURN
$IPT -A udp_outbound -p UDP -s 0/0 -j ACCEPT
$IPT -A tcp_outbound -p TCP -s 0/0 -j ACCEPT

###############################################################################
echo "Process INPUT chain ..."
$IPT -A INPUT -p ALL -i $LO_IFACE -j ACCEPT
$IPT -A INPUT -p ALL -j bad_packets
#INPUT index: 3
#$IPT -A INPUT -p ALL -i $INET_IFACE -m state --state ESTABLISHED,RELATED -j ACCEPT
$IPT -A INPUT -p ALL -i $INET_IFACE -j ACCEPT
$IPT -A INPUT -p TCP -i $INET_IFACE -j tcp_inbound
$IPT -A INPUT -p UDP -i $INET_IFACE -j udp_inbound
$IPT -A INPUT -p ICMP -i $INET_IFACE -j icmp_packets
$IPT -A INPUT -m pkttype --pkt-type broadcast -j DROP
#$IPT -A INPUT -j LOG --log-prefix "fp=INPUT:99 a=DROP "

echo "Process FORWARD chain ..."
$IPT -A FORWARD -p ALL -j bad_packets
$IPT -A FORWARD -i $INET_IFACE -j ACCEPT
#FORWARD index: 3
#$IPT -A FORWARD -j LOG --log-prefix "fp=FORWARD:99 a=DROP "

echo "Process OUTPUT chain ..."
#$IPT -A OUTPUT -m state -p icmp --state INVALID -j DROP
$IPT -A OUTPUT -p ALL -s $LO_IP -j ACCEPT
$IPT -A OUTPUT -p ALL -o $LO_IFACE -j ACCEPT
#OUTPUT index: 3
$IPT -A OUTPUT -p ALL -o $INET_IFACE -j ACCEPT
$IPT -A OUTPUT -j LOG --log-prefix "fp=OUTPUT:99 a=DROP "

#$IPT -t nat -A POSTROUTING -o $INET_IFACE -j MASQUERADE
"""
    return data

def setvlans(clientiface, vlanmin=101, vlanmax=150):
    #vlans
    data = ''
    for vlanid in range(vlanmin, vlanmax + 1, 1):
        dhcpconf_template = """
#dhcpd.conf autogenerated by frankenrouter

authoritative;
default-lease-time 3600;
max-lease-time 7200;
ddns-update-style none;

option subnet-mask 255.255.255.0;
option domain-name-servers 87.120.110.2, 8.8.8.8;

#vlan {0}
host vlan{0}-vm {{
  hardware ethernet 8A:32:CD:E4:EE:11;
  fixed-address 10.0.{0}.10;
}}

subnet 10.0.{0}.0 netmask 255.255.255.0 {{
  option routers 10.0.{0}.1;
  range 10.0.{0}.11 10.0.{0}.99;
}}

""".format(vlanid)
        writefile('/root/fr-vlanconf/v{0}.dhconf'.format(vlanid), dhcpconf_template)

        data += """
### VLAN {0}
echo "setting up vlan: {0}"
kill -9 `cat /root/fr-vlanconf/v{0}.dhpid`
rm /root/fr-vlanconf/v{0}.dhpid

ip link del {1}.{0}
ip link add link {1} name {1}.{0} type vlan id {0}
ip link set dev {1}.{0} up
ip addr add 10.0.{0}.1/24 dev {1}.{0}

#$IPT -I INPUT 3 -p ALL -i {1}.{0} -d 10.0.{0}.255 -j ACCEPT
$IPT -I INPUT 3 -p ALL -i {1}.{0} -s 10.0.{0}.0/24 -j ACCEPT
$IPT -I FORWARD 3 -p ALL -i {1}.{0} -s 10.0.{0}.10 -j ACCEPT
#$IPT -I FORWARD 3 -p ALL -i {1}.{0} -o $INET_IFACE -s 10.0.{0}.10 -j ACCEPT
##$IPT -I FORWARD 3 -p ALL -i $INET_IFACE -o {1}.{0} -d 10.0.{0}.10 -m state --state NEW -j ACCEPT
$IPT -I OUTPUT 3 -p ALL -o {1}.{0} -j ACCEPT

touch /root/fr-vlanconf/v{0}.dhpid
touch /root/fr-vlanconf/v{0}.dhlease
dhcpd -4 -cf /root/fr-vlanconf/v{0}.dhconf -lf /root/fr-vlanconf/v{0}.dhlease -pf /root/fr-vlanconf/v{0}.dhpid {1}.{0}
""".format(vlanid, clientiface)
    return data

def allipsetup(iplist, ip_mask):
    rr = open(iplist, 'r').read()
    cache = json.loads(rr)
    for ip, vlan in cache.items():
        bashexec('ipadd-{}-{}-{}'.format(ip, ip_mask, vlan), assignip(ip, ip_mask, vlan))

def assignip(ip, ip_mask, vlan):
    data = """
ip link add vtap{1} link $INET_IFACE type macvlan
ip addr add {0}/{2} dev vtap{1}
ip link set dev vtap{1} up
$IPT -t nat -A PREROUTING -d {0} -j DNAT --to-destination 10.0.{1}.10
$IPT -t nat -A POSTROUTING -s 10.0.{1}.10 -j SNAT --to-source {0}
""".format(ip, vlan, ip_mask)
    return data

def removeip(ip, vlan):
    data = """
ip link set dev vtap{1} down
ip link delete vtap{1}
$IPT -t nat -D PREROUTING -d {0} -j DNAT --to-destination 10.0.{1}.10
$IPT -t nat -D POSTROUTING -s 10.0.{1}.10 -j SNAT --to-source {0}
""".format(ip, vlan)
    return data

if __name__ == "__main__":
    helpdata = """
python3 frankenrouter.py init --- setup the default firewall
python3 frankenrouter.py allipsetup --- read the contents of /root/pubip.cache and setup all assigments. for startup.

python3 frankenrouter.py ipadd IP VLAN --- add IP to VLAN
    example: ipadd 87.120.110.120 142

python3 frankenrouter,py ipdel IP VLAN --- del IP from VLAN
    example: ipdel 87.120.110.120 142
"""
    conffile = open('/root/frankenrouter/config.sh', 'r')
    for line in conffile:
        if re.search('TRANSPORT_MASK', line):
            ip_mask = line.split('=', 1)[1].rstrip().replace('"', '')
    conffile.close()

    try:
        if sys.argv[1] == 'init':
            bashexec('fwsetup', initfw())
            bashexec('vlsetup', setvlans(clientiface))

        if sys.argv[1] == 'allipsetup':
            allipsetup('/root/pubip.cache', ip_mask)

        if sys.argv[1] == 'ipadd':
            bashexec('ipadd-{}-{}'.format(sys.argv[2], sys.argv[3]), assignip(sys.argv[2], ip_mask, sys.argv[3]))

        if sys.argv[1] == 'ipdel':
            bashexec('ipdel-{}-{}'.format(sys.argv[2], sys.argv[3]), removeip(sys.argv[2], sys.argv[3]))
    except Exception as e:
        print(str(e))
        print(helpdata)

