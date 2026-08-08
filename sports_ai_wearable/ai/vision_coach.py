import os
from urllib import response
from urllib import response
import google.generativeai as genai
from matplotlib import text

# Use the same API key you used in gemini_coach.py

import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-3.5-flash")


def analyze_frames(frame_folder):

    prompt = """
You are an expert sports coach.

Analyze these sports images.

Write the response as plain text.

Do NOT use Markdown.

Do NOT use **

Do NOT use ###

Do NOT use bullet symbols.

Use this format:

Body Posture:
...

Balance:
...

Footwork:
...

Movement Quality:
...

Injury Risk:
...

Performance Tips:
...

Keep it concise and easy to read.
"""

    images = []

    for file in sorted(os.listdir(frame_folder)):

        if file.endswith(".jpg"):

            path = os.path.join(frame_folder, file)

            images.append({
                "mime_type": "image/jpeg",
                "data": open(path, "rb").read()
            })

    response = model.generate_content([prompt] + images)

    text = response.text

# Remove Markdown
    text = text.replace("###", "")
    text = text.replace("##", "")
    text = text.replace("#", "")
    text = text.replace("**", "")
    text = text.replace("*", "")
    text = text.replace("---", "")
    text = text.replace("`", "")

    return text