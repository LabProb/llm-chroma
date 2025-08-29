#app/llm/llama_wrapper.py
import logging
from llama_cpp import Llama
from app.config import settings

class LlamaModel:
    def __init__(self, model_path: str | None = None):
        path = str(model_path or settings.model_path)
        logging.info(f"Loading model: {path}")
        try:
            self.llm = Llama(
                model_path=path,
                n_ctx=settings.n_ctx,
                n_threads=settings.n_threads,
                n_batch=settings.n_batch,
                verbose=False
            )
        except Exception as e:
            logging.error(f"Failed to initialize Llama: {e}")
            self.llm = None

        self.params = {
            "max_tokens": 256,
            "temperature": 0.8,
            "top_p": 0.9,
            "repeat_penalty": 1.2,
            "stop": ["User:", "Assistant:", "</s>"]
        }

    def set_params(self, **kwargs):
        for k, v in kwargs.items():
            if k in self.params:
                self.params[k] = v

    def generate(self, prompt: str, **kwargs) -> tuple[str, int]:
        if not self.llm:
            return "Model not initialized", 0

        args = {**self.params, **kwargs, "prompt": prompt, "echo": False}

        try:
            output = self.llm(**args)
        except Exception as e:
            logging.error(f"llama_cpp call failed: {e}")
            return f"Error: {e}", 0

        choices = output.get("choices", [])
        if not choices:
            return "No relevant information", 0

        text = choices[0].get("text", "").strip()
        tokens = output.get("usage", {}).get("total_tokens", 0)
        return text, tokens

    def close(self):
        if hasattr(self, "llm") and self.llm:
            try:
                self.llm.close()
            except Exception as e:
                logging.warning(f"Failed to close Llama: {e}")

    def __del__(self):
        self.close()
