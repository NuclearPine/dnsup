## dnsup ##
A simple script to update Cloudflare DNS records. Currently only A records are supported.

## Usage ##

The syntax for using dnsup is:

`dnsup domain ip token`

where `domain` is the FQDN of the record to update, `ip` is the IPv4 address to insert into the record, and `token` is your Cloudflare API token. Use a token with edit permissions for a specific DNS zone.
