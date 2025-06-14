from flask import Flask, request, jsonify
import yaml
import os
import random
import time
from kubernetes import client, config
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

app = Flask(__name__)

# Load Kubernetes config
try:
    config.load_incluster_config()  # For running inside cluster
except:
    config.load_kube_config()  # For local development

k8s_apps_v1 = client.AppsV1Api()
k8s_core_v1 = client.CoreV1Api()
# Removed k8s_networking_v1 since not using Ingress with Cloudflare

# MongoDB setup
uri = "mongodb+srv://akaneai420:ilovehentai321@cluster0.jwyab3g.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
mongo_client = MongoClient(uri, server_api=ServerApi('1'))
users_mono = mongo_client['n8n-fork']['users-monolith']

domain = os.getenv('DOMAIN_NAME', '173956.xyz')

def create_n8n_namespace(username):
    namespace = client.V1Namespace(
        metadata=client.V1ObjectMeta(name=f"n8n-{username}")
    )
    try:
        k8s_core_v1.create_namespace(namespace)
    except client.exceptions.ApiException as e:
        if e.status != 409:  # Ignore if namespace already exists
            raise

def create_n8n_deployment(username):
    deployment = client.V1Deployment(
        metadata=client.V1ObjectMeta(
            name=f"n8n-{username}",
            namespace=f"n8n-{username}"
        ),
        spec=client.V1DeploymentSpec(
            replicas=1,
            selector=client.V1LabelSelector(
                match_labels={"app": f"n8n-{username}"}
            ),
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(
                    labels={"app": f"n8n-{username}"}
                ),
                spec=client.V1PodSpec(
                    # Add init container to fix permissions
                    init_containers=[
                        client.V1Container(
                            name="fix-permissions",
                            image="busybox:1.35",
                            command=["sh", "-c"],
                            args=["chown -R 1000:1000 /home/node/.n8n && chmod -R 755 /home/node/.n8n"],
                            volume_mounts=[
                                client.V1VolumeMount(
                                    name="n8n-data",
                                    mount_path="/home/node/.n8n"
                                )
                            ],
                            security_context=client.V1SecurityContext(
                                run_as_user=0  # Run as root to fix permissions
                            )
                        )
                    ],
                    containers=[
                        client.V1Container(
                            name="n8n",
                            image="5quidw4rd/n8n-custom-amd:latest",
                            ports=[client.V1ContainerPort(container_port=5678)],
                            env=[
                                client.V1EnvVar(name="N8N_HOST", value=f"{username}.{domain}"),
                                client.V1EnvVar(name="N8N_PORT", value="5678"),
                                client.V1EnvVar(name="N8N_PROTOCOL", value="https"),
                                client.V1EnvVar(name="NODE_ENV", value="production"),
                                client.V1EnvVar(name="WEBHOOK_URL", value=f"https://{username}.{domain}/"),
                                client.V1EnvVar(name="GENERIC_TIMEZONE", value="Europe/Berlin")
                            ],
                            volume_mounts=[
                                client.V1VolumeMount(
                                    name="n8n-data",
                                    mount_path="/home/node/.n8n"
                                )
                            ],
                            # Add security context to run as node user
                            security_context=client.V1SecurityContext(
                                run_as_user=1000,
                                run_as_group=1000,
                                fs_group=1000
                            )
                        )
                    ],
                    volumes=[
                        client.V1Volume(
                            name="n8n-data",
                            persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                                claim_name=f"n8n-data-{username}"
                            )
                        )
                    ]
                )
            )
        )
    )
    
    return k8s_apps_v1.create_namespaced_deployment(
        namespace=f"n8n-{username}",
        body=deployment
    )

def create_n8n_service(username):
    service = client.V1Service(
        metadata=client.V1ObjectMeta(
            name=f"n8n-{username}",
            namespace=f"n8n-{username}"
        ),
        spec=client.V1ServiceSpec(
            type="NodePort",  # Expose via NodePort for Cloudflare to access
            selector={"app": f"n8n-{username}"},
            ports=[
                client.V1ServicePort(
                    port=80,
                    target_port=5678,
                    protocol="TCP"
                )
            ]
        )
    )
    
    return k8s_core_v1.create_namespaced_service(
        namespace=f"n8n-{username}",
        body=service
    )

def create_n8n_pvc(username):
    pvc = client.V1PersistentVolumeClaim(
        metadata=client.V1ObjectMeta(
            name=f"n8n-data-{username}",
            namespace=f"n8n-{username}"
        ),
        spec=client.V1PersistentVolumeClaimSpec(
            access_modes=["ReadWriteOnce"],
            resources=client.V1ResourceRequirements(
                requests={"storage": "1.5Gi"}
            )
        )
    )
    
    return k8s_core_v1.create_namespaced_persistent_volume_claim(
        namespace=f"n8n-{username}",
        body=pvc
    )

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Kubernetes probes."""
    try:
        # Test MongoDB connection
        users_mono.find_one({}, limit=1)
        
        # Test Kubernetes API connection
        k8s_core_v1.list_namespace(limit=1)
        
        return jsonify({
            'status': 'healthy',
            'timestamp': time.time(),
            'services': {
                'mongodb': 'connected',
                'kubernetes': 'connected'
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        }), 503

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

        # Create Kubernetes resources
        create_n8n_namespace(username)
        create_n8n_pvc(username)
        deployment = create_n8n_deployment(username)
        service = create_n8n_service(username)
        # Removed ingress creation since using Cloudflare proxy

        # Store in database
        users_mono.insert_one({
            'username': username,
            'subdomain': f'{username}.{domain}',
            'namespace': f'n8n-{username}',
            'deployment_type': 'kubernetes'
        })

        return jsonify({
            'status': 'success',
            'subdomain': f'{username}.{domain}',
            'namespace': f'n8n-{username}'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/deprovision', methods=['POST'])
def deprovision_user():
    try:
        data = request.get_json()
        username = data.get('username')

        if not username:
            return jsonify({'error': 'Username is required'}), 400

        # Delete namespace (this will delete all resources in it)
        k8s_core_v1.delete_namespace(name=f"n8n-{username}")

        # Remove from database
        users_mono.delete_one({'username': username})

        return jsonify({'status': 'success'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)