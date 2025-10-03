"""
Notification Service for sending alerts via email/WhatsApp/Telegram
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

class NotificationService:
    """Service for sending notifications"""
    
    def __init__(self):
        self.smtp_configured = all([
            Config.SMTP_HOST,
            Config.SMTP_USER,
            Config.SMTP_PASSWORD
        ])
    
    def send_email(self, to_email, subject, body, html_body=None):
        """Send email notification"""
        if not self.smtp_configured:
            print("SMTP not configured - email not sent")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = Config.SMTP_USER
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add plain text
            msg.attach(MIMEText(body, 'plain'))
            
            # Add HTML if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Connect and send
            with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT) as server:
                server.starttls()
                server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
                server.send_message(msg)
            
            print(f"Email sent to {to_email}")
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def send_delay_alert(self, delivery):
        """Send alert for delayed delivery"""
        subject = f"Delivery Delay Alert - {delivery.purchase_order.po_ref}"
        
        body = f"""
Delivery Delay Alert

PO Reference: {delivery.purchase_order.po_ref}
Material: {delivery.purchase_order.material.material_type}
Expected Date: {delivery.expected_delivery_date.strftime('%Y-%m-%d') if delivery.expected_delivery_date else 'N/A'}
Delay: {delivery.delay_days} days
Status: {delivery.delivery_status}
Reason: {delivery.delay_reason or 'Not specified'}

Please take appropriate action.
"""
        
        html_body = f"""
<html>
<body>
    <h2 style="color: #dc3545;">Delivery Delay Alert</h2>
    <table style="border-collapse: collapse; width: 100%;">
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>PO Reference:</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd;">{delivery.purchase_order.po_ref}</td>
        </tr>
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Material:</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd;">{delivery.purchase_order.material.material_type}</td>
        </tr>
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Expected Date:</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd;">{delivery.expected_delivery_date.strftime('%Y-%m-%d') if delivery.expected_delivery_date else 'N/A'}</td>
        </tr>
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Delay:</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd; color: #dc3545;"><strong>{delivery.delay_days} days</strong></td>
        </tr>
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;"><strong>Status:</strong></td>
            <td style="padding: 8px; border: 1px solid #ddd;">{delivery.delivery_status}</td>
        </tr>
    </table>
    <p style="margin-top: 20px;">Please take appropriate action.</p>
</body>
</html>
"""
        
        if Config.NOTIFICATION_EMAIL:
            return self.send_email(Config.NOTIFICATION_EMAIL, subject, body, html_body)
        return False
    
    def send_ai_suggestion_alert(self, suggestion):
        """Send alert for new AI suggestion requiring review"""
        subject = f"AI Suggestion Requires Review - Confidence: {suggestion.confidence_score}%"
        
        body = f"""
New AI Suggestion Requires Review

Target: {suggestion.target_table}
Action: {suggestion.action_type}
Confidence: {suggestion.confidence_score}%
Source: {suggestion.extraction_source}
AI Model: {suggestion.ai_model}

Reasoning: {suggestion.ai_reasoning}

Please review this suggestion in the dashboard.
"""
        
        if Config.NOTIFICATION_EMAIL:
            return self.send_email(Config.NOTIFICATION_EMAIL, subject, body)
        return False
    
    def send_approval_reminder(self, material):
        """Send reminder for pending material approvals"""
        subject = f"Material Approval Pending - {material.material_type}"
        
        body = f"""
Material Approval Pending

Material: {material.material_type}
Status: {material.approval_status}
Submittal Ref: {material.submittal_ref or 'N/A'}

Please review and approve/reject this material.
"""
        
        if Config.NOTIFICATION_EMAIL:
            return self.send_email(Config.NOTIFICATION_EMAIL, subject, body)
        return False
    
    def send_payment_reminder(self, payment):
        """Send payment reminder"""
        subject = f"Payment Reminder - {payment.purchase_order.po_ref}"
        
        body = f"""
Payment Reminder

PO Reference: {payment.purchase_order.po_ref}
Supplier: {payment.purchase_order.supplier_name}
Total Amount: {Config.CURRENCY} {payment.total_amount:,.2f}
Paid Amount: {Config.CURRENCY} {payment.paid_amount:,.2f}
Remaining: {Config.CURRENCY} {(payment.total_amount - payment.paid_amount):,.2f}
Payment Status: {payment.payment_status}

Please process the payment.
"""
        
        if Config.NOTIFICATION_EMAIL:
            return self.send_email(Config.NOTIFICATION_EMAIL, subject, body)
        return False
    
    # Placeholder methods for WhatsApp and Telegram
    # These would need to be implemented with respective APIs
    
    def send_whatsapp(self, phone, message):
        """Send WhatsApp notification (requires WhatsApp Business API)"""
        # Implement with WhatsApp Business API or n8n integration
        print(f"WhatsApp notification to {phone}: {message}")
        return False
    
    def send_telegram(self, chat_id, message):
        """Send Telegram notification (requires Telegram Bot API)"""
        # Implement with Telegram Bot API or n8n integration
        print(f"Telegram notification to {chat_id}: {message}")
        return False
