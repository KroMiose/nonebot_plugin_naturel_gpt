#牛肉酱同款AzureTTS语音服务，支持日语、中文，参数可参考https://learn.microsoft.com/zh-cn/azure/cognitive-services/speech-service/language-support?tabs=tts#supported-languages


from .Extension import Extension
import os
import uuid
from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesisOutputFormat, SpeechSynthesizer, AudioConfig
import re  # 导入re模块，用于正则表达式匹配

# 扩展的配置信息，用于ai理解扩展的功能 *必填*
ext_config: dict = {
    "name": "ext_azuretts",  # 扩展名称，用于标识扩展
    "arguments": {
        "sentence": "str",  # 需要转换的文本
    },
    "description": "when user let you say or speak, you should reply him",
    "refer_word":  ['say', 'speak', 'talk','talking','说','叫','voice','语音'],
    "author": "Fatima",
    "version": "0.0.1",
    "intro": "taking like a human!",
}


class CustomExtension(Extension):
    async def call(self, arg_dict: dict, ctx_data: dict) -> dict:
        custom_config: dict = self.get_custom_config()

        # 设置资源密钥以及区域
        speech_key = custom_config.get('speech_key', '')
        service_region = custom_config.get('service_region', 'eastus')
        voice = custom_config.get('voice', 'en-US-AshleyNeural')   # 设置语音，默认en-US-AshleyNeural
        pitch= custom_config.get('pitch', '26%')         # 设置音调，默认26%
        rate= custom_config.get('rate', '1')             # 设置音速，默认1
        raw_text = arg_dict.get('sentence', None)


        speech_config = SpeechConfig(subscription=speech_key, region=service_region)
        speech_config.speech_synthesis_voice_name = voice
        speech_config.set_speech_synthesis_output_format(SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3)

        # 设置音调和速度

        rate = "1"  # 设置速度

        # 检查 raw_text 是否包含日文字符
        if re.search(r'[\u3040-\u309F\u30A0-\u30FF]', raw_text):
            voice = 'ja-JP-AoiNeural'
            pitch = "20%"  # 当 raw_text 为日文时，设置 pitch 为 "0%"（可更改）
        # 检查 raw_text 是否包含中文字符
        elif re.search(r'[\u4e00-\u9fff]', raw_text):
            voice = 'zh-CN-XiaochenNeural'
            pitch = "35%"  # 当 raw_text 为中文时，设置 pitch 为 "0%"（可更改）

        ssml_pitch = f'<prosody pitch="{pitch}">'
        ssml_rate = f'<prosody rate="{rate}">'
        ssml = f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US"><voice name="{voice}">{ssml_pitch}{ssml_rate}{raw_text}</prosody></prosody></voice></speak>'

        voice_path = 'voice_cache/'
        if not os.path.exists(voice_path):
            os.mkdir(voice_path)
        file_name = f"{voice_path}{uuid.uuid1()}.mp3"
        audio_output = AudioConfig(filename=file_name)
        synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output)

        try:
            # 使用speak_ssml_async替换speak_text_async
            synthesizer.speak_ssml_async(ssml).get()
        except Exception as e:
            print(f"Failed to synthesize voice: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to synthesize voice. Please check your API connection.',
            }

        local_url = f"file:///{os.path.abspath(file_name)}"

        if raw_text is not None:
            return {
                'success': True,
                'voice': local_url,  # 语音url
            }
        return {}

    def __init__(self, custom_config: dict):
        super().__init__(ext_config.copy(), custom_config)
