variable "domain_name" {
  type    = string
}

variable "name" {
  default = "geofile"
}

variable "asia" {
  type = map(any)

  default = {
    region    = "ap-northeast-1"
    continent = "AS"
  }
}

variable "usa" {
  type = map(any)

  default = {
    region    = "us-east-1"
    continent = "NA"
  }
}

variable "europe" {
  type = map(any)

  default = {
    region    = "eu-central-1"
    continent = "EU"
  }
}
