# Simple DigitalOcean Kubernetes Deployment

## Prerequisites
- DigitalOcean Kubernetes cluster
- `kubectl` configured for your cluster
- Docker Hub account (or any container registry)

## 3-Step Deployment

### Step 1: Build and push image
```bash
# Build
docker build -f Dockerfile.k8s -t your-dockerhub-username/n8n-provisioner:latest .

# Push
docker push your-dockerhub-username/n8n-provisioner:latest
```

### Step 2: Update the manifest
Edit `simple-k8s.yaml`:
- Replace `your-registry/n8n-provisioner:latest` with your actual image
- Update MongoDB URI if needed
- Update domain if needed

### Step 3: Deploy
```bash
kubectl apply -f simple-k8s.yaml
```

## Check status
```bash
# See all resources
kubectl get all -n n8n-provisioning

# Get external IP (from LoadBalancer)
kubectl get service n8n-provisioner -n n8n-provisioning

# Check logs
kubectl logs -f deployment/n8n-provisioner -n n8n-provisioning
```

## Test the API
```bash
# Health check
curl http://EXTERNAL-IP/health

# Provision user
curl -X POST http://EXTERNAL-IP/provision \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser"}'
```

## Connect to Cloudflare
Point your DNS to the LoadBalancer external IP that DigitalOcean provides.

## Cleanup
```bash
kubectl delete -f simple-k8s.yaml
```

That's it! 🚀
