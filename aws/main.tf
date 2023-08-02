# --------------------------------------------------------------------------------------------------------
# Europe
module "europe_ec2server" {
  source = "./modules/ec2server"

  name   = var.name
  region = var.europe.region
}
module "europe_geo_route" {
  source = "./modules/route"

  records        = [module.europe_ec2server.server_ip]
  continent      = var.europe.continent
  domain_name    = var.domain_name
  region         = var.europe.region
  name           = var.name
  default_record = true
}
module "europe_bucket" {
  source = "./modules/s3bucket"

  name   = var.name
  region = var.europe.region
}


# --------------------------------------------------------------------------------------------------------
# Asia
module "asia_ec2server" {
  source = "./modules/ec2server"

  name   = var.name
  region = var.asia.region
}
module "asia_geo_route" {
  source = "./modules/route"

  records       = [module.asia_ec2server.server_ip]
  continent     = var.asia.continent
  domain_name   = var.domain_name
  region        = var.asia.region
  name          = var.name
}
module "asia_bucket" {
  source = "./modules/s3bucket"

  name   = var.name
  region = var.asia.region
}


# --------------------------------------------------------------------------------------------------------
# USA
module "usa_ec2server" {
  source = "./modules/ec2server"

  name   = var.name
  region = var.usa.region
}
module "usa_geo_route" {
  source = "./modules/route"

  records       = [module.usa_ec2server.server_ip]
  continent     = var.usa.continent
  domain_name   = var.domain_name
  region        = var.usa.region
  name          = var.name
}
module "usa_bucket" {
  source = "./modules/s3bucket"

  name   = var.name
  region = var.usa.region
}
