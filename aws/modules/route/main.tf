data "aws_route53_zone" "r53_zone" {
  name = var.domain_name
}

resource "aws_route53_record" "record" {
  zone_id        = data.aws_route53_zone.r53_zone.zone_id
  name           = var.domain_name
  type           = "A"
  set_identifier = "${var.name}-${var.region}"
  ttl     = "300"
  records = var.records

  geolocation_routing_policy {
    continent = var.continent
  }

  //alias {
  //  name                   = var.alias_name
  //  zone_id                = var.alias_zone_id
  //  evaluate_target_health = true
  //}
}

resource "aws_route53_record" "default" {
  count          = var.default_record ? 1 : 0
  zone_id        = data.aws_route53_zone.r53_zone.zone_id
  name           = var.domain_name
  type           = "A"
  set_identifier = "${var.name}-default"
  ttl     = "300"
  records = var.records

  geolocation_routing_policy {
    country = "*"
  }

  //alias {
  //  name                   = var.default_alias_name != "" ? var.default_alias_name : var.alias_name
  //  zone_id                = var.default_alias_zone_id != "" ? var.default_alias_zone_id : var.alias_zone_id
  //  evaluate_target_health = true
  //}
}