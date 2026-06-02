import os
from groq import Groq
from pathlib import Path
from dotenv import load_dotenv


class AiModerator:
    def __init__(self):

        basedir = os.path.dirname(os.path.abspath(__file__))
        envdir = os.path.join(basedir, ".env")
        load_dotenv(dotenv_path=envdir)
        self.apikey = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.model = "llama-3.1-8b-instant"

    def review_message(self, text: str) -> bool:
        prompt = (
            "Task: check if there is any unsafe or toxic content in the message. also search for game cheating or ruining, for example: typing 'the word is banana', search for any type of message trying to give hints or reveal the secret word."
            "if you determine the message unsafe or cheating, REPLY EXACTLY WITH: unsafe. otherwise REPLY EXACTLY WITH: safe ")

        try:
            response = self.apikey.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": prompt}, {"role": "user", "content": text}],
                temperature=0.0,
                max_tokens=10
            )
            decision = response.choices[0].message.content.strip().lower()
            return "unsafe" not in decision
        except Exception as e:
            print(f"Error ai: {e}")
            return True
