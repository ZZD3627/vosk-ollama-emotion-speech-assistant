import streamlit as st
from audiorecorder import audiorecorder
import vosk
import wave
import json
import ollama
import logging
from pydub import AudioSegment
from io import BytesIO
from gtts import gTTS

# 初始化日志
logging.basicConfig(level=logging.ERROR)


def generate_story_from(question):
    response = ollama.chat(
        model="llama3.1:latest",  # 确保名称正确
        messages=[{"role": "system",
                   "content": "You are an emotionally intelligent robot that "
                              "recognizes human speech and responds professionally and emotionally based on it"},
                  {"role": "user",
                   "content": question}])

    return response['message']['content']


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


def text_to_speech(text):
    try:
        tts = gTTS(text, lang='zh')
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer
    except Exception as e:
        logging.error(f"将文本转换为语音时出错: {e}")
        return None


st.title('语音识别与回复')

audio = audiorecorder("点击开始录音", "点击停止录音")

if len(audio) > 0:
    audio_path = "audio.wav"
    st.audio(audio.export().read(), autoplay=True)
    audio.export(audio_path, format="wav")

    transcript = convert_speech_to_text(audio_path)
    # engine.say(transcript)
    st.markdown(f"**识别结果:**{transcript}")

    if transcript:
        story = generate_story_from(transcript)
        st.markdown(f"**回复内容:** {story}")

        audio_buffer = text_to_speech(story)
        if audio_buffer:
            st.audio(audio_buffer.read(), format='audio/mp3', start_time=0)
