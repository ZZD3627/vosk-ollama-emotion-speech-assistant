from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
import os
import json
import logging
from pydub import AudioSegment
import wave
import vosk
import ollama

# 初始化日志
logging.basicConfig(level=logging.ERROR)

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 启用 CORS，允许所有来源
CORS(app, resources={r"/*": {"origins": "*"}})

# 配置允许的跨域来源
origins = [
    "http://127.0.0.1",  # 本地前端
    "http://127.0.0.1:5000",  # 如果使用 VS Code Live Server
    "http://127.0.0.1:8000",  # 如果使用 VS Code Live Server
    "http://localhost",  # 本地前端
    "http://localhost:5000"  # 本地开发时的 URL
    "http://localhost:8000"  # 本地开发时的 URL
]

MODEL_PATH = r"D:\python\model\vosk-model-small-cn-0.22"  # 请修改为你的模型路径

# 存储用户的历史对话
user_conversations = {}

# 场景定义，包含每个场景的 `system` 内容
SCENE_DESCRIPTIONS = {
    "cute": "You are a cute and highly emotional intelligent pet (chick), very smart and always full of energy.",
    "lovely": "You are a lovely and caring teacher, always supportive and friendly.",
    "sweet_girl": "You are a sweet and charming girl, with a gentle voice and warm responses.",
    "tough_guy": "You are a tough guy, confident, strong, and always straightforward in your responses."
}


def save_wav(filename, audio_data, sample_rate):
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)  # 设置为单声道
        wav_file.setsampwidth(2)  # 设置样本宽度为2字节（16位）
        wav_file.setframerate(sample_rate)  # 设置采样率
        wav_file.writeframes(audio_data)  # 写入音频数据


@app.before_request
def handle_options():
    if request.method == "OPTIONS":
        return "", 200  # 响应 200 状态码


@app.after_request
def add_cors_headers(response):
    # 添加 CORS 头部到响应
    response.headers["Access-Control-Allow-Origin"] = "*"  # 或指定前端地址
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.route("/some-endpoint", methods=["GET", "POST", "OPTIONS"])
def some_endpoint():
    return jsonify(message="Hello, world!")


@app.route('/dialogue', methods=['POST'])
def upload_file():
    if 'audio' not in request.files:
        return jsonify({"message": "没有文件上传"}), 400

    user_id = request.form.get('user_id')
    scene = request.form.get('scene')  # 前端传来的场景类型
    file = request.files['audio']
    if file.filename == '':
        return jsonify({"message": "没有选择文件"}), 400
    file_name = user_id + file.filename
    file_path = os.path.join(UPLOAD_FOLDER, file_name)
    file.save(file_path)

    transcript = convert_speech_to_text(file_path)

    os.remove(file_path)
    if not transcript:
        return jsonify({"message": "语音识别失败"}), 500

        # 获取或创建用户的历史对话记录
    if user_id not in user_conversations:
        user_conversations[user_id] = []

        # 获取对应场景的 system 描述
    system_content = SCENE_DESCRIPTIONS.get(scene, "You are an emotionally intelligent robot.")

    user_history = user_conversations[user_id] + [
        {"role": "system", "content": system_content},
        {"role": "user", "content": transcript}
    ]

    # 生成机器人的回复
    reply = generate_story_from(user_history)

    if not reply:
        return jsonify({"message": "生成回复失败"}), 500

        # 返回 JSON 数据
    response = {"transcript": transcript,
                "reply": reply,
                "message": "处理成功"}

    return jsonify(response), 200

def generate_story_from(history):
    """调用 Ollama API 生成回复"""
    try:
        simplified_history = simplify_history(history)
        response = ollama.chat(
            model="llama3.1:latest",  # 确保模型名称正确
            messages=simplified_history
        )
        return response['message']['content']
    except Exception as e:
        logging.error(f"Ollama API 调用出错: {e}")
        return "抱歉，我无法处理您的请求。"

def simplify_history(history):
    """简化对话历史，只保留前几个用户和机器人的互动"""
    max_history = 5  # 设置最大对话历史长度
    return history[-max_history:]


def convert_speech_to_text(audio_path):
    """将 wav 文件转换为文本"""
    try:
        # 加载 vosk 模型（这里使用的是英语模型路径，你需要根据实际情况替换）
        model = vosk.Model(MODEL_PATH)

        # 检查文件路径是否存在
        if not os.path.exists(audio_path):
            print(f"文件 {audio_path} 不存在!")
            return ""

        processed_audio_path = "processed_audio_001.wav"

        # 使用 pydub 尝试修复音频文件（解决 RIFF 错误）
        # 尝试将音频文件加载为 pydub AudioSegment 对象
        audio = AudioSegment.from_file(audio_path)
        if audio.channels != 1:
            audio = audio.set_channels(1)
        if audio.sample_width != 2:
            audio = audio.set_sample_width(2)
        if audio.frame_rate != 16000:
            audio = audio.set_frame_rate(16000)
        # 转换为正确的 wav 格式
        audio.export(processed_audio_path, format="wav")

        with wave.open(processed_audio_path, "rb") as wf:
            rec = vosk.KaldiRecognizer(model, wf.getframerate())
            result = ""
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    res = json.loads(rec.Result())
                    result += res.get("text", "")
            res = json.loads(rec.FinalResult())
            result += res.get("text", "")

        return result

    except Exception as e:
        print(f"处理音频文件 {audio_path} 时出错: {e}")
        return ""


if __name__ == '__main__':
    app.run(debug=True, port=5000)
