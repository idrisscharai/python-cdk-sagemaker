import aws_cdk as cdk

from model.model_stack import ModelStack


app = cdk.App()
ModelStack(app, "ModelStack")

app.synth()
