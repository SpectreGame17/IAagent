import core.whisper_util as whisper_util
import core.deepseek as deepseek

# Chiama la funzione main() dal file script.py
prompt = whisper_util.main()
print("Trascrizione:", prompt)
deepseek.main(prompt)


