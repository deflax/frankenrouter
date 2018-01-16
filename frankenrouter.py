# frankenrouter.py by afx (c) 2018 deflax.net                              [42/9073]

import subprocess
import requests
import json
import datetime

dburl = 'https://www.datapoint.bg/vmanager/slavetables/1'
clientiface = 'ens19'

###

def setpubips():
    db_result = requests.get(dburl, headers={"content-type": "application/json"}, ti
meout=30 )
    proxjson = db_result.json()
    for key, value in proxjson['addresses'].items():
        pass
        #data += '#ip: ' + value['ipv4'] + '  mac:' + value['mac'] + '\n'
        #data += 'iptables -P FORWARD DROP\n'
        #data += 'iptables -P FORWARD -j ACCEPT -i '

    data = """
ip addr add 87.120.110.43/24 dev $PUBIF label $PUBIF:0
ip addr add 87.120.110.44/24 dev $PUBIF label $PUBIF:1
ip addr add 87.120.110.45/24 dev $PUBIF label $PUBIF:2
    """
    return data

def setvlans(vlanmin=101, vlanmax=200, clientiface)
    #vlans
    data = ''
    for vlanid in range(vlanmin, vlanmax, 1):
        data += """
kill -9 `cat /root/vlanconf/v{0}.dhpid`
rm /root/vlanconf/v{0}.dhpid
ip link del {1}.{0}
ip link add link {1} name {1}.{0} type vlan id {0}
ip link set dev {1}.{0} up
ip addr add 10.0.{0}.1/24 dev {1}.{0}
touch /root/vlanconf/v{0}.dhlease
dhcpd -4 -cf /root/vlanconf/v{0}.dhconf -lf /root/vlanconf/v{0}.dhlease -pf /root/vl
anconf/v{0}.dhpid {1}.{0}
""".format(vlanid, clientiface)
    return data

def bashexec(workfile, data)
    script = """
#!/bin/bash
#
# {0} generated at {1}
#

{2}""".format(workfile, datetime.datetime.now(), data)
    wr = open(workfile, 'w')
    wr.write(data)
    wr.close()
    subprocess.call('chmod +x {}'.format(workfile), shell=True)
    subprocess.call('./{}'.format(workfile), shell=True)

def routerinit():
    bashexec('globalfwconfig.sh', setglobalfw())
    bashexec('vlanconfig.sh', setvlans())
    bashexec('pubipconfig.sh', setpubips())

if __name__ == "__main__":
    routerinit()
