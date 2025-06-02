import os
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_sagemaker as sagemaker,
    CfnTag,
    Fn
)


# Imports
s3_bucket_uri = Fn.import_value("Idriss-S3-URI-Output")
execution_role_arn = Fn.import_value("Idriss-Execution-Role-ARN-Output")


ALLOWED_ENVS = ["challenge", "dev", "qa", "uat", "prod"]
# Get the env from environment variable
env = os.environ.get("ENV", "challenge")  # Default to "challenge" if not set

# Restrict envs to deploy to
if env not in ALLOWED_ENVS:
    raise ValueError(
        f"The environment is invalid. Must be one of {ALLOWED_ENVS}"
    )
print(f"Deploying to environment: {env}.")


class ModelStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        model = sagemaker.CfnModel(self, "Idriss_Dummy_Model",
            execution_role_arn=execution_role_arn,
            model_name="Idriss-Dummy-Model",
            primary_container=sagemaker.CfnModel.ContainerDefinitionProperty(
                image="605134434340.dkr.ecr.eu-central-1.amazonaws.com/cdk-hnb659fds-container-assets-605134434340-eu-central-1:latest",
                mode="SingleModel",
                model_data_url=f"{s3_bucket_uri}/models/idriss-model-{env}.tar.gz"
            )
        )

        endpoint_config = sagemaker.CfnEndpointConfig(self, "Idriss_Dummy_Endpoint_Config",
            production_variants=[sagemaker.CfnEndpointConfig.ProductionVariantProperty(
                initial_instance_count=1,
                instance_type="ml.t2.medium",
                model_name=model.attr_model_name,
                variant_name="AllTraffic"
            )],
            endpoint_config_name="Idriss-Dummy-Endpoint-Config",
            tags=[CfnTag(
                key="Name",
                value=f"{self.node.id}_{env}"
            )]
        )

        sagemaker.CfnEndpoint(self, "Idriss_Dummy_Endpoint",
            endpoint_name="Idriss-Dummy-Endpoint",
            endpoint_config_name=endpoint_config.attr_endpoint_config_name,
            tags=[CfnTag(
                key="Name",
                value=f"{self.node.id}_{env}"
            )]
        )
        