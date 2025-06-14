#!/bin/bash

# Deployment script for n8n Kubernetes provisioning system
# Usage: ./deploy.sh [build|deploy|update|status|logs|cleanup]

set -e

# Configuration
REGISTRY="your-docker-registry.com"  # Replace with your registry
IMAGE_NAME="n8n-provisioner"
IMAGE_TAG="latest"
FULL_IMAGE="${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
NAMESPACE="n8n-provisioning"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        error "kubectl is not installed or not in PATH"
    fi
    
    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        error "docker is not installed or not in PATH"
    fi
    
    # Check if cluster is accessible
    if ! kubectl cluster-info &> /dev/null; then
        error "Cannot access Kubernetes cluster. Please check your kubeconfig"
    fi
    
    success "Prerequisites check passed"
}

build_image() {
    log "Building Docker image..."
    
    # Build the image
    docker build -f Dockerfile.k8s -t "${FULL_IMAGE}" .
    
    success "Docker image built: ${FULL_IMAGE}"
}

push_image() {
    log "Pushing Docker image to registry..."
    
    # Push the image
    docker push "${FULL_IMAGE}"
    
    success "Docker image pushed: ${FULL_IMAGE}"
}

update_manifest() {
    log "Updating Kubernetes manifest with image..."
    
    # Update the image in the deployment manifest
    sed -i.bak "s|image: your-registry/n8n-provisioner:latest|image: ${FULL_IMAGE}|g" k8s-deployment.yaml
    
    success "Manifest updated with image: ${FULL_IMAGE}"
}

deploy_to_kubernetes() {
    log "Deploying to Kubernetes..."
    
    # Apply the manifests
    kubectl apply -f k8s-deployment.yaml
    
    # Wait for deployment to be ready
    log "Waiting for deployment to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/n8n-provisioner -n "${NAMESPACE}"
    
    success "Deployment completed successfully"
}

show_status() {
    log "Checking deployment status..."
    
    echo
    echo "=== Namespace ==="
    kubectl get namespace "${NAMESPACE}" 2>/dev/null || echo "Namespace not found"
    
    echo
    echo "=== Deployment ==="
    kubectl get deployment -n "${NAMESPACE}" 2>/dev/null || echo "No deployments found"
    
    echo
    echo "=== Pods ==="
    kubectl get pods -n "${NAMESPACE}" 2>/dev/null || echo "No pods found"
    
    echo
    echo "=== Services ==="
    kubectl get service -n "${NAMESPACE}" 2>/dev/null || echo "No services found"
    
    echo
    echo "=== Recent Events ==="
    kubectl get events -n "${NAMESPACE}" --sort-by='.lastTimestamp' | tail -10 2>/dev/null || echo "No events found"
}

show_logs() {
    log "Showing application logs..."
    
    # Get the first pod name
    POD_NAME=$(kubectl get pods -n "${NAMESPACE}" -l app=n8n-provisioner -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    
    if [ -z "$POD_NAME" ]; then
        error "No pods found for n8n-provisioner"
    fi
    
    echo "Logs from pod: $POD_NAME"
    echo "================================"
    kubectl logs -n "${NAMESPACE}" "$POD_NAME" --tail=100 -f
}

cleanup() {
    log "Cleaning up deployment..."
    
    warning "This will delete the entire n8n-provisioning deployment!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kubectl delete -f k8s-deployment.yaml --ignore-not-found=true
        success "Cleanup completed"
    else
        log "Cleanup cancelled"
    fi
}

test_deployment() {
    log "Testing deployment..."
    
    # Get service endpoint
    SERVICE_IP=$(kubectl get service n8n-provisioner-service -n "${NAMESPACE}" -o jsonpath='{.spec.clusterIP}' 2>/dev/null)
    
    if [ -z "$SERVICE_IP" ]; then
        error "Service not found or not ready"
    fi
    
    # Port forward for testing
    log "Setting up port forward for testing..."
    kubectl port-forward service/n8n-provisioner-service 8080:80 -n "${NAMESPACE}" &
    PF_PID=$!
    
    # Wait a moment for port forward to establish
    sleep 3
    
    # Test health endpoint
    log "Testing health endpoint..."
    if curl -f http://localhost:8080/health &>/dev/null; then
        success "Health check passed"
    else
        warning "Health check failed - service may still be starting"
    fi
    
    # Clean up port forward
    kill $PF_PID 2>/dev/null || true
    
    success "Test completed"
}

print_access_info() {
    log "Access Information:"
    
    echo
    echo "Internal cluster access:"
    echo "  Service: n8n-provisioner-service.${NAMESPACE}.svc.cluster.local"
    echo "  Port: 80"
    echo
    echo "To access from outside the cluster:"
    echo "  kubectl port-forward service/n8n-provisioner-service 8080:80 -n ${NAMESPACE}"
    echo "  Then access: http://localhost:8080"
    echo
    echo "API Endpoints:"
    echo "  Health: GET /health"
    echo "  Provision: POST /provision"
    echo "  Deprovision: POST /deprovision"
}

# Main script logic
case "${1:-help}" in
    "build")
        check_prerequisites
        build_image
        success "Build completed"
        ;;
    "push")
        check_prerequisites
        push_image
        success "Push completed"
        ;;
    "deploy")
        check_prerequisites
        build_image
        push_image
        update_manifest
        deploy_to_kubernetes
        test_deployment
        print_access_info
        success "Full deployment completed"
        ;;
    "update")
        check_prerequisites
        build_image
        push_image
        update_manifest
        kubectl rollout restart deployment/n8n-provisioner -n "${NAMESPACE}"
        kubectl wait --for=condition=available --timeout=300s deployment/n8n-provisioner -n "${NAMESPACE}"
        success "Update completed"
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs
        ;;
    "test")
        test_deployment
        ;;
    "cleanup")
        cleanup
        ;;
    "help"|*)
        echo "n8n Kubernetes Provisioning System Deployment Script"
        echo
        echo "Usage: $0 [command]"
        echo
        echo "Commands:"
        echo "  build      - Build Docker image only"
        echo "  push       - Push Docker image to registry"
        echo "  deploy     - Full deployment (build + push + deploy + test)"
        echo "  update     - Update existing deployment"
        echo "  status     - Show deployment status"
        echo "  logs       - Show application logs"
        echo "  test       - Test the deployment"
        echo "  cleanup    - Remove deployment"
        echo "  help       - Show this help"
        echo
        echo "Before deployment:"
        echo "1. Update REGISTRY variable in this script"
        echo "2. Update k8s-deployment.yaml with your domain and secrets"
        echo "3. Ensure your Kubernetes cluster is accessible"
        ;;
esac
