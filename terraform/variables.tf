variable "project" {
  type    = string
  default = "stocktrading"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "location" {
  type    = string
  default = "eu-central-1"
}

variable "db_name" {
  description = "The name of the database to create."
  type        = string
  default     = "stocktrading"
}

variable "db_username" {
  description = "The administrator username for the database."
  type        = string
  default     = "user"
}

variable "db_password" {
  description = "The password for the administrator user of the database."
  type        = string
  default     = "password"
}

variable "db_port" {
  description = "The port for database service."
  type        = number
  default     = 3306
}