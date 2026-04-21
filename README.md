# CloudApp — Pipeline CI/CD Microservices Complet

Architecture microservices production-ready avec GitHub Actions, Traefik, Docker Swarm.

## Stack Technique
- **Backend** : FastAPI (Python 3.11)
- **Orchestration** : Docker Swarm
- **Reverse Proxy** : Traefik v2
- **CI/CD** : GitHub Actions (4 workflows)
- **Messaging** : Apache Kafka
- **Monitoring** : Prometheus + Grafana
- **Tracing** : Jaeger + OpenTelemetry
- **Sécurité** : Trivy, Pre-commit, Docker Secrets

## Services
| Service | Port | Description |
|---------|------|-------------|
| Gateway | 8000 | Point d'entrée unique |
| Auth | 8001 | Authentification |
| Project | 8002 | Gestion des projets |
| Billing | 8003 | Facturation |
| Notification | 8004 | Notifications email |
| Analytics | 8005 | Analytique |

## Auteur
Leonel-Magloire PENGOU — ESTIAM Paris Bac+3 Cybersécurité & Cloud