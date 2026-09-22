# variables.tf
# Tous les parametres du deploiement. Les valeurs par defaut visent une demonstration
# courte (quelques heures) sur le Free Tier AWS, avec une instance detruite ensuite
# (voir README.md : "terraform destroy" en fin de session).

variable "aws_region" {
  description = "Region AWS de deploiement."
  type        = string
  default     = "eu-west-3" # Paris
}

variable "environment" {
  description = "Nom de l'environnement (utilise dans les tags et le nom de l'instance)."
  type        = string
  default     = "demo"
}

variable "instance_type" {
  description = "Type d'instance EC2. t3.small minimum : la pile complete (13 services) depasse 1,5 Go de RAM utilisee, t3.micro (1 Go) est insuffisant."
  type        = string
  default     = "t3.small"

  validation {
    condition     = can(regex("^t3\\.", var.instance_type))
    error_message = "Utilisez une instance de la famille t3 (Free Tier / cout maitrise)."
  }
}

variable "root_volume_gb" {
  description = "Taille du volume racine (Go). 8 Go a sature un depot ESTIAM anterieur (voir Rendu 04) ; 20 Go donne de la marge."
  type        = number
  default     = 20
}

variable "ssh_allowed_cidr" {
  description = "Plage IP autorisee a se connecter en SSH (port 22). Ne JAMAIS laisser a 0.0.0.0/0 : cela expose le serveur a tout Internet."
  type        = string

  validation {
    condition     = var.ssh_allowed_cidr != "0.0.0.0/0"
    error_message = "ssh_allowed_cidr ne doit pas etre 0.0.0.0/0. Indiquez votre IP publique suivie de /32 (ex: 203.0.113.42/32)."
  }
}

variable "ssh_public_key_path" {
  description = "Chemin local de la cle publique SSH a installer sur l'instance (ex: ~/.ssh/id_ed25519.pub). Generez-la avec : ssh-keygen -t ed25519"
  type        = string
}

variable "docker_username" {
  description = "Compte Docker Hub publiant les images (leonelpengou10)."
  type        = string
  default     = "leonelpengou10"
}

variable "monthly_budget_usd" {
  description = "Plafond d'alerte de facturation mensuelle AWS, en dollars. Une alerte est envoyee par e-mail a 80 % et 100 % de ce montant."
  type        = number
  default     = 5
}

variable "budget_alert_email" {
  description = "Adresse e-mail recevant les alertes de budget AWS."
  type        = string
}