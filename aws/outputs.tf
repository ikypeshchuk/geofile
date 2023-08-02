
output "europe_bucket_name_and_server_ip" {
  value = "${module.europe_bucket.bucket_name}::${module.europe_ec2server.server_ip}"
}

output "asia_bucket_name_and_server_ip" {
  value = "${module.asia_bucket.bucket_name}::${module.asia_ec2server.server_ip}"
}

output "usa_bucket_name_and_server_ip" {
  value = "${module.usa_bucket.bucket_name}::${module.usa_ec2server.server_ip}"
}
