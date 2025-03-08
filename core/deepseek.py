import ollama
import torch
import subprocess
import json
import re


def load_config(config_path=r"config\config.json"):
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config

def generate_tasks(prompt):
    # Carica il file di configurazione
    config = load_config()
    # Costruisci una stringa che descriva il config
    config_info = ""
    for category, details in config.items():
        commands = details.get("commands", [])
        parameters = details.get("parameters", [])
        config_info += f"{category}: Comandi: {', '.join(commands)}; Parametri: {', '.join(parameters)}\n"
    
    instructive_prompt = (
        "Sei un assistente AI che elabora un comando utente suddividendolo in azioni eseguibili elementari, "
        "insieme alle variabili necessarie per eseguirle, ricorda che le variabili possono essere ottenute con le azioni eseguibili."
        "Analizza il comando e restituisci un JSON valido "
        "con la chiave \"actions\" che è una lista di azioni. Ogni azione deve essere un oggetto con tre chiavi: "
        "\"category\", \"action\" e \"parameters\". "
        "Le categorie possibili sono: Contatti, Spotify, Notion, Email, Calendario, Promemoria, Web, File, Altro.\n"
        "I comandi validi per ciascuna categoria sono definiti nel seguente file di configurazione:\n"
        f"{config_info}\n"
        "Se il comando corrisponde a più azioni, restituisci tutte le azioni in ordine di priorità; "
        "se non corrisponde a nessuna, restituisci un JSON con:\n"
        "{\"actions\": [{\"category\": \"Altro\", \"action\": \"Nessuna azione riconosciuta\", \"parameters\": {}}]}.\n\n"
        "Comando: " + prompt
    )
    
    response = ollama.chat(model="deepseek-r1:14b", messages=[{"role": "user", "content": instructive_prompt}])
    # Debug: stampa la risposta grezza
    #print("Raw response:", response)
    
    content = response.get("message", {}).get("content", "").strip()
    pattern = r"```json(.*?)```"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        json_block = match.group(1).strip()
        try:
            tasks = json.loads(json_block)
            return tasks.get("actions", [])
        except json.JSONDecodeError:
            print("Errore nel parsing del JSON. JSON estratto:", json_block)
            return [{"category": "Altro", "action": "Nessuna azione riconosciuta", "parameters": {}}]
    else:
        print("Nessun blocco JSON trovato nella risposta. Risposta ricevuta:", content)
        return [{"category": "Altro", "action": "Nessuna azione riconosciuta", "parameters": {}}]

def execute_tasks(tasks):
    for task in tasks:
        category = task.get("category", "").lower()
        action = task.get("action", "")
        parameters = task.get("parameters", {})
        if category == "spotify":
            handle_spotify(action, parameters)
        elif category == "notion":
            handle_notion(action, parameters)
        elif category == "email":
            handle_email(action, parameters)
        elif category == "calendario":
            handle_calendar(action, parameters)
        elif category == "promemoria":
            handle_reminder(action, parameters)
        elif category == "web":
            handle_web(action, parameters)
        elif category == "file":
            handle_file(action, parameters)
        elif category == "contatti":
            handle_contacts(action, parameters)
        else:
            handle_other(action, parameters)

# Funzioni placeholder per ciascuna categoria: implementale con la logica reale
def handle_spotify(action, params):
    print(f"[Spotify] Esecuzione: {action} con parametri: {params}")

def handle_notion(action, params):
    print(f"[Notion] Esecuzione: {action} con parametri: {params}")

def handle_email(action, params):
    print(f"[Email] Esecuzione: {action} con parametri: {params}")

def handle_calendar(action, params):
    print(f"[Calendario] Esecuzione: {action} con parametri: {params}")

def handle_reminder(action, params):
    print(f"[Promemoria] Esecuzione: {action} con parametri: {params}")

def handle_web(action, params):
    print(f"[Web] Esecuzione: {action} con parametri: {params}")

def handle_file(action, params):
    print(f"[File] Esecuzione: {action} con parametri: {params}")

def handle_contacts(action, params):
    print(f"[Contatti] Esecuzione: {action} con parametri: {params}")

def handle_other(action, params):
    print(f"[Altro] Azione non riconosciuta: {action} con parametri: {params}")

def stop_deepseek():
    subprocess.run(["ollama", "stop", "deepseek-r1:14b"])

def main(prompt):
    device_used = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Utilizzo dispositivo per deepseek: {device_used}")
    
    tasks = generate_tasks(prompt)
    print("Tasks generati:", tasks)
    
    execute_tasks(tasks)
    
    stop_deepseek()
    print("deepseek-r1:14b dovrebbe essere terminato.")

if __name__ == "__main__":
    # Esempio: comando complesso
    main("Riproduci la mia playlist 856 km, poi alza il volume e infine aggiungi al calenadrio un appuntamento con la psicologa domani alle 18:00")
