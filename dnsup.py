import requests
import json
import sys
import argparse

parser = argparse.ArgumentParser(description='A simple script for updating Cloudflare DNS records')
parser.add_argument('domain', help="The domain name for which the record should be updated")
parser.add_argument('ipv4', help="IPv4 address to enter into the record")
parser.add_argument('token', help='Zone.DNS API token from Cloudflare')
parser.add_argument('-p', '--proxy', help='Use this option to enable Cloudflare proxying for the domain', action='store_true')

args = vars(parser.parse_args())
domain = args['domain']
ip = args['ipv4']
token = args['token']
proxy = args['proxy']

class HTTPBadRequest(Exception):
    def __init__(self, status_code, resp_body):
        self.status_code = status_code
        self.resp_body = resp_body
        self.message = f'HTTP error: {status_code}\nResponse body: {resp_body}'
        super().__init__(self.message)

class NoRecordFound(Exception):
    def __init__(self):
        self.message = "No A records were found for the specified domain"
        super().__init__(self.message)

def check_http_err(response: requests.Response):
        if response.status_code != 200:
            raise HTTPBadRequest(response.status_code, response.text)
        else:
            return
        

def update_dns(domain, ip, token):
    # Get retrieve zone ID for the token
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    url = f"https://api.cloudflare.com/client/v4/zones"
    r = requests.get(url=url, headers=headers)
    check_http_err(r)

    zone_id = r.json()['result'][0]['id']

    # Check DNS records for specified domain
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    r = requests.get(url, headers=headers)
    check_http_err(r)

    record_id = None
    for i in r.json()['result']:
        if i['name'] == domain and i['type'] == 'A':
            record_id = i['id']
            print(f"record for {domain} has an id of {record_id}")
            break
    
    if record_id == None:
        raise NoRecordFound()
            
    url += f'/{record_id}'
    payload = {
        'content': ip,
        'name': domain,
        'proxied': False,
        'type': 'A'
    }

    r = requests.put(url=url, headers=headers, data=json.dumps(payload))
    check_http_err(r)
    print(f"DNS entry for {domain} updated successfully\n" + str(r.json()['result']))

    return 0


err = update_dns(domain=domain, ip=ip, token=token)
sys.exit(err)




