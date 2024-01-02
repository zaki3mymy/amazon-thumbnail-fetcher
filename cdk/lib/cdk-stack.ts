import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';


export interface CustomizedProps extends cdk.StackProps {
  projectName: string;
}

export class CdkStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: CustomizedProps) {
    super(scope, id, props);

    // IAM
    const iamRoleForLambda = new iam.Role(this, "iamRoleForLambda", {
      roleName: `${props.projectName}-lambda-role`,
      assumedBy: new iam.ServicePrincipal("lambda.amazonaws.com"),
      managedPolicies: [
        {
          "managedPolicyArn": "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
        }
      ]
    })

    // Lambda
    const pythonPackagePath = "../src/" + props.projectName.replace(/-/g, "_");
    const lambdaFunctions = new lambda.Function(this, "lambdaFunction", {
      functionName: `${props.projectName}-lambda`,
      runtime: lambda.Runtime.PYTHON_3_12,
      timeout: cdk.Duration.seconds(10),
      code: lambda.Code.fromAsset(pythonPackagePath),
      handler: "lambda_handler.lambda_function",
      role: iamRoleForLambda,
      environment: {
        "LOGLEVEL": "INFO",
      }
    })

    // API Gateway
    const apiGatewayRestApi = new apigateway.RestApi(this, "apiGateway", {
      restApiName: `${props.projectName}-api`,
      deployOptions: {
        loggingLevel: apigateway.MethodLoggingLevel.INFO,
        dataTraceEnabled: true,
        metricsEnabled: true,
        stageName: "v1",
      },
      cloudWatchRole: true,
    })
    const thumbnailResoruce = apiGatewayRestApi.root.addResource("thumbnail");
    const lambdaIntegration = new apigateway.LambdaIntegration(lambdaFunctions);
    thumbnailResoruce.addMethod("GET", lambdaIntegration);
  }
}
