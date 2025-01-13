import os
import wave
import base64

from zhipuai import ZhipuAI


class AudioProcessor:
    def __init__(self, api_key=None):
        self.api_key = api_key or self.get_api_key()
        self.client = ZhipuAI(api_key=self.api_key)

    @staticmethod
    def get_api_key():
        api_key = os.getenv("ZHUPUAI_API_KEY")
        if not api_key:
            raise ValueError("API Key is not set. Please set the ZHUPUAI_API_KEY environment variable.")
        return api_key

    def save_audio_as_wav(self, audio_data, filepath):
        with wave.open(filepath, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(44100)
            wav_file.writeframes(audio_data)
        print(f"Audio saved to {filepath}")

    def create_chat_completion(self, audio_base64, audio_format="wav"):
        response = self.client.chat.completions.create(
            model="glm-4-voice",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "你好"
                        },
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": audio_base64,
                                "format": audio_format
                            }
                        }
                    ]
                },
            ],
            max_tokens=1024,
            stream=True
        )
        
        # 处理流式响应
        for chunk in response:
            # 假设每个 chunk 都包含部分的音频数据
            if 'audio' in chunk:
                audio_data = chunk['audio']['data']
                yield base64.b64decode(audio_data)

    def process_audio(self, audio_base64, output_filepath):
        try:
            with open(output_filepath, 'wb') as output_file:
                for audio_chunk in self.create_chat_completion(audio_base64):
                    output_file.write(audio_chunk)
            print(f"Audio saved to {output_filepath}")

        except Exception as e:
            print(f"An error occurred: {e}")


def encode_audio_file(file_path):
    with open(file_path, 'rb') as audio_file:
        audio_data = audio_file.read()
        encoded_data = str(base64.b64encode(audio_data), "utf-8")
        audio_format = os.path.splitext(file_path)[1][1:]  # 获取文件扩展名作为音频格式
        return encoded_data, audio_format


if __name__ == "__main__":
    # 使用示例
    encoded_data, audio_format = encode_audio_file("6254d468e6904b069f4d267cb257ce18.mp3")
    print(encoded_data)

    processor = AudioProcessor()
    # Replace '<base64_string>' with actual base64 encoded audio data
    processor.process_audio(encoded_data, "output.wav")