#!/bin/bash

# Quick verification script for deployment readiness
# Run this before deploying to catch common issues

echo "🔍 Pre-deployment Verification"
echo "=============================="

# Check if required files exist
echo
echo "📁 Checking required files..."
files=(
    "provision_distributed.py"
    "requirements.txt" 
    "Dockerfile.k8s"
    "k8s-deployment.yaml"
    "deploy.sh"
)

for file in "${files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "✅ $file"
    else
        echo "❌ $file (missing)"
        exit 1
    fi
done

# Check if kubectl is configured
echo
echo "🔧 Checking kubectl configuration..."
if kubectl cluster-info &>/dev/null; then
    echo "✅ kubectl configured and cluster accessible"
    kubectl get nodes --no-headers | wc -l | xargs echo "📊 Cluster has" "nodes"
else
    echo "❌ kubectl not configured or cluster not accessible"
    exit 1
fi

# Check if docker is available
echo
echo "🐳 Checking Docker..."
if docker info &>/dev/null; then
    echo "✅ Docker is running"
else
    echo "❌ Docker is not running or not accessible"
    exit 1
fi

# Check Python dependencies
echo
echo "🐍 Checking Python dependencies..."
if python3 -c "import flask, kubernetes, pymongo, yaml" &>/dev/null; then
    echo "✅ Python dependencies available"
else
    echo "⚠️  Some Python dependencies missing (will be installed in container)"
fi

# Validate Kubernetes manifest
echo
echo "📋 Validating Kubernetes manifest..."
if kubectl apply --dry-run=client -f k8s-deployment.yaml &>/dev/null; then
    echo "✅ Kubernetes manifest is valid"
else
    echo "❌ Kubernetes manifest has errors"
    kubectl apply --dry-run=client -f k8s-deployment.yaml
    exit 1
fi

# Check if namespace will be created or already exists
if kubectl get namespace n8n-provisioning &>/dev/null; then
    echo "⚠️  Namespace 'n8n-provisioning' already exists"
else
    echo "✅ Namespace 'n8n-provisioning' will be created"
fi

echo
echo "🎉 Pre-deployment verification completed successfully!"
echo
echo "Next steps:"
echo "1. Update registry in deploy.sh: REGISTRY=\"your-registry.com\""
echo "2. Update secrets in k8s-deployment.yaml"
echo "3. Run: ./deploy.sh deploy"
