# budget.tf
# Alerte de facturation : ce projet a deja genere des couts AWS imprevus par le passe
# (instance EC2 oubliee allumee, voir historique du depot). Cette alerte email se
# declenche a 80 % et 100 % du plafond, sans cout (AWS Budgets est gratuit jusqu'a
# plusieurs dizaines d'alertes).
#
# Ce budget suit TOUT le compte AWS (pas seulement cloudapp), ce qui convient a un
# compte personnel/etudiant dedie a ce projet. Pour filtrer sur le seul tag Project=cloudapp
# (utile si le compte est partage avec d'autres projets), ajouter :
#   cost_filter {
#     name   = "TagKeyValue"
#     values = ["user:Project$cloudapp"]
#   }
# ATTENTION : ce filtre exige d'abord d'activer la balise "Project" comme balise de
# repartition des couts dans AWS Billing > Cost allocation tags, ce qui prend jusqu'a
# 24 h pour devenir actif. Sans cette activation, le filtre ne remonte aucune donnee.

resource "aws_budgets_budget" "monthly" {
  name         = "cloudapp-${var.environment}-mensuel"
  budget_type  = "COST"
  limit_amount = tostring(var.monthly_budget_usd)
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type              = "PERCENTAGE"
    notification_type           = "ACTUAL"
    subscriber_email_addresses  = [var.budget_alert_email]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 100
    threshold_type              = "PERCENTAGE"
    notification_type           = "ACTUAL"
    subscriber_email_addresses  = [var.budget_alert_email]
  }
}