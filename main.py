import core.whisper as whisper
import core.deepseek as deepseek

# Chiama la funzione main() dal file script.py
prompt = whisper.main()
print("Trascrizione:", prompt)
deepseek.main(prompt)


