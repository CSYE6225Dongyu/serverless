# serverless

## Overview

This Lambda function processes SNS messages to send email verification links using SendGrid.

### Key Features:

1. **Receives SNS messages** containing `email` and `token` fields.
2. **Generates verification links** using the `Domain_Name` environment variable.
3. **Sends emails** via SendGrid.

### Environment Variables:

- `SENDGRID_API_KEY`: SendGrid API key.
- `Domain_Name`: Base domain for verification links.
- `FROM_EMAIL`: Sender email address.

## Deployment

Using Makefile:

1. Package the Function

   `make package`

2. Deploy to AWS

   `make deploy`

### Makefile Commands:

- `make build`: Creates the deployment ZIP file.
- `make clean`: Cleans up temporary files.
- `make deploy`: Deploys the Lambda package to AWS (update `YOUR_LAMBDA_FUNCTION_NAME` in `Makefile`).

------

### Notes:

- Ensure the Lambda function role has permissions for SNS and internet access (for SendGrid).
- Verify deployment logs in CloudWatch after deploying.