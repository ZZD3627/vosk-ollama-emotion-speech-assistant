# vosk-ollama-emotion-speech-assistant

[English](https://github.com/ZZD3627/vosk-ollama-emotion-speech-assistant/blob/main/README.md)|[中文简体](https://github.com/ZZD3627/vosk-ollama-emotion-speech-assistant/edit/main/README_CN.md)

###### peculiarity

- VOSK for speech recognition
- ollama3 large model to interact
- gTTS enables voice playback
- Streamlit enables web page access

This code is a Chinese version of the voice intelligent assistant, which will recognize what the user says and realize voice interaction, and can also modify the parameters to achieve English interaction

##### Download the code

```shell
git clone https://github.com/ZZD3627/vosk-ollama-emotion-speech-assistant.git
```

###### Create a virtual environment to run

```shell
python -m venv myvenv
```

###### Execute in a virtual environment

```shell
pip install -r .\requirements.txt
```

######  the code that needs to be modified 1

The model here is changed to your own local ollama model, and the first set of roles and contents is changed to your favorite

```python
def generate_story_from(question):
    response = ollama.chat(
        model="llama3.1:latest",  # Make sure the name is correct
        messages=[{"role": "system",
                   "content": "You are an emotionally intelligent robot that "
                              "recognizes human speech and responds professionally and emotionally based on it"},
                  {"role": "user",
                   "content": question}])

return response['message']['content']
```

###### Where the code needs to be modified 2

model_path changed to your own local path
```python
def convert_speech_to_text(audio_path):
    try:
        # Convert audio to 16-bit PCM WAV using pydub
        audio = AudioSegment.from_wav(audio_path) 	
    
    # Ensure it's mono and 16-bit PCM
    if audio.channels != 1:
        audio = audio.set_channels(1)
    if audio.sample_width != 2:  # 16-bit PCM
        audio = audio.set_sample_width(2)
    if audio.frame_rate != 16000:  # Resample to 16kHz
        audio = audio.set_frame_rate(16000)

    # Export the processed audio back to a WAV file
    processed_audio_path = "processed_audio.wav"
    audio.export(processed_audio_path, format="wav")

    # Load Vosk model for Chinese
    model_path = r"D:\python\model\vosk-model-small-cn-0.22"  # Ensure the model path is correct
    model = vosk.Model(model_path)

    # Open the processed audio file
    with wave.open(processed_audio_path, "rb") as wf:
        # Initialize Vosk recognizer
        rec = vosk.KaldiRecognizer(model, wf.getframerate())

        # Recognize speech
        result = ""
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                result += res.get("text", "")

        # Get final result
        res = json.loads(rec.FinalResult())
        result += res.get("text", "")

    return result

except Exception as e:
    logging.error(f"Error processing audio file {audio_path}: {e}")
    return ""
```

###### Code run (after installing the corresponding package and downloading the model)
```shell
streamlit run app.py
```

