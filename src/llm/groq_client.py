"""
Groq API client wrapper.
"""

import logging
import time

from groq import Groq, APIError, APIConnectionError, RateLimitError

logger = logging.getLogger(__name__)

class GroqClient:
    def __init__(self, api_key: str, model: str, temperature: float):
        # The Groq SDK will automatically pick up GROQ_API_KEY from environment if api_key is None,
        # but we explicitly pass it for clarity if provided.
        self.client = Groq(api_key=api_key) if api_key else Groq()
        self.model = model
        self.temperature = temperature

    def get_recommendation(self, system_prompt: str, user_prompt: str) -> str:
        """
        Calls Groq API to get recommendation. Retries once on transient errors.

        Returns
        -------
        str
            Raw JSON string from Groq.
        """
        max_retries = 1
        
        for attempt in range(max_retries + 1):
            try:
                start_time = time.time()
                
                prompt_length = len(system_prompt) + len(user_prompt)
                logger.info("Calling Groq API (model=%s, est_prompt_tokens=~%d)", self.model, prompt_length // 4)
                
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=self.temperature,
                    response_format={"type": "json_object"},
                )
                
                latency = (time.time() - start_time) * 1000
                logger.info("Groq API call complete in %.2f ms", latency)
                
                content = completion.choices[0].message.content
                if not content:
                    raise APIError("Empty response from Groq API", request=None, body=None)
                    
                return content
                
            except (APIConnectionError, RateLimitError, APIError) as e:
                logger.warning("Groq API error on attempt %d: %s", attempt + 1, str(e))
                if attempt == max_retries:
                    raise
                time.sleep(1) # Backoff
                
        raise RuntimeError("Unreachable")
