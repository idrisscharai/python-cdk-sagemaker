import os
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_sagemaker as sagemaker,
    aws_s3 as s3,
    aws_iam as iam,
    aws_ec2 as ec2,
    CfnTag, Tags,
    CfnOutput
)


region = "eu-central-1"

ALLOWED_ENVS = ["challenge", "dev", "qa", "uat", "prod"]
# Get the env from environment variable
env = os.environ.get("ENV", "challenge")  # Default to "challenge" if not set

# Restrict envs to deploy to
if env not in ALLOWED_ENVS:
    raise ValueError(
        f"The environment is invalid. Must be one of {ALLOWED_ENVS}"
    )
print(f"Deploying to environment: {env}.")


class InfraStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.CfnVPC(self, "Idriss_VPC",
            cidr_block="172.30.255.0/24",
            enable_dns_support=True,
            enable_dns_hostnames=True,
            tags=[CfnTag(
                key="Name",
                value=f"{self.node.id}_{env}"
            )]
        )

        subnet1 = ec2.CfnSubnet(self, "Idriss_Subnet_1",
            vpc_id=vpc.ref,
            cidr_block="172.30.255.0/25",
            availability_zone=f"{self.region}a",
            map_public_ip_on_launch=True,
            tags=[CfnTag(
                key="Name",
                value=f"{self.node.id}_{env}"
            )]
        )
        subnet2 = ec2.CfnSubnet(self, "Idriss_Subnet_2",
            vpc_id=vpc.ref,
            cidr_block="172.30.255.128/25",
            availability_zone=f"{self.region}b",
            map_public_ip_on_launch=True,
            tags=[CfnTag(
                key="Name",
                value=f"{self.node.id}_{env}"
            )]
        )

        public_subnets = [subnet1, subnet2]

        network_acl = ec2.CfnNetworkAcl(self, "Idriss_NetworkACL",
            vpc_id=vpc.ref,
            tags=[CfnTag(
                key="Name",
                value=f"{self.node.id}_{env}"
            )]
        )

        network_acl_inbound = ec2.CfnNetworkAclEntry(self, "InboundAllowAll",
            network_acl_id=network_acl.ref,
            rule_number=100,
            protocol=-1,
            rule_action="allow",
            egress=False,
            cidr_block="0.0.0.0/0"
        )
        network_acl_outbound = ec2.CfnNetworkAclEntry(self, "OutboundAllowAll",
            network_acl_id=network_acl.ref,
            rule_number=100,
            protocol=-1,
            rule_action="allow",
            egress=True,
            cidr_block="0.0.0.0/0"
        )

        for i, subnet in enumerate(public_subnets, start=1):
            ec2.CfnSubnetNetworkAclAssociation(self, f"Idriss_Subnet{i}_NetworkACL_Association",
                subnet_id=subnet.ref,
                network_acl_id=network_acl.ref
            )

        internet_gateway = ec2.CfnInternetGateway(self, "Idriss_InternetGateway",
            tags=[CfnTag(
                key="Name",
                value=f"{self.node.id}_{env}"
            )]                                      
        )

        vpc_gateway_attachment = ec2.CfnVPCGatewayAttachment(self, "Idriss_VPC_Gateway_Attachment",
            vpc_id=vpc.ref,
            internet_gateway_id=internet_gateway.ref
        )

        route_table = ec2.CfnRouteTable(self, "Idriss_RouteTable",
            vpc_id=vpc.ref,
            tags=[CfnTag(
                key="Name",
                value=f"{self.node.id}_{env}"
            )] 
        )

        internet_route = ec2.CfnRoute(self, "InternetRoute",
            route_table_id=route_table.ref,
            destination_cidr_block="0.0.0.0/0",
            gateway_id=internet_gateway.ref
        )

        for i, subnet in enumerate(public_subnets, start=1):
            ec2.CfnSubnetRouteTableAssociation(self, f"Idriss_Subnet{i}_RouteTable_Association",
                subnet_id=subnet.ref,
                route_table_id=route_table.ref
            )

        DHCP_Options = ec2.CfnDHCPOptions(self, "Idriss_DHCP_Options",
            domain_name=f"{region}.compute.internal",
            domain_name_servers=["AmazonProvidedDNS"],
            ipv6_address_preferred_lease_time=None,
            netbios_node_type=None,
            tags=[CfnTag(
                key="Name",
                value=f"{self.node.id}_{env}"
            )]
        )

        # VPC Endpoints for Sagemaker API/Runtime/Studio, STS, and S3
        ec2.CfnVPCEndpoint(self, "Idriss_SageMakerAPIEndpoint",
            vpc_id=vpc.ref,
            service_name=f"com.amazonaws.{region}.sagemaker.api",
            vpc_endpoint_type="Interface",
            subnet_ids=[subnet.ref for subnet in public_subnets],
            private_dns_enabled=True,
            tags=[CfnTag(
                key="Name",
                value=f"{self.node.id}_{env}"
            )] 
        )
        ec2.CfnVPCEndpoint(self, "Idriss_SageMakerRuntimeEndpoint",
            vpc_id=vpc.ref,
            service_name=f"com.amazonaws.{region}.sagemaker.runtime",
            vpc_endpoint_type="Interface",
            subnet_ids=[subnet.ref for subnet in public_subnets],
            private_dns_enabled=True,
            tags=[CfnTag(
                key="Name",
                value=f"{self.node.id}_{env}"
            )]
        )
        ec2.CfnVPCEndpoint(self, "Idriss_STSEndpoint",
            vpc_id=vpc.ref,
            service_name=f"com.amazonaws.{region}.sts",
            vpc_endpoint_type="Interface",
            subnet_ids=[subnet.ref for subnet in public_subnets],
            private_dns_enabled=True,
            tags=[CfnTag(
                key="Name",
                value=f"{self.node.id}_{env}"
            )]
        )
        ec2.CfnVPCEndpoint(self, "Idriss_S3GatewayEndpoint",
            vpc_id=vpc.ref,
            service_name=f"com.amazonaws.{region}.s3",
            vpc_endpoint_type="Gateway",
            route_table_ids=[route_table.ref],
            tags=[CfnTag(
                key="Name",
                value=f"{self.node.id}_{env}"
            )]
        )

        nsg = ec2.CfnSecurityGroup(self, "Idriss_NSG",
            group_description="Allow all access",
            vpc_id=vpc.ref,
            tags=[CfnTag(
                key="Name",
                value=f"{self.node.id}_{env}"
            )]
        )

        nsg_inbound_rule = ec2.CfnSecurityGroupIngress(self, "Idriss_AllowAll",
            group_id=nsg.ref,
            ip_protocol="tcp",
            from_port=0,
            to_port=65535,
            cidr_ip="0.0.0.0/0",
            description="Allow all inbound"
        )

        s3_bucket = s3.CfnBucket(self, "Idriss_S3Bucket",
            bucket_name=f"idriss-s3-bucket-swisscom-challenge-{env}",
            public_access_block_configuration=s3.CfnBucket.PublicAccessBlockConfigurationProperty(
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False
            ),
            tags=[CfnTag(
                key="Name",
                value=f"{self.node.id}_{env}"
            )]
        )
        s3_bucket_policy = s3.CfnBucketPolicy(self, "Idriss_S3Bucket_Policy",
            bucket=s3_bucket.ref,
            policy_document={
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:*",
                        "Resource": [
                            f"{s3_bucket.attr_arn}",
                            f"{s3_bucket.attr_arn}/*"
                        ]
                    }
                ]
            }
        )

        execution_role = iam.CfnRole(self, "Idriss_ExecutionRole",
            assume_role_policy_document={
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "sagemaker.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }]
            },
            managed_policy_arns=[
                "arn:aws:iam::aws:policy/AmazonS3FullAccess",
                "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
            ],
            tags=[CfnTag(
                key="Name",
                value=f"{self.node.id}_{env}"
            )]
        )

        sagemaker_domain = sagemaker.CfnDomain(self, "Idriss_SagemakerStudio_Domain",
            auth_mode="IAM",
            domain_name="Idriss-SagemakerStudio-Domain",
            default_user_settings=sagemaker.CfnDomain.UserSettingsProperty(
                execution_role=execution_role.attr_arn,
                jupyter_server_app_settings=sagemaker.CfnDomain.JupyterServerAppSettingsProperty(
                    default_resource_spec=sagemaker.CfnDomain.ResourceSpecProperty(
                        instance_type="system"
                    )
                )
            ),
            subnet_ids=[subnet.ref for subnet in public_subnets],
            vpc_id=vpc.ref,
            app_network_access_type="VpcOnly",
            tag_propagation="ENABLED",
            tags=[CfnTag(
                key="Name",
                value=f"{self.node.id}_{env}"
            )]
        )
        
        sagemaker_user_profile = sagemaker.CfnUserProfile(self, "Idriss_UserProfile",
            domain_id=sagemaker_domain.attr_domain_id,
            user_profile_name="Idriss-User",
            user_settings={
                "executionRole": execution_role.attr_arn
            }
        )


    # Outputs
        CfnOutput(self, "Idriss_S3_URI_Output",
            value=f"s3://{s3_bucket.bucket_name}",
            export_name="Idriss-S3-URI-Output"
        )
        CfnOutput(self, "Idriss_Execution_Role_ARN_Output",
            value=execution_role.attr_arn,
            export_name="Idriss-Execution-Role-ARN-Output"
        )
