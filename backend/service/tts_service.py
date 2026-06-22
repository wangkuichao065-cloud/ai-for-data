"""TTS 服务 — IndexTTS2 语音合成 + 降级方案"""
import os
import uuid
import time
import asyncio
from pathlib import Path
import config
from utils.logger import get_logger

logger = get_logger()

_tts_model = None
_tts_loading = False


def _is_indextts_available() -> bool:
    """检查 IndexTTS2 是否可用（checkpoints 目录存在 config.yaml）"""
    return os.path.exists(config.INDEXTTS_CFG)


async def _load_tts_model():
    """懒加载 IndexTTS2 模型（8GB 显存按需加载）"""
    global _tts_model, _tts_loading
    if _tts_model is not None or _tts_loading:
        return _tts_model

    if not _is_indextts_available():
        logger.warning("IndexTTS2 模型未找到 ({}), TTS 功能将使用降级模式", config.INDEXTTS_CFG)
        return None

    _tts_loading = True
    try:
        # 在线程池中加载模型（避免阻塞事件循环）
        def _load():
            from indextts.infer_v2 import IndexTTS2
            return IndexTTS2(
                cfg_path=config.INDEXTTS_CFG,
                model_dir=config.INDEXTTS_CHECKPOINTS,
                use_fp16=config.INDEXTTS_USE_FP16,
                use_cuda_kernel=config.INDEXTTS_USE_CUDA,
                use_deepspeed=False,
            )

        loop = asyncio.get_event_loop()
        _tts_model = await loop.run_in_executor(None, _load)
        logger.info("IndexTTS2 模型加载完成")
    except Exception as e:
        logger.error("IndexTTS2 加载失败: {}", e)
        _tts_model = None
    finally:
        _tts_loading = False

    return _tts_model


async def generate_speech(text: str, voice: str = "default", speed: float = 1.0,
                          emotion: str = None) -> dict:
    """生成语音文件

    Args:
        text: 要合成的文本
        voice: 音色（目前使用预设参考音频，后续可扩展）
        speed: 语速（1.0 = 正常）
        emotion: 情绪（happy/sad/angry/neutral）

    Returns:
        dict: audio_url, duration_ms, format
    """
    model = await _load_tts_model()

    if model is None:
        # 降级：返回空音频或使用 edge-tts
        return await _fallback_tts(text, speed)

    # IndexTTS2 生成
    audio_name = f"tts_{uuid.uuid4().hex[:12]}.wav"
    audio_path = Path(config.STATIC_DIR) / "voice" / audio_name
    audio_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        def _infer():
            kwargs = {
                "spk_audio_prompt": config.INDEXTTS_VOICE_PROMPT,
                "text": text,
                "output_path": str(audio_path),
                "verbose": False,
            }
            # 情绪控制
            if emotion:
                emotion_map = {
                    "happy": [1, 0, 0, 0, 0, 0, 0, 0],
                    "angry": [0, 1, 0, 0, 0, 0, 0, 0],
                    "sad": [0, 0, 1, 0, 0, 0, 0, 0],
                    "afraid": [0, 0, 0, 1, 0, 0, 0, 0],
                    "neutral": [0, 0, 0, 0, 0, 0, 0, 1],
                }
                vec = emotion_map.get(emotion, [0, 0, 0, 0, 0, 0, 0, 1])
                kwargs["emo_vector"] = vec
                kwargs["use_random"] = False
            model.infer(**kwargs)

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _infer)

        # 获取音频时长
        duration_ms = _get_audio_duration(audio_path)

        logger.info("IndexTTS2 语音生成完成: {} ({}ms)", audio_name, duration_ms)
        return {
            "audio_url": f"/static/voice/{audio_name}",
            "duration_ms": duration_ms,
            "format": "wav",
            "engine": "indextts2",
        }
    except Exception as e:
        logger.error("IndexTTS2 生成失败: {}, 使用降级方案", e)
        return await _fallback_tts(text, speed)


async def _fallback_tts(text: str, speed: float = 1.0) -> dict:
    """降级 TTS 方案 — 使用 edge-tts（免费在线 TTS）"""
    try:
        import edge_tts

        audio_name = f"tts_{uuid.uuid4().hex[:12]}.mp3"
        audio_path = Path(config.STATIC_DIR) / "voice" / audio_name
        audio_path.parent.mkdir(parents=True, exist_ok=True)

        voice = "zh-CN-XiaoxiaoNeural"  # 微软晓晓中文女声
        communicate = edge_tts.Communicate(text=text, voice=voice, rate=f"{int((speed-1)*100):+d}%")
        await communicate.save(str(audio_path))

        duration_ms = _get_audio_duration(audio_path)
        logger.info("edge-tts 降级生成完成: {}", audio_name)
        return {
            "audio_url": f"/static/voice/{audio_name}",
            "duration_ms": duration_ms,
            "format": "mp3",
            "engine": "edge-tts",
        }
    except ImportError:
        logger.warning("edge-tts 未安装，TTS 功能不可用")
        return {"audio_url": None, "duration_ms": 0, "format": None, "engine": "none"}
    except Exception as e:
        logger.error("降级 TTS 也失败: {}", e)
        return {"audio_url": None, "duration_ms": 0, "format": None, "engine": "none"}


def _get_audio_duration(path: Path) -> int:
    """获取音频文件时长（毫秒）"""
    try:
        import wave
        with wave.open(str(path), "rb") as f:
            frames = f.getnframes()
            rate = f.getframerate()
            return int(frames / rate * 1000)
    except Exception:
        # mp3 或其他格式，估算
        size = path.stat().st_size
        return int(size / 16000)  # 粗略估算


async def unload_tts_model():
    """卸载 TTS 模型释放显存"""
    global _tts_model
    if _tts_model is not None:
        del _tts_model
        _tts_model = None
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("IndexTTS2 模型已卸载，显存已释放")
