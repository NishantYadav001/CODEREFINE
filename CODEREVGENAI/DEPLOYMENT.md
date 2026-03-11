# CODEREFINE - Deployment Guide

## Table of Contents
1. [Quick Start](#quick-start)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Production Checklist](#production-checklist)
5. [Monitoring & Maintenance](#monitoring--maintenance)
6. [Rollback Procedures](#rollback-procedures)

---

## Quick Start

### Docker (Local/Dev)
```bash
cd CODEREVGENAI
docker-compose up --build
# Application: http://localhost:8000
```

### Docker (Production)
```bash
docker build -t coderefine:latest .
docker run -d \
  --name coderefine \
  -p 8000:8000 \
  --env-file .env \
  coderefine:latest
```

---

## Docker Deployment

### Building Image
```bash
docker build -t your-registry/coderefine:2.0.0 .
docker tag your-registry/coderefine:2.0.0 your-registry/coderefine:latest
docker push your-registry/coderefine:2.0.0
docker push your-registry/coderefine:latest
```

### Running Container
```bash
docker run -d \
  --name coderefine \
  -p 8000:8000 \
  -e GROQ_API_KEY=your_key \
  -e DB_HOST=your_db_host \
  -e SECRET_KEY=your_secret_key \
  your-registry/coderefine:latest
```

### Health Check
```bash
curl http://localhost:8000/api/health
```

---

## Cloud Deployment

### Azure Container Apps
```bash
# Login to Azure
az login
az account set --subscription YOUR_SUBSCRIPTION_ID

# Create resource group
az group create \
  --name coderefine-rg \
  --location eastus

# Create container app
az containerapp create \
  --resource-group coderefine-rg \
  --name coderefine \
  --image your-registry.azurecr.io/coderefine:latest \
  --target-port 8000 \
  --environment coderefine-env \
  --registry-login-server your-registry.azurecr.io \
  --registry-username your-username \
  --registry-password your-password \
  --environment-variables \
    GROQ_API_KEY=your_key \
    DB_HOST=your_db_host \
    SECRET_KEY=your_secret_key
```

### Azure App Service
```bash
# Create app service
az appservice plan create \
  --name coderefine-plan \
  --resource-group coderefine-rg \
  --sku B1 \
  --is-linux

az webapp create \
  --resource-group coderefine-rg \
  --plan coderefine-plan \
  --name coderefine-app \
  --deployment-container-image-name \
    your-registry.azurecr.io/coderefine:latest
```

### Kubernetes (AKS)
```bash
# Create AKS cluster
az aks create \
  --resource-group coderefine-rg \
  --name coderefine-aks \
  --node-count 2

# Get credentials
az aks get-credentials \
  --resource-group coderefine-rg \
  --name coderefine-aks

# Deploy with kubectl
kubectl apply -f k8s/deployment.yaml
```

---

## Production Checklist

### Security
- [ ] Set strong `SECRET_KEY` (32+ characters)
- [ ] Set strong `APP_ENCRYPTION_KEY`
- [ ] Rotate `ADMIN_PASSWORD`
- [ ] Enable HTTPS/TLS
- [ ] Configure CORS properly
- [ ] Setup WAF (Web Application Firewall)
- [ ] Enable audit logging
- [ ] Backup encryption keys

### Database
- [ ] Create database backups
- [ ] Configure automatic backups
- [ ] Test backup restoration
- [ ] Setup database monitoring
- [ ] Enable slow query logging
- [ ] Optimize indexes

### Application
- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=false`
- [ ] Configure sentry (error tracking)
- [ ] Setup application monitoring
- [ ] Configure logging
- [ ] Setup health checks

### Infrastructure
- [ ] Configure load balancer
- [ ] Setup auto-scaling
- [ ] Configure DNS
- [ ] Setup CDN for static assets
- [ ] Configure firewall rules
- [ ] Setup VPN/bastion host

### Testing
- [ ] Run smoke tests
- [ ] Test all API endpoints
- [ ] Test database connectivity
- [ ] Test API key rotation
- [ ] Test backup/restore
- [ ] Load test application

---

## Monitoring & Maintenance

### Health Monitoring
```bash
# Check application health
curl -i http://localhost:8000/api/health

# Check database connection
curl http://localhost:8000/api/health/db

# View logs
docker logs coderefine
```

### Performance Monitoring
```bash
# Monitor memory
docker stats coderefine

# Monitor requests
tail -f /var/log/coderefine/access.log
```

### Backup & Restore

**Backup Database**:
```bash
mysqldump -u user -p database > backup.sql
```

**Restore Database**:
```bash
mysql -u user -p database < backup.sql
```

---

## Rollback Procedures

### Azure Container Apps
```bash
# List revisions
az containerapp revision list \
  --resource-group coderefine-rg \
  --name coderefine

# Deploy previous version
az containerapp update \
  --resource-group coderefine-rg \
  --name coderefine \
  --image previous-version:tag
```

### Docker Rollback
```bash
# Stop current container
docker stop coderefine

# Run previous version
docker run -d \
  --name coderefine \
  -p 8000:8000 \
  --env-file .env \
  coderefine:previous-version
```

---

See [CI-CD.md](CI-CD.md) for automated deployment pipelines.
