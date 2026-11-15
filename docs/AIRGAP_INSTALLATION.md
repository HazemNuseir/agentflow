# Air-Gapped Installation & Deployment Guide

## 1. Principle of Operation
DME AgentFlow is designed from first principles to operate in completely disconnected, top-secret, or air-gapped environments without any access to the public Internet.

## 2. Preparation (Online Machine)
1. Download the release bundle: `agentflow-release-v1.0.tar.gz`.
2. Download pre-quantized Gemma 4 GGUF weights to `./models/`.
3. Export Docker images (if deploying via containerization):
   ```bash
   docker save -o agentflow-images.tar \
     dme/agentflow-api:latest \
     dme/agentflow-web:latest \
     pgvector/pgvector:pg16 \
     redis:7-alpine
   ```

## 3. Installation (Air-Gapped Machine)
1. Mount the encrypted transfer media.
2. Unpack files to the designated target directory:
   ```bash
   tar -xzf agentflow-release-v1.0.tar.gz -C /opt/dme/agentflow
   ```
3. Copy GGUF weights into `/opt/dme/agentflow/models/`.
4. Ensure `.env` is configured with `DEPLOYMENT_PROFILE=FULLY_PRIVATE_AIRGAPPED`.
5. Start services via Docker Compose or systemd:
   ```bash
   docker compose -f docker-compose.yml up -d
   ```
6. Verify deployment by querying the local health endpoint:
   ```bash
   curl -s http://localhost:8000/health | grep healthy
   ```
