import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from pydub import AudioSegment
from dotenv import load_dotenv

# Carica il file .env dalla cartella config
env_path = os.path.join("config", ".env")
load_dotenv(env_path)

# Ottieni il token dal file .env
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Funzione per inviare un messaggio
async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ciao, sono il tuo bot!")

# Funzione per leggere e restituire il messaggio ricevuto
async def echo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    received_message = update.message.text  # Legge il testo del messaggio
    print(f"Messaggio ricevuto: {received_message}")
    await update.message.reply_text(f"Hai detto: {received_message}")

# Funzione per ricevere un messaggio vocale e salvarlo come file .wav
async def receive_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice_file = await update.message.voice.get_file()  # Ottieni il file audio
    file_path = 'audio_received.ogg'  # Salva temporaneamente come file OGG
    await voice_file.download_to_drive(file_path)

    # Converte il file OGG in WAV
    audio = AudioSegment.from_ogg(file_path)
    wav_file_path = 'audio_received.wav'  # Percorso per il file WAV
    audio.export(wav_file_path, format='wav')
    print(f"Audio ricevuto e salvato come {wav_file_path}")

    # Invia un messaggio di conferma all'utente
    await update.message.reply_text("Audio ricevuto e salvato come file .wav.")
    
    # Rimuovi il file OGG temporaneo
    os.remove(file_path)

# Funzione per avviare il bot con il comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ciao! Sono un bot Telegram.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Aggiungi i gestori per i comandi e i messaggi
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_message))
    app.add_handler(MessageHandler(filters.VOICE, receive_voice))
    
    # Avvia il bot in modalità polling
    app.run_polling()

if __name__ == '__main__':
    main()


#QUESTO È UN TEST DI PROVA DELLE FUNZIONALITA INTEGRERÒ IL MIO CODICE AFFINCHE AUDIO E TESTO VENGANO USATI COME PROMT