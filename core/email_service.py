"""
Email Service - Email verification system
Använder Gmail SMTP för att skicka verifieringskoder
"""

import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from core.debug_logger import debug, info, warning, error, exception


class EmailService:
    """Email service för verifikation och notifikationer"""
    
    # Gmail SMTP settings
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    EMAIL_ADDRESS = "MultiTeamCommunication@gmail.com"
    EMAIL_PASSWORD = "guom hlwv ousw mkhz"  # App password
    APP_NAME = "MultiTeamCommunication"
    
    def __init__(self):
        """Initialize email service"""
        debug("EmailService", "Initializing email service")
        info("EmailService", f"Email service initialized with: {self.EMAIL_ADDRESS}")
    
    def generate_verification_code(self) -> str:
        """Generate 6-digit verification code"""
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        debug("EmailService", f"Generated verification code: {code}")
        return code
    
    def send_verification_email(self, to_email: str, name: str, code: str) -> bool:
        """Send verification email"""
        debug("EmailService", f"Sending verification email to: {to_email}")
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"{self.APP_NAME} - Email Verification"
            msg['From'] = f"{self.APP_NAME} <{self.EMAIL_ADDRESS}>"
            msg['To'] = to_email
            
            debug("EmailService", "Creating email content")
            
            # Plain text version
            text_content = f"""
Hello {name},

Welcome to {self.APP_NAME}!

Your verification code is: {code}

Please enter this code in the application to verify your email address.

This code will expire in 15 minutes.

If you didn't request this verification, please ignore this email.

Best regards,
{self.APP_NAME} Team
            """
            
            # HTML version
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #1f6aa5 0%, #144870 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .code-box {{
            background-color: #f0f0f0;
            border: 2px dashed #1f6aa5;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            margin: 30px 0;
        }}
        .code {{
            font-size: 32px;
            font-weight: bold;
            color: #1f6aa5;
            letter-spacing: 8px;
            font-family: 'Courier New', monospace;
        }}
        .footer {{
            background-color: #f8f8f8;
            padding: 20px 30px;
            text-align: center;
            font-size: 12px;
            color: #666;
        }}
        .button {{
            display: inline-block;
            padding: 12px 30px;
            background-color: #1f6aa5;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{self.APP_NAME}</h1>
            <p>Email Verification</p>
        </div>
        <div class="content">
            <h2>Hello {name}!</h2>
            <p>Welcome to {self.APP_NAME}. To complete your registration, please verify your email address.</p>
            
            <div class="code-box">
                <p style="margin: 0 0 10px 0; color: #666;">Your verification code:</p>
                <div class="code">{code}</div>
            </div>
            
            <p>Enter this code in the application to verify your email address.</p>
            <p style="color: #999; font-size: 14px;">This code will expire in 15 minutes.</p>
            
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            
            <p style="color: #666; font-size: 14px;">
                If you didn't request this verification, please ignore this email.
            </p>
        </div>
        <div class="footer">
            <p>&copy; 2025 {self.APP_NAME}. All rights reserved.</p>
            <p>This is an automated message, please do not reply.</p>
        </div>
    </div>
</body>
</html>
            """
            
            # Attach both versions
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            debug("EmailService", "Email content created, connecting to SMTP server")
            
            # Send email
            with smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT) as server:
                debug("EmailService", "Starting TLS")
                server.starttls()
                
                debug("EmailService", "Logging in to SMTP server")
                server.login(self.EMAIL_ADDRESS, self.EMAIL_PASSWORD)
                
                debug("EmailService", "Sending email")
                server.send_message(msg)
            
            info("EmailService", f"Verification email sent successfully to: {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            error("EmailService", "SMTP authentication failed - check credentials")
            return False
        except smtplib.SMTPException as e:
            exception("EmailService", f"SMTP error sending email to {to_email}")
            return False
        except Exception as e:
            exception("EmailService", f"Unexpected error sending email to {to_email}")
            return False
    
    def send_email(self, to_email: str, subject: str, body: str, html_body: str = None) -> bool:
        """Generic send email method"""
        debug("EmailService", f"Sending email to: {to_email}")
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.APP_NAME} <{self.EMAIL_ADDRESS}>"
            msg['To'] = to_email
            
            # Attach text version
            part1 = MIMEText(body, 'plain')
            msg.attach(part1)
            
            # Attach HTML version if provided
            if html_body:
                part2 = MIMEText(html_body, 'html')
                msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT) as server:
                server.starttls()
                server.login(self.EMAIL_ADDRESS, self.EMAIL_PASSWORD)
                server.send_message(msg)
            
            info("EmailService", f"Email sent successfully to: {to_email}")
            return True
            
        except Exception as e:
            error("EmailService", f"Error sending email to {to_email}: {e}")
            return False
    
    def send_welcome_email(self, to_email: str, name: str) -> bool:
        """Send welcome email after verification"""
        debug("EmailService", f"Sending welcome email to: {to_email}")
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Welcome to {self.APP_NAME}!"
            msg['From'] = f"{self.APP_NAME} <{self.EMAIL_ADDRESS}>"
            msg['To'] = to_email
            
            text_content = f"""
Hello {name},

Your email has been verified successfully!

Welcome to {self.APP_NAME}. You can now access all features of the application.

Get started:
- Connect with your team
- Share files securely via P2P
- Communicate in real-time

If you have any questions, feel free to reach out to our support team.

Best regards,
{self.APP_NAME} Team
            """
            
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #107c10 0%, #0d5e0d 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .success-icon {{
            text-align: center;
            font-size: 64px;
            color: #107c10;
            margin: 20px 0;
        }}
        .footer {{
            background-color: #f8f8f8;
            padding: 20px 30px;
            text-align: center;
            font-size: 12px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{self.APP_NAME}</h1>
            <p>Welcome!</p>
        </div>
        <div class="content">
            <div class="success-icon">✓</div>
            <h2 style="text-align: center;">Email Verified!</h2>
            <p>Hello {name},</p>
            <p>Your email has been verified successfully. Welcome to {self.APP_NAME}!</p>
            
            <h3>Get Started:</h3>
            <ul>
                <li>Connect with your team members</li>
                <li>Share files securely via P2P</li>
                <li>Communicate in real-time</li>
                <li>Manage your projects efficiently</li>
            </ul>
            
            <p>If you have any questions, our support team is here to help.</p>
        </div>
        <div class="footer">
            <p>&copy; 2025 {self.APP_NAME}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
            """
            
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            with smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT) as server:
                server.starttls()
                server.login(self.EMAIL_ADDRESS, self.EMAIL_PASSWORD)
                server.send_message(msg)
            
            info("EmailService", f"Welcome email sent successfully to: {to_email}")
            return True
            
        except Exception as e:
            exception("EmailService", f"Error sending welcome email to {to_email}")
            return False


    def send_backup_codes_email(self, to_email: str, name: str, codes: list, secret_key: str = None, qr_image = None) -> bool:
        """Send backup codes email with 30 codes, secret key and QR code"""
        debug("EmailService", f"Sending backup codes email to: {to_email}")
        
        try:
            # Create message with related parts for embedded images
            msg = MIMEMultipart('related')
            msg['Subject'] = f"{self.APP_NAME} - Your 2FA Backup Codes"
            msg['From'] = f"{self.APP_NAME} <{self.EMAIL_ADDRESS}>"
            msg['To'] = to_email
            
            # Create alternative part for HTML
            msg_alternative = MIMEMultipart('alternative')
            msg.attach(msg_alternative)
            
            # Formatera secret key med mellanslag för läsbarhet
            secret_key_formatted = ""
            if secret_key:
                # Formatera som: XXXX XXXX XXXX XXXX
                secret_key_formatted = ' '.join([secret_key[i:i+4] for i in range(0, len(secret_key), 4)])
                debug("EmailService", f"Formatted secret key for email")
            
            # Formatera backup codes i 3 kolumner × 10 rader
            codes_html = ""
            for i in range(0, 30, 3):
                row_codes = codes[i:i+3]
                codes_html += f"""
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #e0e0e0;">{i+1}. {row_codes[0]}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #e0e0e0;">{i+2}. {row_codes[1] if len(row_codes) > 1 else ''}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #e0e0e0;">{i+3}. {row_codes[2] if len(row_codes) > 2 else ''}</td>
                </tr>
                """
            
            # HTML version
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 700px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #1f6aa5 0%, #144870 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .codes-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: #f9f9f9;
            border: 2px solid #1f6aa5;
            border-radius: 8px;
            overflow: hidden;
        }}
        .codes-table td {{
            font-family: 'Courier New', monospace;
            font-size: 14px;
            color: #333;
        }}
        .warning-box {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .footer {{
            background-color: #f8f8f8;
            padding: 20px 30px;
            text-align: center;
            font-size: 12px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{self.APP_NAME}</h1>
            <p>Two-Factor Authentication Backup Codes</p>
        </div>
        <div class="content">
            <h2>Hello {name}!</h2>
            <p>Here are your 30 backup codes for Two-Factor Authentication. Each code can only be used once.</p>
            
            <div class="warning-box">
                <strong>⚠️ Important:</strong> These codes are only for 2FA authenticator access. Save them in a safe place. You can use them to access your account if you lose your authenticator device.
            </div>
            
            <table class="codes-table">
                {codes_html}
            </table>
            
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            
            <p><strong>How to use backup codes:</strong></p>
            <ul style="list-style-type: none; padding-left: 0; margin-left: 0;">
                <li>Each code can only be used once</li>
                <li>Use them when you don't have access to your authenticator app</li>
                <li>Keep them in a secure location</li>
                <li>Never share these codes with anyone</li>
            </ul>
            
            <div style="height: 45px;"></div>
            
            <h3 style="color: #ffffff; margin-top: 30px;">2FA Setup Information</h3>
            <p>Use this information to set up 2FA on a new device:</p>
            
            <div style="text-align: left; margin: 20px 0;">
                <img src="cid:qr_code" alt="QR Code" style="max-width: 200px; border: 2px solid #1f6aa5; border-radius: 8px; padding: 10px; background-color: white;"/>
                <p style="margin-top: 10px; font-size: 12px; color: #666;">Scan this QR code with Google Authenticator</p>
            </div>
            
            <div style="background-color: #f9f9f9; border: 2px solid #1f6aa5; border-radius: 8px; padding: 15px; margin: 20px 0;">
                <p style="margin: 0 0 10px 0; font-weight: bold;">Manual Entry Key:</p>
                <p style="font-family: monospace; font-size: 14px; color: #333333; margin: 0; word-break: break-all;">{secret_key_formatted}</p>
            </div>
            
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            
            <p style="color: #666; font-size: 14px;">
                If you didn't request these backup codes, please contact support immediately.
            </p>
            
            <div style="background-color: #fff3cd; border-left: 4px solid #ff6b6b; padding: 20px; margin: 30px 0; border-radius: 4px;">
                <p style="margin: 0 0 10px 0; font-weight: bold; color: #d63031; font-size: 16px;">🔒 SECURITY WARNING</p>
                <p style="margin: 0; color: #333; font-size: 14px; line-height: 1.6;">
                    This email contains sensitive security information including your 2FA secret key, QR code, and backup codes. 
                    <strong>This is a significant security risk if this email falls into the wrong hands.</strong>
                </p>
                <p style="margin: 10px 0 0 0; color: #333; font-size: 14px; line-height: 1.6;">
                    <strong>IMPORTANT ACTIONS:</strong><br>
                    1. Save the backup codes in a secure password manager or encrypted storage<br>
                    2. Save the QR code and secret key if needed for future device setup<br>
                    3. <strong style="color: #d63031;">DELETE THIS EMAIL IMMEDIATELY</strong> after saving the information<br>
                    4. Empty your email trash/deleted items folder
                </p>
                <p style="margin: 10px 0 0 0; color: #d63031; font-size: 13px; font-weight: bold;">
                    ⚠️ Never forward this email or share its contents with anyone!
                </p>
            </div>
        </div>
        <div class="footer">
            <p>&copy; 2025 {self.APP_NAME}. All rights reserved.</p>
            <p>This is an automated message, please do not reply.</p>
        </div>
    </div>
</body>
</html>
            """
            
            # Attach HTML
            msg_alternative.attach(MIMEText(html_content, 'html'))
            
            # Attach QR code image if provided
            if qr_image:
                try:
                    from email.mime.image import MIMEImage
                    import io
                    
                    # Convert PIL Image to bytes
                    img_buffer = io.BytesIO()
                    qr_image.save(img_buffer, format='PNG')
                    img_buffer.seek(0)
                    
                    # Create MIMEImage
                    img = MIMEImage(img_buffer.read())
                    img.add_header('Content-ID', '<qr_code>')
                    img.add_header('Content-Disposition', 'inline', filename='qr_code.png')
                    msg.attach(img)
                    
                    debug("EmailService", "QR code image attached to email")
                except Exception as e:
                    warning("EmailService", f"Failed to attach QR code: {e}")
            
            # Send email
            debug("EmailService", "Connecting to SMTP server")
            with smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT) as server:
                server.starttls()
                server.login(self.EMAIL_ADDRESS, self.EMAIL_PASSWORD)
                server.send_message(msg)
            
            info("EmailService", f"Backup codes email sent successfully to: {to_email}")
            return True
            
        except Exception as e:
            exception("EmailService", f"Failed to send backup codes email: {e}")
            return False


if __name__ == "__main__":
    # Test email service
    info("TEST", "Testing EmailService...")
    
    service = EmailService()
    
    # Generate code
    code = service.generate_verification_code()
    print(f"Generated code: {code}")
    
    # Test sending (uncomment to actually send)
    # success = service.send_verification_email("test@example.com", "Test User", code)
    # print(f"Email sent: {success}")
    
    info("TEST", "EmailService test completed")
