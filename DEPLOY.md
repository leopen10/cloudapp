# Premier deploiement

Deux façons de déployer CloudApp : localement (Docker Swarm sur votre poste), ou sur
un serveur réel (AWS EC2 via Terraform). Les deux utilisent le même
`docker-compose.prod.yml` et les mêmes images publiées sur Docker Hub.

## Option A — Local, avec Docker Swarm (validation avant tout déploiement réel)

Prérequis : Docker Desktop, mode Swarm activable.

```powershell
docker swarm init
docker network create --driver overlay --attachable traefik-public

$env:DOCKER_USERNAME = "leonelpengou10"
$env:POSTGRES_PASSWORD = "<mot_de_passe>"
$env:JWT_SECRET_KEY = "<cle_aleatoire>"
$env:GRAFANA_ADMIN_PASSWORD = "<mot_de_passe>"
$env:RESEND_API_KEY = "<cle_resend_ou_vide>"

docker stack deploy -c docker-compose.prod.yml cloudapp
```

Un script automatise ce déploiement et le vérifie de bout en bout (services prêts,
accès via Traefik, inscription, sauvegarde PostgreSQL et sa restauration, traçage
distribué, Grafana, Prometheus) :

```powershell
powershell -ExecutionPolicy Bypass -File scripts\swarm-local-test.ps1
```

Arrêt propre :
```powershell
powershell -ExecutionPolicy Bypass -File scripts\swarm-local-test.ps1 -Down
```

## Option B — Serveur réel (AWS EC2), via Terraform

Voir [`terraform/README.md`](terraform/README.md) pour la marche à suivre complète :
création de l'instance, IP fixe, Security Group restreint, alerte de budget, puis
`terraform destroy` en fin de session pour éviter toute facturation continue.

Résumé :
```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Éditer terraform.tfvars : IP SSH, clé publique, mots de passe, e-mail d'alerte.
terraform init
terraform plan
terraform apply
```

## Chaîne CI/CD

Un déploiement en production ne se fait normalement pas à la main : le workflow
`cd-deploy.yml` (déclenchement manuel depuis l'onglet Actions de GitHub) se connecte
en SSH au serveur, met à jour le dépôt et relance `docker stack deploy` avec les
images les plus récentes. Voir le README principal, section CI/CD, pour le détail
des quatre workflows.
