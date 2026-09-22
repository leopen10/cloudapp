#!/bin/bash
# user_data.sh.tpl — execute une seule fois au premier demarrage de l'instance (cloud-init).
# Installe Docker, active Swarm, recupere le depot et deploie la pile de production.
# Journal complet : /var/log/cloud-init-output.log (utile en cas de probleme).

set -euo pipefail
exec > >(tee /var/log/cloudapp-bootstrap.log) 2>&1

echo "=== CloudApp : demarrage du bootstrap $(date -u) ==="

# --- 1) Docker ---
apt-get update -y
curl -fsSL https://get.docker.com | sh
systemctl enable --now docker
usermod -aG docker ubuntu

# --- 2) Depot ---
apt-get install -y git
git clone https://github.com/${github_repo}.git /opt/cloudapp
cd /opt/cloudapp

# --- 3) Swarm + reseau ---
docker swarm init --advertise-addr "$(curl -s http://169.254.169.254/latest/meta-data/local-ipv4)"
docker network create --driver overlay --attachable traefik-public

# --- 4) Secrets de la session (jamais commites : fournis par Terraform) ---
export DOCKER_USERNAME='${docker_username}'
export IMAGE_TAG='latest'
export POSTGRES_PASSWORD='${postgres_password}'
export JWT_SECRET_KEY='${jwt_secret_key}'
export GRAFANA_ADMIN_PASSWORD='${grafana_admin_password}'
export RESEND_API_KEY='${resend_api_key}'

# --- 5) Deploiement ---
docker stack deploy -c docker-compose.prod.yml cloudapp --with-registry-auth

echo "=== CloudApp : bootstrap termine $(date -u) ==="
echo "Application disponible sur http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)/"