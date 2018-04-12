# downloads and update the ip cache.

import requests
import json
import sys
import re
import subprocess

class DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current, self.set_past = set(current_dict.keys()), set(past_dict.keys())
        self.intersect = self.set_current.intersection(self.set_past)
    def added(self):
        return self.set_current - self.intersect 
    def removed(self):
        return self.set_past - self.intersect 
    def changed(self):
        return set(o for o in self.intersect if self.past_dict[o] != self.current_dict[o])
    def unchanged(self):
        return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])

conffile = open('/root/frankenrouter/config.sh', 'r')
for line in conffile:
    if re.search('APIHOST', line):
        api_host = line.split('=', 1)[1].rstrip().replace('"', '')
conffile.close()

api_url = 'https://' + str(api_host) + '/vmanager/slavetables'

conffile = open('/root/frankenrouter/config.sh', 'r')
for line in conffile:
    if re.search('LABEL', line):
        slave_name = line.split('=', 1)[1].rstrip().replace('"', '')
conffile.close()

###

try:
    data = {"passphrase": "batkataisthebest1", "slavename": str(slave_name)}
    apireq = requests.post(api_url, headers={'Content-Type': 'application/json'}, data=json.dumps(data), timeout=30)
    result = apireq.json()
except:
    print('can not connect')
    sys.exit()

if result['status'] == 'ok':
    del result['status']
    new_list = result

    # read cache to load the old values
    r_ca = open('/root/pubip.cache', 'r')
    current_list = json.loads(r_ca.read())
    r_ca.close()

    #compare the current value with the cache
    newdataflag = False
    difference = DictDiffer(new_list, current_list)
    if len(difference.removed()) is not 0:
        for ipkey in difference.removed():
            ip = ipkey
            vlan = current_list[ipkey]
            print('removed {} from {}'.format(ip, vlan))
            newdataflag = True
            subprocess.call('python3 /root/frankenrouter/frankenrouter.py ipdel {} {}'.format(ip, vlan), shell=True)
    if len(difference.added()) is not 0:
        for ipkey in difference.added():
            ip = ipkey
            vlan = new_list[ipkey]
            print('added {} to {}'.format(ip, vlan))
            newdataflag = True
            subprocess.call('python3 /root/frankenrouter/frankenrouter.py ipadd {} {}'.format(ip, vlan), shell=True)


    if newdataflag:
        # move the old cache and write the new data
        subprocess.call('mv /root/pubip.cache /root/pubip.cache.old', shell=True)
        w_ca = open('/root/pubip.cache', 'w')
        w_ca.write(json.dumps(new_list))
        w_ca.close()
        print('public ip cache updated with the new data')
    else:
        pass

else:
    print('no data error')


