#!/bin/bash

ALLOWED_ENVS=("challenge" "dev" "qa" "uat" "prod")
# Get the env from environment variable
env="${ENV:-challenge}"

# Restrict envs to deploy to
if [[ ! " ${ALLOWED_ENVS[@]} " =~ " ${env} " ]]; then
  echo "The environment is invalid. Must be one of ${ALLOWED_ENVS[*]}"
  exit 1
fi

S3_BUCKET="idriss-s3-bucket-swisscom-challenge-${env}"
S3_MODEL_PATH="models/idriss-model-${env}.tar.gz"

mkdir -p dummy-model
echo "# Dummy model file for the SageMaker challenge" > dummy-model/dummy-model.py

tar -czf idriss-model-${env}.tar.gz dummy-model/

aws s3 cp idriss-model-${env}.tar.gz s3://$S3_BUCKET/$S3_MODEL_PATH

echo "Dummy model uploaded to:"
echo "s3://$S3_BUCKET/$S3_MODEL_PATH"
