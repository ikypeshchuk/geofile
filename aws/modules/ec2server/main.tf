
resource "aws_default_vpc" "default" {}


resource "aws_eip" "static_ip" {
  instance = aws_instance.webserver.id
  domain   = "vpc"

  tags = {
    Name  = "${var.name} Server IP"
  }
}


resource "aws_instance" "webserver" {
  ami                    = data.aws_ami.latest_amazon_linux.id
  instance_type          = var.instance_type
  vpc_security_group_ids = [aws_security_group.sg.id]
  key_name               = aws_key_pair.key.key_name
  user_data              = file("modules/ec2server/userdata.sh")

  tags = {
    Name  = "${var.name} Web Server"
  }
}
