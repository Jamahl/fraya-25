from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
import logging

from crewai.tools import tool
from pydantic import BaseModel, Field
from functions import mcp2_GMAIL_SEND_EMAIL

class MCPGmailSendInput(BaseModel):
    recipient_email: str = Field(..., description="Email address of recipient")
    body: str = Field(..., description="Email body")
