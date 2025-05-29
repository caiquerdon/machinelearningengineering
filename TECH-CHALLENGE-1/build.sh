#!/bin/bash

mkdir -p lambda_build
cp app.py requirements.txt lambda_build/
echo "from app import handler" > lambda_build/lambda_function.py

docker run --rm -v "$PWD/lambda_build":/var/task amazonlinux:2 \
  /bin/bash -c "
    yum install -y python3 pip zip;
    pip3 install -r requirements.txt -t .;
    zip -r9 /var/task/api_embrapa_lambda.zip .
"
