import os
import base64
import json
import pickle
from typing import List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.send"]
TOKEN_PATH = "token.pickle"
CREDENTIALS_PATH = os.path.join("config", "client_google.json")



def authenticate():
    """Autentica l'utente e restituisce il servizio Gmail."""
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "wb") as token:
            pickle.dump(creds, token)
    return build("gmail", "v1", credentials=creds)


def get_recent_emails(max_results: int = 5) -> List[dict]:
    """Legge le ultime email ricevute."""
    service = authenticate()
    results = service.users().messages().list(userId="me", maxResults=max_results).execute()
    messages = results.get("messages", [])
    emails = []

    for msg in messages:
        msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
        payload = msg_data.get("payload", {})
        headers = payload.get("headers", [])
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "(No Subject)")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown")
        snippet = msg_data.get("snippet", "")
        emails.append({"from": sender, "subject": subject, "snippet": snippet})

    return emails


def get_email_from_sender(sender_email: str) -> Optional[dict]:
    """Trova l'ultima email ricevuta da un mittente specifico."""
    service = authenticate()
    results = service.users().messages().list(userId="me", q=f"from:{sender_email}", maxResults=1).execute()
    messages = results.get("messages", [])

    if not messages:
        return None

    msg_data = service.users().messages().get(userId="me", id=messages[0]["id"]).execute()
    payload = msg_data.get("payload", {})
    headers = payload.get("headers", [])
    subject = next((h["value"] for h in headers if h["name"] == "Subject"), "(No Subject)")
    snippet = msg_data.get("snippet", "")
    return {"from": sender_email, "subject": subject, "snippet": snippet}


def send_email(to: str, subject: str, body: str) -> None:
    """Invia un'email."""
    service = authenticate()
    message = {
        "raw": base64.urlsafe_b64encode(f"From: me\nTo: {to}\nSubject: {subject}\n\n{body}".encode("utf-8")).decode("utf-8")
    }
    service.users().messages().send(userId="me", body=message).execute()


def search_emails(query: str, max_results: int = 5) -> List[dict]:
    """Cerca email in base a una query (es. 'subject:Report')."""
    service = authenticate()
    results = service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
    messages = results.get("messages", [])
    emails = []
    
    for msg in messages:
        msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
        payload = msg_data.get("payload", {})
        headers = payload.get("headers", [])
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "(No Subject)")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown")
        snippet = msg_data.get("snippet", "")
        emails.append({"from": sender, "subject": subject, "snippet": snippet})

    return emails


def mark_email_as_read(email_id: str) -> None:
    """Segna un'email come letta."""
    service = authenticate()
    service.users().messages().modify(userId="me", id=email_id, body={"removeLabelIds": ["UNREAD"]}).execute()

if __name__ == "__main__":
    send_email("demusso1617@gmail.com", "test IA", "questa è un email di test")
