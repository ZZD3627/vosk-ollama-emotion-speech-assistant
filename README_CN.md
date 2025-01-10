# vosk-ollama-emotion-speech-assistant

[English](https://github.com/ZZD3627/vosk-ollama-emotion-speech-assistant/blob/main/README.md)|[中文简体](https://github.com/ZZD3627/vosk-ollama-emotion-speech-assistant/edit/main/README_CN.md)

###### 特点

- vosk进行语音识别
- ollama3大模型进行交互
- gTTS实现语音的播放
- streamlit实现网页访问

此代码是中文版本的语音智能助手，会识别用户所说的话，并实现语音交互

##### 下载代码

```shell
git clone https://github.com/ZZD3627/vosk-ollama-emotion-speech-assistant.git
```

###### 创建虚拟环境运行

```shell
python -m venv myvenv
```

###### 在虚拟环境中执行

```shell
pip install -r .\requirements.txt
```

###### 代码中需要修改的地方1

此处的model改成自己本地的ollama model,第一组role和content改成自己喜欢的

```python
def generate_story_from(question):
    response = ollama.chat(
        model="llama3.1:latest",  # 确保名称正确
        messages=[{"role": "system",
                   "content": "You are an emotionally intelligent robot that "
                              "recognizes human speech and responds professionally and emotionally based on it"},
                  {"role": "user",
                   "content": question}])

return response['message']['content']
```

###### 代码中需要修改的地方2

model_path改成自己本地的path

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

###### 代码运行（在安装了对应的包和下载了模型后）

```shell
streamlit run app.py
```
###### 使用flask实现后端API语音交互
[dialogue.py](app%2Fdialogue.py)

###### 效果演示
[效果演示](https://www.bilibili.com/video/BV1MmCBYqEF4/)

