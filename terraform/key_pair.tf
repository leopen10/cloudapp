# key_pair.tf
# Importe une cle SSH LOCALE existante : Terraform ne genere ni ne stocke jamais
# de cle privee. Generez la paire au prealable si necessaire :
#   ssh-keygen -t ed25519 -f ~/.ssh/cloudapp -C "cloudapp-demo"
# puis pointez ssh_public_key_path vers le fichier .pub correspondant.

resource "aws_key_pair" "cloudapp" {
  key_name   = "cloudapp-${var.environment}"
  public_key = file(var.ssh_public_key_path)
}