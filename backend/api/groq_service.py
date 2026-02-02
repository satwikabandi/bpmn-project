import os
import re

import requests


class GroqService:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.base_url = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
        # Updated to current Groq model (llama-3.3 instead of 3.1)
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    def normalize_input(self, text):
        if not self.api_key:
            print("Groq API key not found, skipping Groq normalization")
            return text

        system_prompt = """You are a BPMN Logic Normalizer. Convert the user's natural language description into a strict, step-by-step logic format for BPMN diagram generation.

RULES:
1. ALWAYS start with 'Start Process' and end with 'End Process'
2. Use short, clear step names (3-5 words max). Example: "Enter Credentials" not "The user enters their credentials"
3. For decisions/conditions, use explicit IF/ELSE blocks:
   If <Short Condition>
      <Action Step>
   Else
      <Alternative Step>
   End If
4. Condition names should be concise questions/states: "Credentials Valid", "User Exists", "Payment Approved"
5. For groups, use 'Group: <Name>' and 'End Group'
6. Do NOT include markdown formatting. Output plain text only.
7. Support multilingual input (English, Telugu/తెలుగు, Tamil/தமிழ்) - convert to English step names

EXAMPLE INPUT:
"The process starts when a user opens the login page. The user enters username and password. The system validates the credentials. If the credentials are valid, the system logs in the user and shows the dashboard. If invalid, show error and ask to retry. The process ends."

EXAMPLE OUTPUT:
Start Process
Enter Credentials
Validate Credentials
If Credentials Valid
   Log In User
   Show Dashboard
Else
   Show Error Message
   Ask to Retry
End If
End Process

EXAMPLE INPUT (Telugu):
"వినియోగదారు లాగిన్ పేజీని తెరిచినప్పుడు ప్రక్రియ ప్రారంభమవుతుంది. వినియోగదారు యూజర్‌నేమ్ మరియు పాస్‌వర్డ్ నమోదు చేస్తారు."

EXAMPLE OUTPUT:
Start Process
Open Login Page
Enter Username and Password
End Process

Now convert the following description:"""

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            "temperature": 0.1,  # Lower temperature for more consistent output
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            resp = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            content = re.sub(r"^```[a-zA-Z]*\n?", "", content.strip())
            content = re.sub(r"```$", "", content.strip())
            return content.strip()
        except requests.exceptions.HTTPError as e:
            # Log full error details for debugging
            print(f"Groq API HTTP Error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response Status: {e.response.status_code}")
                print(f"Response Body: {e.response.text[:500]}")
            return text
        except Exception as e:
            print(f"Groq Normalization Error: {e}")
            return text

