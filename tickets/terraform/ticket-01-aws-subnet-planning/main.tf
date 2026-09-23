terraform {
  required_version = ">= 1.5.0"
}

variable "vpc_cidr" {
  description = "CIDR block assigned to the AWS VPC"
  type        = string
  default     = "10.42.0.0/16"

  validation {
    condition     = can(cidrnetmask(var.vpc_cidr))
    error_message = "vpc_cidr must be a valid IPv4 CIDR block."
  }
}

locals {
  subnet_numbers = {
    public_az1  = 0
    public_az2  = 1
    private_az1 = 10
    private_az2 = 11
  }

  subnets = { for name, number in local.subnet_numbers :
  name => cidrsubnet(var.vpc_cidr, 8, number) }
}

output "subnets" {
  description = "Calculated public and private subnet CIDR blocks"
  value       = local.subnets
}