from flask import Flask, request, jsonify
import docker
import os
import yaml
import socket
import random
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from dotenv import load_dotenv, find_dotenv
import threading
load_dotenv(find_dotenv())

uri = "mongodb+srv://akaneai420:<db_password>@cluster0.jwyab3g.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))
users_mono = client['n8n-fork']['users-monolith']

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
        'networks': {
            'traefik-network': {
                'external': True
            }
        },
        'services': {
            'n8n': {
                'image': '5quidw4rd/n8n-custom-amd:latest',
                'restart': 'always',
                'networks': ['traefik-network'],
                'ports': [str(f'{randomised_port}:5678')],
                'container_name': f'n8n-{username}',
                'labels': {
                    'traefik.enable': 'true',
                    'traefik.http.routers.n8n-{}.rule'.format(username): f'Host(`{username}.{domain}`)',
                    'traefik.http.routers.n8n-{}.tls'.format(username): 'true',
                    'traefik.http.routers.n8n-{}.entrypoints'.format(username): 'web,websecure',
                    'traefik.http.routers.n8n-{}.tls.certresolver'.format(username): 'mytlschallenge',
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

def create_compose_config_mac(username, randomised_port):
    return {
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
                'ports': [str(f'{randomised_port}:5678')],
                'container_name': f'n8n-{username}',
                'labels': {
                    'traefik.enable': 'true',
                    'traefik.http.routers.n8n-{}.rule'.format(username): f'Host(`{username}.{domain}`)',
                    'traefik.http.routers.n8n-{}.tls'.format(username): 'true',
                    'traefik.http.routers.n8n-{}.entrypoints'.format(username): 'web,websecure',
                    'traefik.http.routers.n8n-{}.tls.certresolver'.format(username): 'mytlschallenge',
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

        # check if username is being used
        if users_mono.find_one({'username': username}):
            return jsonify({'error': 'Username is already in use'}), 400
        
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
        compose_file = f'/tmp/docker-compose-{username}.yaml'
        with open(compose_file, 'w') as f:
            yaml.dump(compose_config, f)

        # Use docker-compose programmatically
        os.system(f'docker compose -f {compose_file} -p n8n-{username} up -d')
        
        # Clean up
        os.remove(compose_file)

        # add to database with username, subdomain, port, container name
        users_mono.insert_one({
            'username': username,
            'subdomain': f'{username}.{domain}',
            'port': port,
            'container_name': f'n8n-{username}'
        })

        return jsonify({
            'status': 'success',
            'subdomain': f'{username}.{domain}'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stop', methods=['POST'])
def stop():
    try:
        data = request.get_json()
        username = data.get('username')

        if not username:
            return jsonify({'error': 'Username is required'}), 400

        # Stop container
        container = client.containers.get(f'n8n-{username}')
        container.stop()

        return jsonify({
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/deprovision', methods=['POST'])
def shutdown():
    try:
        data = request.get_json()
        username = data.get('username')

        if not username:
            return jsonify({'error': 'Username is required'}), 400

        # Stop and remove container
        container = client.containers.get(f'n8n-{username}')
        container.stop()
        container.remove()

        # Remove volume
        client.volumes.get(f'n8n_data_{username}').remove()

        return jsonify({
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/update', methods=['POST'])
def update():
    try:
        data = request.get_json()
        username = data.get('username')

        if not username:
            return jsonify({'error': 'Username is required'}), 400

        # Stop container
        container = client.containers.get(f'n8n-{username}')
        container.stop()

        # Pull latest image
        client.images.pull('5quidw4rd/n8n-custom-amd:latest')

        # Start container
        container.start()

        return jsonify({
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/update-all', methods=['POST'])
def update_all():
    try:
        # Stop all containers
        for container in client.containers.list():
            container.stop()

        # Pull latest image
        client.images.pull('5quidw4rd/n8n-custom-amd:latest')

        # Start all containers
        for container in client.containers.list():
            container.start()

        return jsonify({
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/provision-test-windows', methods=['POST'])
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
        
        def run_docker():
            os.system(f'docker volume create n8n_data_{username}')
            os.system(f'docker run --rm --name n8n-{username} -p {port}:5678 -v n8n_data_{username}:/home/node/.n8n 5quidw4rd/n8n-custom-amd:latest start --tunnel')

        thread = threading.Thread(target=run_docker)
        thread.daemon = True
        thread.start()

        return jsonify({
            'status': 'success',
            'url': f'http://localhost:{port}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/provision-test-mac', methods=['POST'])
def provision_user_test_mac():
    try:
        data = request.get_json()
        username = data.get('username')

        # check if username is being used
        if users_mono.find_one({'username': username}):
            return jsonify({'error': 'Username is already in use'}), 400
        
        if not username:
            return jsonify({'error': 'Username is required'}), 400

        # get a random unused port
        while True:
            port = random.randint(49152, 65535)  # Dynamic port range
            if not is_port_in_use(port):
                break

        # Create compose config
        compose_config = create_compose_config_mac(username, port)
        
        # Write compose file temporarily
        compose_file = f'/tmp/docker-compose-{username}.yaml'
        with open(compose_file, 'w') as f:
            yaml.dump(compose_config, f)

        # Use docker-compose programmatically
        os.system(f'docker compose -f {compose_file} -p n8n-{username} up -d')
        
        # Clean up
        os.remove(compose_file)

        # add to database with username, subdomain, port, container name
        users_mono.insert_one({
            'username': username,
            'subdomain': f'{username}.{domain}',
            'port': port,
            'container_name': f'n8n-{username}'
        })

        return jsonify({
            'status': 'success',
            'subdomain': f'{username}.{domain}'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def welcome():
    return 'Welcome to N8N Provisioning Service'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)