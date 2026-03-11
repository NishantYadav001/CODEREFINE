# CODEREFINE - CI/CD Pipeline Guide

## Table of Contents
1. [Overview](#overview)
2. [Pipeline Architecture](#pipeline-architecture)
3. [GitHub Actions Workflow](#github-actions-workflow)
4. [Azure DevOps Pipeline](#azure-devops-pipeline)
5. [Deployment Strategies](#deployment-strategies)
6. [Testing in Pipeline](#testing-in-pipeline)
7. [Security Scanning](#security-scanning)
8. [Monitoring & Alerts](#monitoring--alerts)

---

## Overview

CODEREFINE uses automated CI/CD pipelines to:
- Run automated tests on every commit
- Perform code quality checks
- Build Docker images
- Deploy to staging/production
- Monitor application health

### Pipeline Features
- ✅ Automatic testing on PR
- ✅ Code quality analysis
- ✅ Security scanning
- ✅ Docker image building
- ✅ Multi-environment deployment
- ✅ Automated rollback capability

---

## Pipeline Architecture

### High-Level Flow
```
Git Push/PR
    ↓
┌─────────── CI ────────────┐
│ - Code Checkout          │
│ - Install Dependencies   │
│ - Run Tests             │
│ - Code Quality Check    │
│ - Security Scan         │
│ - Build Docker Image    │
└────────────┬────────────┘
             ↓
    ┌────────────────┐
    │  Approval?     │
    └────────────────┘
             ↓
┌─────────── CD ────────────┐
│ - Push Docker Image      │
│ - Deploy to Staging      │
│ - Run Integration Tests  │
│ - Deploy to Production   │
│ - Health Checks          │
│ - Rollback if Failed     │
└────────────────────────┘
```

---

## GitHub Actions Workflow

### File: `.github/workflows/ci-cd.yml`

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  # TESTING JOB
  # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  test:
    name: Test & Code Quality
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11']
    
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'
      
      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r backend/requirements.txt
          pip install -r backend/requirements-dev.txt
      
      - name: Run Tests
        run: |
          pytest backend/ -v --cov=backend --cov-report=xml --cov-report=term
      
      - name: Upload Coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: unittests
          name: codecov-umbrella
      
      - name: Format Check (Black)
        run: black backend/ --check
      
      - name: Lint Check (Flake8)
        run: flake8 backend/ --count --statistics
      
      - name: Type Check (MyPy)
        run: mypy backend/ --ignore-missing-imports


  # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  # BUILD JOB
  # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  build:
    name: Build Docker Image
    runs-on: ubuntu-latest
    needs: test
    if: github.event_name == 'push' || github.event.pull_request.draft == false
    
    permissions:
      contents: read
      packages: write
    
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Log in to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract Metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha,prefix={{branch}}-
      
      - name: Build and Push Docker Image
        uses: docker/build-push-action@v4
        with:
          context: ./CODEREVGENAI
          push: ${{ github.event_name == 'push' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max


  # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  # SECURITY SCANNING JOB
  # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  security:
    name: Security Scanning
    runs-on: ubuntu-latest
    needs: test
    
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3
      
      - name: Dependency Check
        run: |
          pip install safety
          safety check --json
      
      - name: SAST Scan (Bandit)
        run: |
          pip install bandit
          bandit -r backend/ -f json -o bandit-report.json || true
      
      - name: Upload Bandit Report
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: bandit-report.json


  # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  # DEPLOY TO STAGING
  # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: [build, security]
    if: github.event_name == 'push' && github.ref == 'refs/heads/develop'
    environment: staging
    
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3
      
      - name: Deploy to Staging
        run: |
          echo "Deploying to staging..."
          # Add your staging deployment command
          # Example: kubectl apply -f k8s/staging/
      
      - name: Run Integration Tests
        run: |
          echo "Running integration tests..."
          # Add integration test commands


  # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  # DEPLOY TO PRODUCTION
  # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: deploy-staging
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    environment: production
    
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3
      
      - name: Deploy to Production
        run: |
          echo "Deploying to production..."
          # Add your production deployment command
      
      - name: Health Check
        run: |
          echo "Running health checks..."
          # Add health check commands
      
      - name: Notify Deployment
        run: |
          echo "Deployment successful!"
          # Send notification to Slack, Email, etc.
```

---

## Azure DevOps Pipeline

### File: `azure-pipelines.yml`

```yaml
trigger:
  branches:
    include:
    - main
    - develop
  paths:
    include:
    - CODEREVGENAI/*

pr:
  branches:
    include:
    - main
    - develop

pool:
  vmImage: 'ubuntu-latest'

variables:
  pythonVersion: '3.11'
  imageName: 'coderefine'
  dockerRegistryServiceConnection: 'DockerHub'
  imageRepository: 'your-org/coderefine'
  containerRegistry: 'yourregistry.azurecr.io'
  dockerfilePath: '$(Build.SourcesDirectory)/CODEREVGENAI/Dockerfile'
  tag: '$(Build.BuildId)'

stages:
  - stage: Test
    displayName: Test & Quality
    jobs:
      - job: TestJob
        displayName: Unit Tests & Code Quality
        steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '$(pythonVersion)'
            displayName: 'Use Python $(pythonVersion)'
          
          - script: |
              python -m pip install --upgrade pip
              pip install -r backend/requirements.txt
              pip install -r backend/requirements-dev.txt
            displayName: 'Install Dependencies'
          
          - script: |
              pytest backend/ -v --cov=backend --cov-report=xml --cov-report=term
            displayName: 'Run Tests'
          
          - task: PublishCodeCoverageResults@1
            inputs:
              codeCoverageTool: Cobertura
              summaryFileLocation: '$(System.DefaultWorkingDirectory)/**/coverage.xml'
            displayName: 'Publish Coverage'
          
          - script: |
              black backend/ --check
            displayName: 'Format Check'
          
          - script: |
              flake8 backend/ --count --statistics
            displayName: 'Lint Check'
  
  - stage: Build
    displayName: Build & Push Docker Image
    dependsOn: Test
    condition: succeeded()
    jobs:
      - job: BuildJob
        displayName: Build Docker Image
        steps:
          - task: Docker@2
            displayName: Build Docker Image
            inputs:
              command: build
              dockerfile: $(dockerfilePath)
              tags: |
                $(containerRegistry)/$(imageRepository):$(tag)
                $(containerRegistry)/$(imageRepository):latest
              arguments: '--build-arg BUILD_DATE=$(Build.BuildNumber)'
          
          - task: Docker@2
            displayName: Push to Registry
            inputs:
              command: push
              containerRegistry: $(dockerRegistryServiceConnection)
              repository: $(imageRepository)
              tags: |
                $(tag)
                latest
  
  - stage: SecurityScan
    displayName: Security Scanning
    dependsOn: Test
    condition: succeeded()
    jobs:
      - job: SecurityJob
        displayName: SAST & Dependency Check
        steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '$(pythonVersion)'
          
          - script: |
              pip install safety bandit
              safety check --json > safety-report.json || true
              bandit -r backend/ -f json -o bandit-report.json || true
            displayName: 'Run Security Scans'
          
          - task: PublishBuildArtifacts@1
            inputs:
              pathToPublish: 'safety-report.json'
              artifactName: 'security-reports'
  
  - stage: DeployStaging
    displayName: Deploy to Staging
    dependsOn: Build
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/develop'))
    jobs:
      - deployment: DeployStaging
        displayName: Deploy to Staging
        environment: Staging
        strategy:
          runOnce:
            deploy:
              steps:
                - script: |
                    echo "Deploying to staging..."
                  displayName: 'Deploy'
  
  - stage: DeployProduction
    displayName: Deploy to Production
    dependsOn: DeployStaging
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
    jobs:
      - deployment: DeployProduction
        displayName: Deploy to Production
        environment: Production
        strategy:
          runOnce:
            deploy:
              steps:
                - script: |
                    echo "Deploying to production..."
                  displayName: 'Deploy'
```

---

## Deployment Strategies

### Blue-Green Deployment
```yaml
deploy:
  strategy:
    type: BlueGreen
    blueGreenConfig:
      terminateBlueInstancesOnDeploymentSuccess:
        action: KEEP_ALIVE
      deploymentReadyOption:
        actionOnTimeout: CONTINUE_DEPLOYMENT
      greenFleetProvisioningOption:
        action: COPY_AUTO_SCALING_GROUP
```

### Canary Deployment
```yaml
deploy:
  strategy:
    type: Canary
    canaryConfig:
      increments: [10, 50, 100]
      interval: 5    # minutes
      onFailure: ROLLBACK
```

### Rolling Deployment
```yaml
deploy:
  strategy:
    type: Rolling
    rollingStrategy:
      maxUnavailable: 1
      maxSurge: 1
```

---

## Testing in Pipeline

### Unit Tests
```bash
pytest backend/ -v --cov=backend --cov-report=html
```

### Integration Tests
```bash
# Test against staging database
pytest backend/tests/integration/ -v --db=staging
```

### Performance Tests
```bash
# Load testing
locust -f backend/tests/load/locustfile.py
```

### Security Tests
```bash
# SAST scanning
bandit -r backend/

# Dependency checking
safety check

# Container scanning
trivy image ghcr.io/coderefine:latest
```

---

## Security Scanning

### SAST (Static Application Security Testing)
```bash
bandit -r backend/ -f json -o bandit-report.json
```

### Dependency Scanning
```bash
pip install safety
safety check --json
```

### Container Vulnerability Scanning
```bash
trivy image --format json ghcr.io/coderefine:latest
aqua trivy image ghcr.io/coderefine:latest
```

### Secret Scanning
- GitHub automatically scans for secrets
- GitGuardian integration for advanced detection
- Pre-commit hooks to prevent secret commits

---

## Monitoring & Alerts

### Pipeline Notifications
- Slack notifications on build failure
- Email notifications to team
- GitHub Status checks on PR

### Deployment Notifications
```yaml
- name: Notify Slack
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "Deployment complete: ${{ job.status }}"
      }
```

### Health Checks
```bash
# Verify application is running
curl -f http://app:8000/api/health || exit 1
```

---

## Setting Up CI/CD

### GitHub Actions Setup
1. Create `.github/workflows/ci-cd.yml`
2. Add secrets in Settings → Secrets
   - `DOCKER_TOKEN`
   - `GROQ_API_KEY`
   - etc.
3. Push to trigger workflow

### Azure DevOps Setup
1. Create `azure-pipelines.yml` in root
2. Create pipeline in Azure DevOps
3. Configure environment variables
4. Set approvers for production deployment

---

## Troubleshooting Pipeline

### Build Failures
- Check logs in GitHub Actions / Azure DevOps
- Verify dependencies are installed
- Check environment variables are set
- Ensure Docker daemon is running

### Test Failures
- Run tests locally first: `pytest backend/ -v`
- Check database connection in pipeline
- Verify test data is initialized
- Review test output in pipeline logs

### Deployment Failures
- Verify credentials are correct
- Check resource availability
- Review deployment logs
- Perform manual rollback if needed

---

**Document Version**: 2.0.0
**Last Updated**: February 2026
