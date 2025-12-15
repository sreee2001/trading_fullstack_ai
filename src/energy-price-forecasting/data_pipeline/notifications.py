"""
Notification system for data pipeline events.

Supports email and Slack notifications for pipeline status updates.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
import requests

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending pipeline notifications."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize notification service.
        
        Args:
            config: Configuration dictionary from pipeline_config.yaml
        """
        self.config = config
        self.email_config = config.get('notifications', {}).get('email', {})
        self.slack_config = config.get('notifications', {}).get('slack', {})
    
    def send_notification(
        self,
        status: str,
        summary: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Send notification about pipeline execution.
        
        Args:
            status: Execution status (SUCCESS, PARTIAL_SUCCESS, FAILED)
            summary: Summary text
            details: Additional details dictionary
        """
        should_send = self._should_send_notification(status)
        
        if not should_send:
            logger.debug(f"Notifications disabled for status: {status}")
            return
        
        # Send email if enabled
        if self.email_config.get('enabled', False):
            try:
                self._send_email(status, summary, details)
                logger.info("Email notification sent successfully")
            except Exception as e:
                logger.error(f"Failed to send email notification: {e}")
        
        # Send Slack message if enabled
        if self.slack_config.get('enabled', False):
            try:
                self._send_slack(status, summary, details)
                logger.info("Slack notification sent successfully")
            except Exception as e:
                logger.error(f"Failed to send Slack notification: {e}")
    
    def _should_send_notification(self, status: str) -> bool:
        """Determine if notification should be sent based on status."""
        status_lower = status.lower()
        
        # Check email settings
        if self.email_config.get('enabled', False):
            if status_lower == 'success' and self.email_config.get('send_on_success', False):
                return True
            if status_lower == 'failed' and self.email_config.get('send_on_failure', True):
                return True
            if status_lower == 'partial_success' and self.email_config.get('send_on_partial', True):
                return True
        
        # Check Slack settings
        if self.slack_config.get('enabled', False):
            if status_lower == 'success' and self.slack_config.get('send_on_success', False):
                return True
            if status_lower == 'failed' and self.slack_config.get('send_on_failure', True):
                return True
            if status_lower == 'partial_success' and self.slack_config.get('send_on_partial', True):
                return True
        
        return False
    
    def _send_email(
        self,
        status: str,
        summary: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Send email notification."""
        # Get email credentials from environment
        smtp_user = os.getenv('SMTP_USER', self.email_config.get('from_email'))
        smtp_password = os.getenv('SMTP_PASSWORD')
        
        if not smtp_password:
            logger.warning("SMTP_PASSWORD not set, skipping email notification")
            return
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Pipeline Alert: {status}"
        msg['From'] = smtp_user
        msg['To'] = ', '.join(self.email_config.get('to_emails', []))
        
        # Create email body
        body = self._format_email_body(status, summary, details)
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        with smtplib.SMTP(
            self.email_config.get('smtp_server'),
            self.email_config.get('smtp_port', 587)
        ) as server:
            if self.email_config.get('use_tls', True):
                server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
    
    def _send_slack(
        self,
        status: str,
        summary: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Send Slack notification."""
        webhook_url = self.slack_config.get('webhook_url')
        
        if not webhook_url:
            logger.warning("Slack webhook URL not configured")
            return
        
        # Determine color based on status
        color_map = {
            'SUCCESS': '#36a64f',  # Green
            'PARTIAL_SUCCESS': '#ff9900',  # Orange
            'FAILED': '#ff0000'  # Red
        }
        color = color_map.get(status.upper(), '#808080')
        
        # Format message
        message = {
            'attachments': [
                {
                    'color': color,
                    'title': f'Data Pipeline: {status}',
                    'text': summary,
                    'footer': 'Energy Price Forecasting Pipeline',
                    'ts': int(details.get('timestamp', 0)) if details else 0
                }
            ]
        }
        
        # Add fields if details provided
        if details:
            fields = []
            if 'records_fetched' in details:
                fields.append({
                    'title': 'Records Fetched',
                    'value': str(sum(details['records_fetched'].values())),
                    'short': True
                })
            if 'records_stored' in details:
                fields.append({
                    'title': 'Records Stored',
                    'value': str(sum(details['records_stored'].values())),
                    'short': True
                })
            
            message['attachments'][0]['fields'] = fields
        
        # Send request
        response = requests.post(webhook_url, json=message, timeout=10)
        response.raise_for_status()
    
    def _format_email_body(
        self,
        status: str,
        summary: str,
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        """Format email notification body."""
        body = f"""
Energy Price Data Pipeline Notification

Status: {status}

{summary}
"""
        
        if details:
            body += "\n\nDetails:\n"
            for key, value in details.items():
                body += f"  {key}: {value}\n"
        
        body += "\n\n-- \nThis is an automated message from the Energy Price Forecasting System."
        
        return body


def send_error_notification(
    config: Dict[str, Any],
    error: Exception,
    context: Optional[str] = None
):
    """
    Send notification about an error.
    
    Args:
        config: Pipeline configuration
        error: The exception that occurred
        context: Additional context about where the error occurred
    """
    notification_service = NotificationService(config)
    
    summary = f"Pipeline Error: {type(error).__name__}"
    if context:
        summary += f" ({context})"
    
    details = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'context': context or 'Unknown'
    }
    
    notification_service.send_notification(
        status='FAILED',
        summary=summary,
        details=details
    )

