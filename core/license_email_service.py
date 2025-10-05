"""
License Email Service
Handles email notifications for license system
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from .debug_logger import debug, info, warning, error

class LicenseEmailService:
    """
    Email service for license notifications
    """
    
    def __init__(self, smtp_server="smtp.gmail.com", smtp_port=587, sender_email=None, sender_password=None):
        """Initialize email service"""
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email or "MultiTeamCommunication@gmail.com"
        self.sender_password = sender_password or "guom hlwv ousw mkhz"  # Gmail App Password
        
        info("LicenseEmail", "License email service initialized")
    
    def send_application_confirmation(self, to_email: str, name: str, tier: str, machine_uid: str) -> bool:
        """
        Send confirmation email when application is submitted
        
        Args:
            to_email: Recipient email
            name: Applicant name
            tier: Requested tier
            machine_uid: Machine UID
            
        Returns:
            bool: Success
        """
        subject = "License Application Received - MultiTeam Communication"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2d7a2d;">License Application Received</h2>
                
                <p>Dear {name},</p>
                
                <p>Thank you for applying for a MultiTeam Communication license!</p>
                
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Application Details:</h3>
                    <p><strong>Requested Tier:</strong> {tier.title()}</p>
                    <p><strong>Machine ID:</strong> {machine_uid}</p>
                    <p><strong>Submitted:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
                    <p><strong>Status:</strong> Pending Review</p>
                </div>
                
                <p>Your application is now being reviewed by our team. You will receive another email once your application has been processed.</p>
                
                <p>This typically takes 1-2 business days.</p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                
                <p style="font-size: 12px; color: #666;">
                    If you have any questions, please contact us at support@multiteam.com
                </p>
                
                <p style="font-size: 12px; color: #666;">
                    Best regards,<br>
                    The MultiTeam Team
                </p>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(to_email, subject, html_body)
    
    def send_approval_notification(self, to_email: str, name: str, tier: str, license_key: str) -> bool:
        """
        Send email when application is approved with license key
        
        Args:
            to_email: Recipient email
            name: Applicant name
            tier: Approved tier
            license_key: Generated license key
            
        Returns:
            bool: Success
        """
        subject = "License Approved - Your License Key - MultiTeam Communication"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2d7a2d;">🎉 License Application Approved!</h2>
                
                <p>Dear {name},</p>
                
                <p>Great news! Your license application has been approved.</p>
                
                <div style="background-color: #e8f5e9; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #2d7a2d;">
                    <h3 style="margin-top: 0; color: #2d7a2d;">Your License Key:</h3>
                    <p style="font-size: 24px; font-weight: bold; letter-spacing: 2px; color: #2d7a2d; text-align: center; padding: 10px; background: white; border-radius: 3px;">
                        {license_key}
                    </p>
                </div>
                
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">License Details:</h3>
                    <p><strong>Tier:</strong> {tier.title()}</p>
                    <p><strong>Status:</strong> Active</p>
                    <p><strong>Issued:</strong> {datetime.now().strftime("%Y-%m-%d")}</p>
                </div>
                
                <h3>How to Activate:</h3>
                <ol>
                    <li>Open MultiTeam Communication application</li>
                    <li>Click "Enter License Key" on the activation screen</li>
                    <li>Enter the license key above</li>
                    <li>Click "Activate"</li>
                </ol>
                
                <p><strong>Important:</strong> Please save this email for your records. You will need this license key to activate your software.</p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                
                <p style="font-size: 12px; color: #666;">
                    If you have any questions or need assistance, please contact us at support@multiteam.com
                </p>
                
                <p style="font-size: 12px; color: #666;">
                    Thank you for choosing MultiTeam Communication!<br>
                    The MultiTeam Team
                </p>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(to_email, subject, html_body)
    
    def send_rejection_notification(self, to_email: str, name: str, reason: str = None) -> bool:
        """
        Send email when application is rejected
        
        Args:
            to_email: Recipient email
            name: Applicant name
            reason: Rejection reason (optional)
            
        Returns:
            bool: Success
        """
        subject = "License Application Update - MultiTeam Communication"
        
        reason_text = f"<p><strong>Reason:</strong> {reason}</p>" if reason else ""
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #c42b1c;">License Application Update</h2>
                
                <p>Dear {name},</p>
                
                <p>Thank you for your interest in MultiTeam Communication.</p>
                
                <p>After reviewing your application, we regret to inform you that we are unable to approve your license request at this time.</p>
                
                {reason_text}
                
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #f7630c;">
                    <p style="margin: 0;"><strong>Alternative Options:</strong></p>
                    <ul style="margin: 10px 0;">
                        <li>You can still use our 30-day free trial</li>
                        <li>Contact us to discuss your requirements</li>
                        <li>Reapply with updated information</li>
                    </ul>
                </div>
                
                <p>If you have any questions or would like to discuss this decision, please don't hesitate to contact us.</p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                
                <p style="font-size: 12px; color: #666;">
                    Contact us at support@multiteam.com for more information
                </p>
                
                <p style="font-size: 12px; color: #666;">
                    Best regards,<br>
                    The MultiTeam Team
                </p>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(to_email, subject, html_body)
    
    def send_payment_confirmation(self, to_email: str, name: str, tier: str, amount: float, transaction_id: str) -> bool:
        """
        Send payment confirmation email
        
        Args:
            to_email: Recipient email
            name: Customer name
            tier: License tier
            amount: Payment amount
            transaction_id: Transaction ID
            
        Returns:
            bool: Success
        """
        subject = "Payment Confirmed - MultiTeam Communication"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2d7a2d;">Payment Confirmed</h2>
                
                <p>Dear {name},</p>
                
                <p>Thank you for your payment! Your transaction has been processed successfully.</p>
                
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Payment Details:</h3>
                    <p><strong>License Tier:</strong> {tier.title()}</p>
                    <p><strong>Amount:</strong> ${amount:.2f}</p>
                    <p><strong>Transaction ID:</strong> {transaction_id}</p>
                    <p><strong>Date:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
                </div>
                
                <p>Your license will be activated shortly. You will receive another email with your license key within a few minutes.</p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                
                <p style="font-size: 12px; color: #666;">
                    If you have any questions about your payment, please contact us at billing@multiteam.com
                </p>
                
                <p style="font-size: 12px; color: #666;">
                    Thank you for your business!<br>
                    The MultiTeam Team
                </p>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(to_email, subject, html_body)
    
    def _send_email(self, to_email: str, subject: str, html_body: str) -> bool:
        """
        Internal method to send email
        
        Args:
            to_email: Recipient email
            subject: Email subject
            html_body: HTML email body
            
        Returns:
            bool: Success
        """
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = to_email
            
            # Add HTML body
            html_part = MIMEText(html_body, "html")
            message.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            info("LicenseEmail", f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            error("LicenseEmail", f"Failed to send email to {to_email}: {e}")
            return False


# Debug logging
debug("LicenseEmail", "License email service module loaded")
