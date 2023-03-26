# output "db_address" {
#   description = "The address of the database."
#   value       = module.db.this_db_instance_address
# }

# output "db_port" {
#   description = "The port of the database service."
#   value       = module.db.this_db_instance_port
# }

output "db_security_group_id" {
  description = "The security group ID of the database service."
  value       = aws_security_group.rds.id
}