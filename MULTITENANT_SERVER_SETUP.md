# Steps to set up multi-tenancy in remote server

1. Clone repository to root directory
2. Install docker, docker compose: 
- https://docs.n8n.io/hosting/installation/server-setups/docker-compose/#1-install-docker
- https://docs.n8n.io/hosting/installation/server-setups/docker-compose/#3-install-docker-compose
3. Setup DNS A records for domain name, wildcard subdomains and a CNAME for www support. Examples:
- A record: *.example.com => IP address
- A record: example.com => IP address
- CNAME: www => example.com
4. For cloudflare: Enable **full** SSL/TSL encryption mode
5. In root directory: docker compose -f docker-compose-prod.yaml up -d