import threading
import whisper
import os
import speech_recognition as sr
import torch
from pydub import AudioSegment
import io

# Imposta il dispositivo per Whisper
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Utilizzo dispositivo per Whisper: {device}")

# Carica il modello Whisper specificando il linguaggio italiano
model = whisper.load_model("large", device=device)

# Evento per fermare la registrazione se viene premuto Invio
stop_event = threading.Event()

def check_for_stop():
    input("Premi Invio per terminare la registrazione in qualsiasi momento...\n")
    stop_event.set()

def record_audio_to_file():
    """
    Registra continuamente audio in segmenti finché non viene rilevato silenzio prolungato
    oppure si preme Invio. I segmenti vengono uniti e salvati in un file WAV.
    """
    recognizer = sr.Recognizer()
    audio_segments = []
    silent_counter = 0
    silence_limit = 2  # Se si hanno 2 timeout consecutivi, si ferma la registrazione

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Parla... La registrazione continuerà finché non viene rilevato silenzio prolungato o premi Invio per fermare.")

        # Avvia un thread che aspetta l'input dell'utente per fermare la registrazione
        stop_thread = threading.Thread(target=check_for_stop)
        stop_thread.daemon = True
        stop_thread.start()

        while not stop_event.is_set():
            try:
                # Registra un segmento con timeout di 5 secondi e durata massima di 10 secondi
                audio_chunk = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                silent_counter = 0  # Reset se viene catturato audio

                # Utilizza i parametri originali per evitare rallentamenti nel parlato
                audio_data = audio_chunk.get_wav_data()
                segment = AudioSegment(
                    data=audio_data,
                    sample_width=audio_chunk.sample_width,
                    frame_rate=audio_chunk.sample_rate,
                    channels=1
                )
                audio_segments.append(segment)
                print("Segmento registrato.")
            except sr.WaitTimeoutError:
                silent_counter += 1
                print(f"Silenzio rilevato ({silent_counter}/{silence_limit})...")
                if silent_counter >= silence_limit:
                    print("Silenzio prolungato, terminazione della registrazione.")
                    break

    if audio_segments:
        combined_audio = audio_segments[0]
        for segment in audio_segments[1:]:
            combined_audio += segment

        output_path = "temp_audio.wav"
        combined_audio.export(output_path, format="wav")
        return output_path
    else:
        print("Nessun audio registrato.")
        return None

def preprocess_audio(audio_path):
    """
    Preprocessa l'audio: imposta 16kHz, mono, 16 bit.
    """
    audio = AudioSegment.from_file(audio_path)
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
    output_path = "processed_audio.wav"
    audio.export(output_path, format="wav")
    return output_path

def transcribe_audio(audio_path):
    """
    Carica l'audio e utilizza Whisper per trascrivere in italiano,
    specificando il linguaggio con language="it".
    """
    audio = whisper.load_audio(audio_path)
    result = model.transcribe(audio, language="it")
    return result['text']

def user_input():
    audio_path = record_audio_to_file()
    if audio_path:
        processed_audio_path = preprocess_audio(audio_path)
        transcription = transcribe_audio(processed_audio_path)

         # Rimuove i file temporanei
        if os.path.exists(audio_path):
            os.remove(audio_path)
        if os.path.exists(processed_audio_path):
            os.remove(processed_audio_path)
     

        # Sposta il modello sulla CPU e libera la cache GPU
        model.to("cpu")
        torch.cuda.empty_cache()
        print("Modello spostato sulla CPU e GPU svuotata.")
        return transcription
    else:
        transcription = None
        return transcription
    
def telegram_input(audio_path):
    if audio_path:
        processed_audio_path = preprocess_audio(audio_path)
        transcription = transcribe_audio(processed_audio_path)

         # Rimuove i file temporanei
        if os.path.exists(audio_path):
            os.remove(audio_path)
        if os.path.exists(processed_audio_path):
            os.remove(processed_audio_path)
     

        # Sposta il modello sulla CPU e libera la cache GPU
        model.to("cpu")
        torch.cuda.empty_cache()
        print("Modello spostato sulla CPU e GPU svuotata.")
        return transcription
    else:
        transcription = None
        return transcription

if __name__ == "__main__":
    result = user_input()
    print("Trascrizione:", result)