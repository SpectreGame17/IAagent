import os
import datetime
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Percorso del file JSON delle credenziali OAuth2 (scaricato dalla Google Cloud Console)
CREDENTIALS_PATH = os.path.join("config", "client_google.json")
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_credentials():
    """Recupera le credenziali dell'utente tramite OAuth2.
    
    Se esistono credenziali salvate (token.pickle), le usa.
    Altrimenti, esegue il flusso di autenticazione e salva le nuove credenziali.
    """
    creds = None
    token_path = os.path.join("config", "token.pickle")  # Salva il token nella cartella config
    
    # Carica il token se esiste
    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)
    
    # Se non ci sono credenziali valide o i permessi sono insufficienti, esegui il flusso OAuth2.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # IMPORTANTE: se cambi gli SCOPES, elimina il file token.pickle per forzare la ri-autenticazione.
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        # Salva le credenziali per usi futuri
        with open(token_path, "wb") as token:
            pickle.dump(creds, token)
    
    return creds

def get_service():
    """Crea e restituisce il servizio Google Calendar utilizzando le credenziali OAuth2."""
    creds = get_credentials()
    return build("calendar", "v3", credentials=creds)

def list_events(calendar_id='primary', max_results=10):
    """Elenca i prossimi eventi dal calendario."""
    service = get_service()
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()  # Usa oggetti timezone-aware
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=now,
        maxResults=max_results,
        singleEvents=True,
        orderBy="startTime"
    ).execute()
    return events_result.get("items", [])

def add_event(summary, start_time, end_time, calendar_id='primary', description=None, location=None):
    """Aggiunge un evento al calendario."""
    service = get_service()
    event = {
        "summary": summary,
        "location": location,
        "description": description,
        "start": {"dateTime": start_time, "timeZone": "Europe/Rome"},
        "end": {"dateTime": end_time, "timeZone": "Europe/Rome"},
    }
    event = service.events().insert(calendarId=calendar_id, body=event).execute()
    return event.get("id")

def delete_event(event_id, calendar_id='primary'):
    """Elimina un evento dal calendario."""
    service = get_service()
    service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
    return True

def update_event(event_id, summary=None, start_time=None, end_time=None, description=None, location=None, calendar_id='primary'):
    """Modifica un evento esistente."""
    service = get_service()
    event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
    if summary:
        event["summary"] = summary
    if start_time:
        event["start"] = {"dateTime": start_time, "timeZone": "Europe/Rome"}
    if end_time:
        event["end"] = {"dateTime": end_time, "timeZone": "Europe/Rome"}
    if description:
        event["description"] = description
    if location:
        event["location"] = location
    updated_event = service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()
    return updated_event

def get_next_event(calendar_id='primary'):
    """Restituisce il prossimo evento in programma."""
    events = list_events(calendar_id, max_results=1)
    return events[0] if events else None

if __name__ == "__main__":
    next_event = get_next_event()
    if next_event:
        # Gestisce eventi con "dateTime" o "date" (eventi a giornata intera)
        start = next_event['start'].get('dateTime', next_event['start'].get('date'))
        print(f"Prossimo evento: {next_event['summary']} alle {start}")
    else:
        print("Nessun evento in programma.")
