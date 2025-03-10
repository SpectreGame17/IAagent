import os
import sys
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from pydub import AudioSegment
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))

import core.whisper_util
import core.deepseek

# Configurazione base del logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Carica il file .env dalla cartella config
env_path = os.path.join("config", ".env")
load_dotenv(env_path)

# Ottieni il token dal file .env
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Funzione per inviare un messaggio
async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE, messaggio: str):
    if update.message:
        await update.message.reply_text(messaggio)

# Funzione per leggere e restituire il messaggio ricevuto
async def echo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    received_message = update.message.text  # Legge il testo del messaggio
    print(f"Messaggio ricevuto: {received_message}")
    replay = core.deepseek.main(received_message)
    await send_message(update, context, replay)

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

    # Rimuove il file OGG temporaneo, se esiste
    if os.path.exists(file_path):
        os.remove(file_path)

    prompt = core.whisper_util.telegram_input(wav_file_path)
    replay = core.deepseek.main(prompt)
    await send_message(update, context, replay)

    # Opzionale: rimuove anche il file WAV se non serve più
    if os.path.exists(wav_file_path):
        os.remove(wav_file_path)

# Funzione per avviare il bot con il comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ciao! Sono il tuo assistente digitale")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Funzione che gestisce gli errori sollevati durante il processing degli update.
    """
    # Logga l'errore con tutte le informazioni utili
    logger.error("Update caused error: %s", context.error, exc_info=context.error)
    
    # Se possibile, notifica l'utente dell'errore
    if update and update.effective_message:
        try:
            await update.effective_message.reply_text("Ops, qualcosa è andato storto. Riprova più tardi.")
        except Exception as e:
            logger.error("Errore nell'invio del messaggio di notifica: %s", e)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Aggiunge i gestori per i comandi e i messaggi
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_message))
    app.add_handler(MessageHandler(filters.VOICE, receive_voice))
    
    # Registra l'error handler
    app.add_error_handler(error_handler)
    
    # Avvia il bot in modalità polling
    app.run_polling()
    print("Il bot è pronto.")

if __name__ == '__main__':
    main()