# python-cdk-sagemaker
Deploy a model on AWS Sagemaker Studio along with its required infra using Python and AWS CDK.

Here are the steps followed to build and deploy the project:

- AWS CLI Credentials
    - export the AWS CLI Credentials
    - export ENV=challenge (or other)

- STEPS
    1. Using an IDE on a tablet:
        - GitHub Codespaces (essentially VSCode on browser with access to GitHub)
    2. Create a GitHub repo for the project  (initialize with README.md)
        - idrisscharai/python-cdk-sagemaker
    3. Create a Codespaces environment using the repo above
        - [https://cautious-yodel-vrgj5xpp9xgcpvpj.github.dev](https://cautious-yodel-vrgj5xpp9xgcpvpj.github.dev/)
        - Ubuntu 20.04.6 LTS
        - Python 3.12.1
        - pip
        - npm
    4. Install requirements:
        - AWS CLI (2.27.24)
            - curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
            - unzip awscliv2.zip
            - sudo ./aws/install
        - AWS CDK (2.1017.0)
            - npm install -g aws-cdk
        - Python aws-cdk module
            - python -m pip install aws-cdk-lib
        - mkdir project
        - python3 -m venv .venv
        - source .venv/bin/activate
        - cdk init app --language python
    5. Research and list the AWS resources needed for the project:
        - Infra:
            - Sagemaker Domain (ml.t3.medium)
            - User Profile
            - VPC + 2x subnets (2x AZs)
            - DHCP
            - route table + internet route + associations
            - internet gateway + association
            - network ACL + in/outbound rules + association
            - 5x VPC Endpoints: api/runtime/studio/sts/s3
            - NSG + internet rule
            - S3
                - Add dummy model
            - IAM Execution Role
        - Model:
            - Model (build minimal image - No permissions for AWS public ECR)
            - Endpoint
            - Endpoint Config
    6. Create the infra.py and infra_stack.py files
    7. Create the model.py and model_stack.py files
    8. Run cdk bootstrap (needed only once)
    9. Deploy Infra:
        - cd into project folder
        - cdk deploy —app “python3 infra.py”
    10. Create upload_model_to_s3.sh
        - chmod +x upload_model_to_s3.sh
    11. Create serve.py
        1. pip install flask
    12. Create entrypoint.sh
        - chmod +x entrypoint.sh
    13. Model image:
        1. create a Dockerfile for a min dummy container
        2. docker build -t idrisscharai/sagemaker-dummy .
        3. docker login -u idrisscharai (prompt for pwd)
        4. docker push idrisscharai/sagemaker-dummy
        5. aws ecr get-login-password --region eu-central-1 | \
        docker login --username AWS --password-stdin 605134434340.dkr.ecr.eu-central-1.amazonaws.com (auth docker)
        6. docker tag idrisscharai/sagemaker-dummy:latest \
        605134434340.dkr.ecr.eu-central-1.amazonaws.com/cdk-hnb659fds-container-assets-605134434340-eu-central-1:latest (tag the image)
        7. docker push \
        605134434340.dkr.ecr.eu-central-1.amazonaws.com/cdk-hnb659fds-container-assets-605134434340-eu-central-1:latest (push to ECR)
    14. Run the upload_model_to_s3.sh script
    15. Deploy Model:
        - cd into project folder
        - cdk deploy —app “python3 model.py”
    16. Invoke the endpoint:
        1. pip install requests-auth-aws-sigv4 (install AWS Signature V4)
        2. aws sagemaker-runtime invoke-endpoint \
        --endpoint-name Idriss-Dummy-Endpoint \
        --body '{"input": "test"}' \
        --content-type application/json \
        output.json
        cat output.json
    
    ## To Do:
    
    1. Deploy infra + model using GitHub Actions
    2. Destroy an env
        - Some resources created automatically by Sagemaker Domain block this
    3. Manually delete:
        1. EFS (first)
        2. NICs (they get deleted automatically after deleting the EFS)
        3. NSGs - delete their rules first because they have a circular dependency
    4. Add model deployment strategies
    5. Use feature store

- Sample App Steps
    - (create a sample-app folder, cd into it)
    - cdk init sample-app --language=python
    - source .venv/bin/activate