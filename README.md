
# Scryber

Scryber is a skribbl inspired interactive game built in python with pygame, one person draws - the rest guess. allows multi-client games and supports different rooms running at once.

---

* Contains LLM-based profanity blocker, custom TCP/SSL based communication, password encryption and more security measures.

---
<img width="1199" height="731" alt="image" src="https://github.com/user-attachments/assets/2cb8c4d7-6d4b-4369-87fb-3a1eeca3fa03" />

<img width="1192" height="723" alt="image" src="https://github.com/user-attachments/assets/dc8bb9cb-88d3-4131-8a4b-daef2d4a1c31" />
---

### Setup

.env file needed with GROQ llm api key and pepper encryption string. 

```env
GROQ_API_KEY=your_groq_key_here
PEPPER_SECRET=your_pepper_string_here
```
also there needs to be a cert file containing certificates for the asymmetric encryption, client needs to be able to access the public server certificate.
