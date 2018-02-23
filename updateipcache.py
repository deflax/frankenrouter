# downloads and update the ip cache.

import requests
import json
import sys
import re

conffile = open('/root/frankenrouter/config.sh', 'r')
for line in conffile:
    if re.search('LABEL', line):
        slave_name = line.split('=', 1)[1].rstrip().replace('"', '')
conffile.close()

conffile = open('/root/frankenrouter/config.sh', 'r')
for line in conffile:
    if re.search('APIHOST', line):
        api_host = line.split('=', 1)[1].rstrip().replace('"', '')
conffile.close()

api_url = 'https://' + str(api_host) + '/vmanager/slavetables'

###

try:
    data = {"passphrase": "batkataisthebest1", "slavename": str(slave_name)}
    apireq = requests.post(api_url, headers={'Content-Type': 'application/json'}, data=json.dumps(data), timeout=30)
    result = apireq.json()
except:
    sys.exit()

if result['status'] == 'ok':
    del result['status']
    wr = open('/root/pubip.cache', 'w')
    wr.write(json.dumps(result))
    wr.close()
    print('public ip cache updated')

