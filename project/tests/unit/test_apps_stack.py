import aws_cdk as core
import aws_cdk.assertions as assertions

from apps.infra_stack import AppsStack

# example tests. To run these tests, uncomment this file along with the example
# resource in apps/apps_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AppsStack(app, "apps")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
