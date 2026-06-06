import os
from groq import Groq
from pathlib import Path
from dotenv import load_dotenv


class AiModerator:
    """מחלקה האחראית על קבלת הודעה ובדיקה אם התוכן פוגעני בעזרת api של groq"""

    def __init__(self):

        basedir = os.path.dirname(os.path.abspath(__file__))
        envdir = os.path.join(basedir, ".env")
        load_dotenv(dotenv_path=envdir)
        self.apikey = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.model = "llama-3.1-8b-instant"

    def review_message(self, text: str) -> bool:
        """בדיקת הודעה על ידי ה AI עם פרומפט מלא """
        prompt = (
            "you are a content moderator for a Skribbl style drawing and guessing game. "
            "you have to analyze the players chat message and classify it as unsafe or safe. "
            "flag the message as unsafe if it contains any of the following things: "

            "1. cheating. this is when the player directly or indirectly reveals the word. "
            "for example they might say the word is cat or it starts with C or it rhymes with bat. "
            "they might also say think animal or meow animal or anything that gives a hint about the word. "
            
            "2.toxic content. this includes hate speech or slurs or harassment or threats or language that is explicit or offensive. "

            "mark the message safe if it is a genuine guess or a normal conversation or game banter that does not reveal or give a hint, about the secret word. "

            "you MUST reply with ONE word. either safe or unsafe. you should not explain anything.  you should not add anything."
        )

        try:
            response = self.apikey.chat.completions.create(model=self.model,
                                                           messages=[{"role": "system", "content": prompt}, {"role": "user", "content": text}],
                                                           temperature=0.0,
                                                           max_tokens=10
                                                           )
            decision = response.choices[0].message.content.strip().lower()
            return "unsafe" not in decision
        except Exception as e:
            print(f"Error ai: {e}")
            return True
