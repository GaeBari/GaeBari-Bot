
module "lambda_default_role" {
  source = "./modules/role"
  name   = "LambdaDefault"
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "kms:Decrypt"
      ],
      "Resource": "arn:aws:kms:*:*:*"
    }
  ]
}
EOF
}

resource "aws_s3_bucket" "lambda_build_bucket" {
  bucket = var.lambda_build_bucket
}

// layers
module "pynacl_layer" {
  source = "terraform-aws-modules/lambda/aws"

  create_layer = true

  layer_name          = "pynacl_layer"
  description         = "PyNaCl"
  compatible_runtimes = ["python3.10"]

  source_path = "../layers/pynacl"

  store_on_s3 = true
  s3_bucket   = aws_s3_bucket.lambda_build_bucket.id
}

module "requests_layer" {
  source = "terraform-aws-modules/lambda/aws"

  create_layer = true

  layer_name          = "requests_layer"
  description         = "requests"
  compatible_runtimes = ["python3.10"]

  source_path = "../layers/requests"

  store_on_s3 = true
  s3_bucket   = aws_s3_bucket.lambda_build_bucket.id
}

// Lambdas
module "event_handler" {
  depends_on = [aws_s3_bucket.lambda_build_bucket]

  source = "terraform-aws-modules/lambda/aws"

  function_name = "event_handler"
  description   = "Receive event from Discord server"
  handler       = "main.lambda_handler"
  runtime       = "python3.10"
  timeout       = 120
  source_path   = "../lambdas/event_handler"

  store_on_s3 = true
  s3_bucket   = var.lambda_build_bucket

  create_role = false
  lambda_role = module.lambda_default_role.role_arn

  layers = [
    module.pynacl_layer.lambda_layer_arn
  ]

  environment_variables = {
    "DISCORD_PUBLIC_KEY" = var.DISCORD_PUBLIC_KEY
  }

  tags = {
    version = "v1"
  }
}
