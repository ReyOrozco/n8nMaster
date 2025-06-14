# Kubernetes Deployment Guide for n8n Provisioning System

This guide will walk you through deploying the n8n provisioning system on a Kubernetes cluster.

## Prerequisites

1. **Kubernetes Cluster**: A running Kubernetes cluster (v1.19+)
2. **kubectl**: Configured and connected to your cluster
3. **Docker**: For building container images
4. **Container Registry**: Access to a container registry (Docker Hub, GCR, ECR, etc.)
5. **Domain**: A domain name with wildcard DNS setup for Cloudflare

## Step-by-Step Deployment

### 1. Prepare Your Environment

```bash
# Clone the repository and navigate to provision directory
cd /path/to/n8n-fork/provision

# Copy and customize environment file
cp .env.example .env
# Edit .env with your specific configuration
```

### 2. Configure Secrets

Edit `k8s-deployment.yaml` and update the following sections:

```yaml
# Update MongoDB connection string
stringData:
  MONGODB_URI: "your-mongodb-connection-string"
  DOMAIN_NAME: "your-domain.com"

# Update image reference
image: your-registry/n8n-provisioner:latest

# Update ingress hostname (if using)
- host: provision.your-domain.com
```

### 3. Configure Docker Registry

Edit `deploy.sh` and update:

```bash
REGISTRY="your-docker-registry.com"
```

### 4. Build and Deploy

#### Option A: Full Automated Deployment

```bash
# Make the deployment script executable
chmod +x deploy.sh

# Run full deployment
./deploy.sh deploy
```

#### Option B: Manual Step-by-Step

```bash
# 1. Build Docker image
./deploy.sh build

# 2. Push to registry
./deploy.sh push

# 3. Deploy to Kubernetes
kubectl apply -f k8s-deployment.yaml

# 4. Wait for deployment
kubectl wait --for=condition=available --timeout=300s deployment/n8n-provisioner -n n8n-provisioning
```

### 5. Verify Deployment

```bash
# Check deployment status
./deploy.sh status

# View logs
./deploy.sh logs

# Test the service
./deploy.sh test
```

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB connection string | Required |
| `DOMAIN_NAME` | Base domain for n8n instances | Required |
| `FLASK_ENV` | Flask environment | `production` |

### Resource Configuration

The deployment includes:
- **CPU**: 100m request, 500m limit
- **Memory**: 256Mi request, 512Mi limit
- **Replicas**: 2 (for high availability)

### Security Features

- Non-root container execution
- Security context with dropped capabilities
- Network policies (if supported)
- RBAC with minimal required permissions

## Accessing the Service

### Internal Access (from within cluster)

```
Service: n8n-provisioner-service.n8n-provisioning.svc.cluster.local
Port: 80
```

### External Access

#### Option 1: Port Forward (for testing)

```bash
kubectl port-forward service/n8n-provisioner-service 8080:80 -n n8n-provisioning
# Access at: http://localhost:8080
```

#### Option 2: Ingress (if configured)

```
https://provision.your-domain.com
```

#### Option 3: Cloudflare Tunnel (recommended)

Set up a Cloudflare tunnel pointing to the internal service.

## API Endpoints

- **Health Check**: `GET /health`
- **Provision User**: `POST /provision`
- **Deprovision User**: `POST /deprovision`

### Example API Usage

```bash
# Health check
curl https://provision.your-domain.com/health

# Provision a new user
curl -X POST https://provision.your-domain.com/provision \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser"}'

# Deprovision a user
curl -X POST https://provision.your-domain.com/deprovision \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser"}'
```

## Monitoring and Troubleshooting

### Check Pod Status

```bash
kubectl get pods -n n8n-provisioning
kubectl describe pod <pod-name> -n n8n-provisioning
```

### View Logs

```bash
kubectl logs -f deployment/n8n-provisioner -n n8n-provisioning
```

### Check Events

```bash
kubectl get events -n n8n-provisioning --sort-by='.lastTimestamp'
```

### Common Issues

1. **Pod CrashLoopBackOff**
   - Check logs for errors
   - Verify MongoDB connection
   - Check RBAC permissions

2. **Service Unreachable**
   - Verify service endpoints: `kubectl get endpoints -n n8n-provisioning`
   - Check network policies
   - Verify ingress configuration

3. **Permission Denied**
   - Check RBAC configuration
   - Verify service account binding

## Scaling and High Availability

### Horizontal Scaling

```bash
kubectl scale deployment n8n-provisioner --replicas=3 -n n8n-provisioning
```

### Resource Monitoring

```bash
# Check resource usage
kubectl top pods -n n8n-provisioning

# Set up resource alerts
kubectl apply -f monitoring/alerts.yaml
```

## Security Considerations

1. **Network Security**
   - Use network policies to restrict traffic
   - Enable TLS for all communications
   - Use service mesh for advanced security

2. **Secret Management**
   - Use Kubernetes secrets or external secret management
   - Rotate secrets regularly
   - Avoid hardcoding sensitive data

3. **RBAC**
   - Follow principle of least privilege
   - Regular RBAC audits
   - Use separate service accounts for different services

## Backup and Recovery

### Database Backup

Ensure your MongoDB cluster has proper backup procedures in place.

### Configuration Backup

```bash
# Backup Kubernetes manifests
kubectl get all -n n8n-provisioning -o yaml > backup-$(date +%Y%m%d).yaml
```

## Updates and Maintenance

### Rolling Updates

```bash
# Update to new version
./deploy.sh update
```

### Maintenance Mode

```bash
# Scale down for maintenance
kubectl scale deployment n8n-provisioner --replicas=0 -n n8n-provisioning

# Scale back up
kubectl scale deployment n8n-provisioner --replicas=2 -n n8n-provisioning
```

## Cleanup

To completely remove the deployment:

```bash
./deploy.sh cleanup
```

Or manually:

```bash
kubectl delete -f k8s-deployment.yaml
```

## Support and Troubleshooting

For issues with the deployment:

1. Check the logs: `./deploy.sh logs`
2. Verify cluster connectivity: `kubectl cluster-info`
3. Check resource availability: `kubectl top nodes`
4. Review the configuration files for typos or misconfigurations

## Next Steps

After successful deployment:

1. Set up monitoring and alerting
2. Configure backup procedures
3. Set up CI/CD pipelines for automated deployments
4. Implement additional security measures
5. Scale based on usage patterns
