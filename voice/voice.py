from qwen_tts import Qwen3TTSModel
import torch
import soundfile as sf
from utils.logger import get_logger
import datetime
from utils.config_ import config
from models.factory import OllamaChatModel
from utils.prompt_loader import load_prompt

logger = get_logger("Voice")

class VoiceService:
    def __init__(self):
        super().__init__()
        self.model = VoiceService.get_model()
        
    @staticmethod
    def get_model():
        try:
            model = Qwen3TTSModel.from_pretrained(
                "Qwen/Qwen3-TTS-12Hz-0.6B-Base",
                device_map="cuda:0",
                dtype=torch.bfloat16
            )
            logger.info(f"加载模型成功")
        except Exception as e:
            logger.warning(f"加载模型失败, 错误: {str(e)}")
            logger.info("正在尝试加载CPU版本模型...")
            try:
                model = Qwen3TTSModel.from_pretrained(
                    "Qwen/Qwen3-TTS-12Hz-0.6B-Base"
                )
                logger.info(f"加载模型成功")
            except Exception as e:
                logger.error(f"加载模型失败, 错误: {str(e)}")
                raise e
        finally:
            return model
    
    def __get_text(self, text: str) -> str:
        try:
            model = OllamaChatModel().generator(config["models"]["chat_model"])
            logger.info(f"加载模型成功")
            prompt = model.invoke(f"{load_prompt(config["prompts"]["translate4tts_prompt"])}\n{text}").content
            logger.info(f"生成文本成功")
            if config["Debug"]:
                logger.debug(f"生成文本: {prompt}")
            return prompt # pyright: ignore[reportReturnType]
        except Exception as e:
            logger.error(f"加载模型失败, 错误: {str(e)}")
            raise e
    
    def excute(self, text: str) -> str:
        text = self.__get_text(text)
        
        ref_audio = "./voice/sample_2.wav"
        ref_text = "ここにいてもいいでしょ別に，邪魔すいいからさ"

        try:
            wavs, sr = self.model.generate_voice_clone(
                text= text,
                ref_audio= ref_audio,
                ref_text= ref_text,
                language= "Japanese"
            )
            logger.info(f"生成语音成功")
            path = f"{config["file"]["outputs"]}/Voice{datetime.datetime.now().strftime("%Y%m%d-%H.%M.%S")}.wav"
            sf.write(path, wavs[0], sr)
            logger.info(f"保存语音文件成功, 路径: {path}")
            return path
            
        except Exception as e:
            logger.error(f"生成语音失败, 错误: {str(e)}")
            raise e