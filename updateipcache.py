# downloads and update the ip cache.

import requests
import json
import sys

slave_name = 'lexx'

api_url = 'https://www.datapoint.bg/vmanager/slavetables'

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

