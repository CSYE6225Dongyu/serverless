import os
import pymysql
import uuid
from datetime import datetime, timedelta
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import json
import socket

# from dotenv import load_dotenv

# # Load environment variables (useful for local testing)
# load_dotenv()

# Database configuration
# DB_HOST = os.getenv("DB_HOST", "localhost")
DB_HOST = "csye6225.cjsgequ8eo8s.us-east-1.rds.amazonaws.com"
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_NAME = os.getenv("DB_NAME", "mydb")
Domain_Name = os.getenv("Domain_Name", "demo.csye6225dongyu.me")

# SendGrid configuration
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")  # Use environment variables for security
FROM_EMAIL = 'no-reply@demo.csye6225dongyu.me'  # Must be a verified email in SendGrid

def generate_verification_token():
    """Generate a unique verification token."""
    return str(uuid.uuid4())  # Use UUID to ensure uniqueness

def clean_expired_verifications(user_id):
    """Clean expired verification records for the user."""
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        with connection.cursor() as cursor:
            # Delete all expired tokens
            cursor.execute("DELETE FROM email_verification WHERE expires_at < NOW()")
            # Optional: Also remove tokens associated with this user
            cursor.execute("DELETE FROM email_verification WHERE user_id = %s", (user_id,))
            connection.commit()
        connection.close()
        print("Expired verifications cleaned.")
        return True
    except Exception as e:
        print(f"Error cleaning expired verifications: {e}")
        return False

def store_verification_data(user_id, token):
    """Store the verification token and expiration time in the database."""
    try:
        clean_expired_verifications(user_id)
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        with connection.cursor() as cursor:
            expires_at = datetime.now() + timedelta(minutes=2)  # Token valid for 2 minutes
            sql = """
                INSERT INTO email_verification (id, user_id, token, expires_at)
                VALUES (UUID(), %s, %s, %s)
            """
            cursor.execute(sql, (user_id, token, expires_at))
            connection.commit()
        connection.close()
        print(f"Verification data stored successfully for user_id {user_id}.")
        return True
    except Exception as e:
        print(f"Error storing verification data: {e}")
        return False

def generate_verification_link(user_email, user_id):
    """Generate a verification link for the user."""
    # Generate a token
    token = generate_verification_token()
    
    # Store the token in the database
    success = store_verification_data(user_id, token)
    if success:
        # Create the verification link
        verification_link = f"http://{Domain_Name}:8080/verify/{token}"  # Replace with your domain
        print(f"Verification link generated for {user_email}: {verification_link}")
        return verification_link
    return None

def send_email(to_email, subject, html_content):
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
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

# def lambda_handler(event, context=None):
#     """Lambda function entry point."""
#     # Extract parameters from the event
#     user_email = event.get('email')
#     user_id = event.get('userId')

#     print("email read", user_email)
#     print("id read", user_id)



#     if not user_email or not user_id:
#         return {
#             'statusCode': 400,
#             'body': 'Missing email or userId in the event.'
#         }

#     # Generate a verification link
#     verification_link = generate_verification_link(user_email, user_id)
#     if verification_link:
#         # Construct the email content
#         subject = 'Verify Your Email Address'
#         html_content = f"""
#             <p>Hello,</p>
#             <p>Please verify your email address by clicking the link below:</p>
#             <a href="{verification_link}">{verification_link}</a>
#             <p>Thank you!</p>
#         """
#         # Send the email
#         print("sending email...")
#         if send_email(user_email, subject, html_content):
#             return {
#                 'statusCode': 200,
#                 'body': {'message': 'Verification email sent successfully.'}
#             }
#         else:
#             return {
#                 'statusCode': 500,
#                 'body': 'Failed to send email.'
#             }
#     return {
#         'statusCode': 500,
#         'body': 'Failed to generate verification link.'
#     }


# # Local testing
# if __name__ == "__main__":
#     # Simulate a test event
#     test_event = {
#         'email': 'dyliu981@gmail.com',  # Example email
#         'userId': '8edcf1c6-4d61-4ad2-83df-52d6f4c32bf5'  # Example user ID
#     }
#     print("Simulating Lambda function...")
#     response = lambda_handler(test_event)
#     print("Response:", response)


# import json
# import socket

# def lambda_handler(event, context):
#     # RDS 配置
#     host = "csye6225.cjsgequ8eo8s.us-east-1.rds.amazonaws.com"
#     port = 3306
    
#     # DNS 解析测试
#     try:
#         ip = socket.gethostbyname(host)
#         print(f"Resolved IP for RDS: {ip}")
#     except Exception as e:
#         print(f"DNS resolution failed for RDS: {e}")
#         return {
#             "statusCode": 500,
#             "body": json.dumps("Failed to resolve RDS domain name.")
#         }
    
#     # 数据库连接测试
#     try:
#         with socket.create_connection((host, port), timeout=10):
#             print(f"Successfully connected to {host}:{port}")
#     except Exception as e:
#         print(f"Failed to connect to RDS at {host}:{port}, error: {e}")
#         return {
#             "statusCode": 500,
#             "body": json.dumps("Failed to connect to RDS.")
#         }

#     return {
#         "statusCode": 200,
#         "body": json.dumps("DNS and RDS connection tests passed!")
#     }





def test_connectivity():
    services = [
        ("http://example.com", 80),  # HTTP
        ("https://example.com", 443)  # HTTPS
    ]
    for service, port in services:
        try:
            with socket.create_connection((service, port), timeout=10):
                print(f"Successfully connected to {service} on port {port}")
        except Exception as e:
            print(f"Failed to connect to {service} on port {port}: {e}")

def lambda_handler(event, context):
    test_connectivity()
    return {"statusCode": 200, "body": "Connectivity test completed"}
