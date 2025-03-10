import whisper
import os
import speech_recognition as sr
import torch
from pydub import AudioSegment


def preprocess_audio(audio_path):
    """
    Preprocessa l'audio: imposta 16kHz, mono, 16 bit.
    """
    audio = AudioSegment.from_file(audio_path)
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
    output_path = "processed_audio.wav"
    audio.export(output_path, format="wav")
    return output_path
   
def telegram_input(audio_path):

    # Imposta il dispositivo per Whisper
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Utilizzo dispositivo per Whisper: {device}")

    # Carica il modello Whisper specificando il linguaggio italiano
    model = whisper.load_model("large", device=device)

    # Se il file audio esiste
    if audio_path:

        #processa il file audio
        processed_audio_path = preprocess_audio(audio_path)

        #Lo converte in testo
        audio = whisper.load_audio(processed_audio_path)
        result = model.transcribe(audio, language="it")
        transcription = result['text']

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
