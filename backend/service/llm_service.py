"""LLM 服务 — Ollama DeepSeek 流式/非流式调用"""
import json
import httpx
import config
from typing import AsyncGenerator
from utils.logger import get_logger

logger = get_logger()


async def stream_chat(prompt: str, model: str = None, temperature: float = None) -> AsyncGenerator[dict, None]:
    """流式调用 Ollama，yield token 字典"""
    model = model or config.OLLAMA_MODEL
    temperature = temperature if temperature is not None else config.LLM_TEMPERATURE

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True,
        "options": {
            "temperature": temperature,
            "num_predict": config.LLM_MAX_TOKENS,
            "num_ctx": config.LLM_CONTEXT_WINDOW,
        }
    }

    async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
        try:
            async with client.stream("POST", f"{config.OLLAMA_BASE_URL}/api/generate", json=payload) as resp:
                async for line in resp.aiter_lines():
                    if not line:
                        continue
                    data = json.loads(line)
                    if data.get("response"):
                        yield {"type": "token", "content": data["response"]}
                    if data.get("done"):
                        yield {
                            "type": "done",
                            "usage": {
                                "prompt_tokens": data.get("prompt_eval_count", 0),
                                "completion_tokens": data.get("eval_count", 0),
                                "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
                            }
                        }
                        break
        except httpx.ConnectError:
            logger.error("Ollama 服务连接失败: {}", config.OLLAMA_BASE_URL)
            yield {"type": "error", "content": "大模型服务未启动，请先运行 ollama serve"}
        except Exception as e:
            logger.error("LLM 流式调用异常: {}", e)
            yield {"type": "error", "content": str(e)}


async def chat(prompt: str, model: str = None, temperature: float = None) -> dict:
    """非流式调用 Ollama"""
    model = model or config.OLLAMA_MODEL
    temperature = temperature if temperature is not None else config.LLM_TEMPERATURE

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": config.LLM_MAX_TOKENS,
            "num_ctx": config.LLM_CONTEXT_WINDOW,
        }
    }

    async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
        try:
            resp = await client.post(f"{config.OLLAMA_BASE_URL}/api/generate", json=payload)
            data = resp.json()
            return {
                "answer": data.get("response", ""),
                "usage": {
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                    "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
                },
                "response_time_ms": int(data.get("total_duration", 0) / 1_000_000),
            }
        except httpx.ConnectError:
            return {"answer": "大模型服务未启动，请先运行 ollama serve", "usage": {}, "response_time_ms": 0}
        except Exception as e:
            logger.error("LLM 调用异常: {}", e)
            return {"answer": f"调用失败: {e}", "usage": {}, "response_time_ms": 0}


async def check_ollama_status() -> dict:
    """检查 Ollama 服务状态"""
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.get(f"{config.OLLAMA_BASE_URL}/api/tags")
            data = resp.json()
            models = [m["name"] for m in data.get("models", [])]
            return {
                "status": "up",
                "models": models,
                "default_model": config.OLLAMA_MODEL,
                "model_loaded": config.OLLAMA_MODEL in models,
            }
        except Exception:
            return {"status": "down", "models": [], "default_model": config.OLLAMA_MODEL, "model_loaded": False}
