variable "region" {
  type = string
}

variable "name" {
  type = string
}

variable "continent" {
  type = string
}

variable "domain_name" {
  type = string
}

variable "default_record" {
  type    = bool
  default = false
}

variable "records" {
  type = list(string)
}