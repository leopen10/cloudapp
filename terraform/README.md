\# Terraform — CloudApp sur AWS EC2



Deploiement reproductible de la pile de production (`docker-compose.prod.yml`) sur une

instance AWS EC2, pensee pour une \*\*session de demonstration courte\*\* (1 a 2 h), avec

destruction complete a la fin pour eviter toute facturation continue — le meme incident

(instance oubliee allumee, facturee plusieurs semaines) qui a motive ce module ne doit

plus se reproduire.



\## Ce que ce module cree



| Ressource | Role |

|---|---|

| `aws\_instance` | Une instance EC2 (Ubuntu 24.04, t3.small par defaut) |

| `aws\_eip` | Une IP publique fixe (sans elle, l'adresse change a chaque redemarrage) |

| `aws\_security\_group` | SSH limite a une seule IP, HTTP (80) ouvert, tout le reste ferme |

| `aws\_key\_pair` | Import d'une cle SSH \*\*existante\*\* (aucune cle n'est generee ni stockee par Terraform) |

| `aws\_budgets\_budget` | Alerte e-mail a 80 % et 100 % d'un plafond mensuel |



Au premier demarrage, l'instance installe Docker, active Swarm, clone le depot et lance

`docker stack deploy` automatiquement (voir `templates/user\_data.sh.tpl`) — aucune

commande manuelle a taper une fois `terraform apply` termine.



\## Prerequis



1\. Un compte AWS avec des identifiants configures (`aws configure`, ou variables

&#x20;  `AWS\_ACCESS\_KEY\_ID` / `AWS\_SECRET\_ACCESS\_KEY`).

2\. \[Terraform](https://developer.hashicorp.com/terraform/install) >= 1.6.

3\. Une paire de cles SSH locale :

```bash

&#x20;  ssh-keygen -t ed25519 -f \~/.ssh/cloudapp -C "cloudapp-demo"

```

4\. Votre adresse IP publique, pour restreindre le SSH :

```bash

&#x20;  curl https://checkip.amazonaws.com

```



\## Utilisation



```bash

cd terraform

cp terraform.tfvars.example terraform.tfvars

\# Editez terraform.tfvars : IP SSH, chemin de la cle, mots de passe, e-mail d'alerte.



terraform init

terraform plan      # verifie ce qui va etre cree, sans rien modifier

terraform apply     # tape "yes" pour confirmer

```



A la fin (2 a 3 minutes pour l'instance, puis 3 a 5 minutes pour le demarrage de la

pile), Terraform affiche l'URL de l'application et la commande SSH :



```bash

terraform output

```



Verification que tout fonctionne :

```bash

curl http://$(terraform output -raw public\_ip)/api/

```



\## Fin de la session : destruction



\*\*Essentiel pour eviter toute facturation continue.\*\*



```bash

terraform destroy

```



Confirmez avec `yes`. Toutes les ressources (instance, IP, groupe de securite, alerte

de budget) sont supprimees. Le volume EBS, attache a l'instance, est supprime avec elle.



\## Secrets



Aucun secret n'est ecrit dans les fichiers `.tf` : ils sont lus depuis `terraform.tfvars`

(ignore par Git) au moment de l'execution. Le fichier d'etat Terraform (`terraform.tfstate`)

contient neanmoins ces secrets en clair une fois appliques — il est lui aussi ignore par

Git (voir `.gitignore`). Pour un usage en equipe, deplacer cet etat vers un backend

distant chiffre (S3 + KMS) plutot que de le garder en local (voir le bloc commente dans

`versions.tf`).



\## Limites assumees



\- Noeud Swarm unique : pas de haute disponibilite (coherent avec `docker-compose.prod.yml`).

\- Pas de nom de domaine ni de HTTPS (necessiterait un domaine et Let's Encrypt via Traefik).

\- L'alerte de budget suit tout le compte AWS, pas seulement ce projet (voir le

&#x20; commentaire dans `budget.tf` pour la restreindre par tag).

\- L'IP publique change si l'instance est detruite puis recreee (l'IP elastique n'a de

&#x20; sens que le temps d'une session ; elle est detruite avec le reste).

