import os
import json
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from urllib.parse import urlencode
import boto3
import base64

# Initialize global variables
SENDGRID_API_KEY = None
Domain_Name = None
FROM_EMAIL = None

def get_secrets():
    """Retrieve secrets from AWS Secrets Manager."""
    secret_name = os.getenv("SECRET_NAME", "my-lambda-secrets")
    region_name = os.getenv("AWS_WEBAPP_REGION", "us-east-1")
    
    session = boto3.session.Session() # type: ignore run Ok in the lambda aws
    client = session.client(service_name="secretsmanager", region_name=region_name)
    
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        
        if 'SecretString' in get_secret_value_response:
            secrets = json.loads(get_secret_value_response['SecretString'])
        else:
            secrets = json.loads(base64.b64decode(get_secret_value_response['SecretBinary']))
        
        return secrets
    except Exception as e:
        print(f"Error retrieving secrets: {e}")
        raise

# Load secrets into global variables
try:
    secrets = get_secrets()
    SENDGRID_API_KEY = secrets.get("sendgrid_api_key")
    Domain_Name = secrets.get("domain_name", "demo.csye6225dongyu.me")
    FROM_EMAIL = secrets.get("from_email", "no-reply@demo.csye6225dongyu.me")
except Exception as e:
    print("Failed to initialize secrets. Exiting.")
    raise

def generate_verification_link(token):
    """generate verifie link"""
    verification_link = f"https://{Domain_Name}/verify/{token}"
    return verification_link

def send_email(to_email,subject, html_content):
    """Send an email using SendGrid."""
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Email sent successfully to {to_email}. Status code: {response.status_code}")
        return response.status_code == 202
    except Exception as e:
        print(f"Error sending email to {to_email}: {e}")
        return False
    

def lambda_handler(event, context):
    """Lambda function to process SNS events."""

    # test network connecting
    test_connectivity()

    # Check and print values
    print("Checking environment variables:")
    if SENDGRID_API_KEY:
        print(f"SENDGRID_API_KEY: {SENDGRID_API_KEY[:5]}... (truncated for security)")  # Do not print full API Key
    else:
        print("SENDGRID_API_KEY is missing or not set.")

    if Domain_Name:
        print(f"Domain_Name: {Domain_Name}")
    else:
        print("Domain_Name is missing or not set.")

    if FROM_EMAIL:
        print(f"FROM_EMAIL: {FROM_EMAIL}")
    else:
        print("FROM_EMAIL is missing or not set.")

    try:
        # Iterate over SNS records
        for record in event['Records']:
            # Extract the SNS Message field
            sns_message = record['Sns']['Message']  # This is a JSON string
            print(f"Raw SNS Message: {sns_message}")

            # Parse the JSON string
            message_data = json.loads(sns_message)

            # Extract fields from the parsed message
            email = message_data.get('email')
            token = message_data.get('token')

            if not email or not token:
                print("Validation failed: Missing email or token.")
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Missing email or token in the SNS message.'})
                }

            # Log and process the data
            print(f"Extracted email: {email}")
            print(f"Extracted token: {token}")

            try:
                verification_link = generate_verification_link(token)
                print(f"Generated verification link: {verification_link}")
            except Exception as e:
                print(f"Error generating verification link: {e}")
                return {
                    'statusCode': 500,
                    'body': json.dumps({'error': 'Failed to generate verification link.'})
                }
            
        # send the email
        subject = 'Verify Your Email Address'
        html_content = f"""
            <p>Hello,</p>
            <p>Please verify your email address by clicking the link below:</p>
            <a href="{verification_link}">{verification_link}</a>
            <p>Thank you!</p>
        """        
        try:
            if send_email(email, subject, html_content):
                print(f"Verification email sent successfully to {email}.")
                return {
                    'statusCode':200,
                    'body': json.dumps({'message': 'Verification email sent successfully.'})
                }
            else:
                print(f"Failed to send email to {email}.")
                return {
                    'statusCode': 500,
                    'body': json.dumps({'error': 'Failed to send email.'})
                }
        except Exception as e:
            print(f"Error during email sending process: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'An error occurred while sending email.'})
            }

    except Exception as e:
        print(f"Error processing SNS event: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "An error occurred while processing the SNS event."})
        }
    
import requests

def test_connectivity():
    try:
        response = requests.get("https://api.sendgrid.com")
        print(f"Connectivity Test: {response.status_code}")
    except Exception as e:
        print(f"Error during connectivity test: {e}")

