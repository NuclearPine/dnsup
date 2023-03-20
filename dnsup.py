import requests
import json
import sys
import argparse


def check_http_err(r: requests.Response):
        if r.status_code != 200:
            return f'HTTP error code: {r.status_code}\nResponse body: {r.text}'
        else:
            return None
        

def update_record(domain, ip, token):
    # Get zone ID for the token
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    url = f"https://api.cloudflare.com/client/v4/zones"
    r = requests.get(url=url, headers=headers)
    err = check_http_err(r)
    if err != None:
        return err

    zone_id = r.json()['result'][0]['id']

    # Check DNS records for specified domain
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    r = requests.get(url, headers=headers)
    err = check_http_err(r)
    if err != None:
        return err

    record_id = None
    for i in r.json()['result']:
        if i['name'] == domain and i['type'] == 'A':
            record_id = i['id']
            break
    
    if record_id == None:
        return f"Error: no A records found for {domain}"

    # PUT the new record into Cloudflare
    url += f'/{record_id}'
    payload = {
        'content': ip,
        'name': domain,
        'proxied': False,
        'type': 'A'
    }

    r = requests.put(url=url, headers=headers, data=json.dumps(payload))
    err = check_http_err(r)
    if err != None:
        return err
    
    return None

def main():
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

    err = update_record(domain=domain, ip=ip, token=token)
    if err != None:
        print(err, file=sys.stderr)
        sys.exit(1)
    
    print(f"Record for {domain} successfully updated")

if __name__ == '__main__':
     main()




