# secrets.tf
# Variables sensibles : jamais de valeur par defaut, jamais commitees. A fournir via
# un fichier terraform.tfvars local (ignore par Git, voir .gitignore) ou des
# variables d'environnement TF_VAR_xxx. Voir README.md pour la marche a suivre.

variable "postgres_password" {
  description = "Mot de passe PostgreSQL de production. Lettres et chiffres uniquement (utilise dans une URL de connexion)."
  type        = string
  sensitive   = true
}

variable "jwt_secret_key" {
  description = "Cle de signature des jetons JWT (connexions)."
  type        = string
  sensitive   = true
}

variable "grafana_admin_password" {
  description = "Mot de passe administrateur Grafana."
  type        = string
  sensitive   = true
}

variable "resend_api_key" {
  description = "Cle API Resend (envoi d'e-mails). Facultative : laisser vide desactive simplement l'envoi."
  type        = string
  sensitive   = true
  default     = ""
}