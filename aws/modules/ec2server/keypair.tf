resource "aws_key_pair" "key" {
  key_name   = "${var.name}-${var.region}"
  public_key = file("~/.ssh/id_rsa.pub")
}
