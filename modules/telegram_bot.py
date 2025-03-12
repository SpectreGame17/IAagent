import os
import sys
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from pydub import AudioSegment
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))

import core.whisper_util
import core.deepseek

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

env_path = os.path.join("config", ".env")
load_dotenv(env_path)
TOKEN = os.getenv("TELEGRAM_TOKEN")

def process_text_message(text: str) -> str:
    print(f"Messaggio ricevuto: {text}")
    return core.deepseek.main(text)

def process_voice_message(file_path: str) -> str:
    audio = AudioSegment.from_ogg(file_path)
    wav_file_path = 'audio_received.wav'
    audio.export(wav_file_path, format='wav')
    print(f"Audio ricevuto e salvato come {wav_file_path}")
    
    # Rimuove il file OGG temporaneo, se esiste
    if os.path.exists(file_path):
        os.remove(file_path)
    
    prompt = core.whisper_util.telegram_input(wav_file_path)
    response = core.deepseek.main(prompt)
    
    return response

# Funzione per inviare una risposta all'utente
async def echo_message(update, context):
    response = process_text_message(update.message.text)
    await update.message.reply_text(response)

async def receive_voice(update, context):
    voice_file = await update.message.voice.get_file()
    file_path = 'audio_received.ogg'
    await voice_file.download_to_drive(file_path)
    response = process_voice_message(file_path)
    await update.message.reply_text(response)

async def start(update, context):
    await update.message.reply_text("Ciao! Sono il tuo assistente digitale")

async def error_handler(update, context):
    logger.error("Update caused error: %s", context.error, exc_info=context.error)
    if update and update.effective_message:
        try:
            await update.effective_message.reply_text("Ops, qualcosa è andato storto. Riprova più tardi.")
        except Exception as e:
            logger.error("Errore nell'invio del messaggio di notifica: %s", e)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_message))
    app.add_handler(MessageHandler(filters.VOICE, receive_voice))
    app.add_error_handler(error_handler)
    app.run_polling()
    print("Il bot è pronto.")

if __name__ == '__main__':
    main()
