from flask import Flask, request, jsonify
import docker
import os
import yaml
import socket
import random

from dotenv import load_dotenv, find_dotenv
import threading
load_dotenv(find_dotenv())

app = Flask(__name__)
client = docker.from_env()

domain = os.getenv('DOMAIN_NAME')

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('', port))
            return False
        except socket.error:
            return True

def create_compose_config(username, randomised_port):
    return {
        'version': '3.7',
        'networks': {
            'traefik-network': {
                'external': True
            }
        },
        'services': {
            'n8n': {
                'image': '5quidw4rd/n8n-custom:latest',
                'restart': 'always',
                'networks': ['traefik-network'],
                'ports': {f'{randomised_port}:5678'},
                'labels': {
                    'traefik.enable': 'true',
                    'traefik.http.routers.n8n-{}'.format(username): f'Host(`{username}.{domain}`)',
                    'traefik.http.routers.n8n-{}.tls'.format(username): 'true',
                    'traefik.http.routers.n8n-{}.entrypoints'.format(username): 'web,websecure',
                    'traefik.http.routers.n8n-{}.tls.certresolver'.format(username): 'mytlschallenge',
                    'traefik.http.middlewares.n8n-{}.headers.SSLRedirect'.format(username): 'true',
                    'traefik.http.middlewares.n8n-{}.headers.STSSeconds'.format(username): '315360000',
                    'traefik.http.middlewares.n8n-{}.headers.forceSTSHeader'.format(username): 'true',
                    'traefik.http.middlewares.n8n-{}.headers.SSLHost'.format(username): f'{domain}',
                    'traefik.http.middlewares.n8n-{}.headers.STSIncludeSubdomains'.format(username): 'true',
                    'traefik.http.middlewares.n8n-{}.headers.STSPreload'.format(username): 'true',
                    'traefik.http.routers.n8n-{}.middlewares'.format(username): 'n8n@docker',
                },
                'environment': {
                    'N8N_HOST': f'{username}.{domain}',
                    'N8N_PORT': '5678',
                    'N8N_PROTOCOL': 'https',
                    'NODE_ENV': 'production',
                    'WEBHOOK_URL': f'https://{username}.{domain}/',
                    'GENERIC_TIMEZONE': 'Europe/Berlin'
                },
                'volumes': [
                    f'n8n_data_{username}:/home/node/.n8n'
                ]
            }
        },
        'volumes': {
            f'n8n_data_{username}': {
                'name': f'n8n_data_{username}'
            }
        }
    }

@app.route('/provision', methods=['POST'])
def provision_user():
    try:
        data = request.get_json()
        username = data.get('username')
        
        if not username:
            return jsonify({'error': 'Username is required'}), 400

        # get a random unused port
        while True:
            port = random.randint(49152, 65535)  # Dynamic port range
            if not is_port_in_use(port):
                break

        # Create compose config
        compose_config = create_compose_config(username, port)
        
        # Write compose file temporarily
        compose_file = f'/tmp/docker-compose-{username}.yml'
        with open(compose_file, 'w') as f:
            yaml.dump(compose_config, f)

        # Use docker-compose programmatically
        os.system(f'docker compose -f {compose_file} -p n8n-{username} up -d')
        
        # Clean up
        os.remove(compose_file)

        return jsonify({
            'status': 'success',
            'subdomain': f'{username}.{domain}'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/provision-test', methods=['POST'])
def provision_user_test():
    try:
        data = request.get_json()
        username = data.get('username')

        if not username:
            return jsonify({'error': 'Username is required'}), 400
        
        # get a random unused port
        while True:
            port = random.randint(49152, 65535)  # Dynamic port range
            if not is_port_in_use(port):
                break
        
        def run_container():
            os.system(f'docker volume create n8n_data_{username}')
            os.system(f'docker run --rm --name n8n-{username} -p {port}:5678 -v n8n_data_{username}:/home/node/.n8n 5quidw4rd/n8n-custom:latest start --tunnel')

        thread = threading.Thread(target=run_container)
        thread.daemon = True
        thread.start()

        return jsonify({
            'status': 'success',
            'url': f'http://localhost:{port}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def welcome():
    return 'Welcome to N8N Provisioning Service'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)