# outputs.tf

output "instance_id" {
  description = "Identifiant de l'instance EC2."
  value       = aws_instance.cloudapp.id
}

output "public_ip" {
  description = "Adresse IP publique fixe (Elastic IP)."
  value       = aws_eip.cloudapp.public_ip
}

output "application_url" {
  description = "URL de l'application."
  value       = "http://${aws_eip.cloudapp.public_ip}/"
}

output "ssh_command" {
  description = "Commande de connexion SSH."
  value       = "ssh -i <votre_cle_privee> ubuntu@${aws_eip.cloudapp.public_ip}"
}