resource "aws_s3_bucket" "public" {
  acl = "public-read"
}
