import google.generativeai as genai

import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-3.5-flash-lite")


def generate_coaching_advice(workout):
    print("Step 1: Preparing prompt...")

    prompt = f"""
You are an expert sports performance coach.

Analyze this workout data.

Heart Rate: {workout['heart_rate']} BPM
SpO2: {workout['spo2']}%
Fatigue: {workout['fatigue']}%
Performance Score: {workout['performance']}
Activity: {workout['activity']}
Steps: {workout['steps']}
Cadence: {workout['cadence']}
Stride Length: {workout['stride_length']}
Temperature: {workout['temperature']}°C

Return ONLY plain text.

Do NOT use Markdown.
Do NOT use ** symbols.
Do NOT use headings with ##.
Do NOT use bullet points.

Use exactly this format:

Fatigue Analysis:
<your analysis>

Performance Analysis:
<your analysis>

Hydration Advice:
<your advice>

Recovery Advice:
<your advice>

Injury Risk:
<your analysis>

Next Workout Recommendation:
<your recommendation>

Keep the response concise and professional.
"""

    print("Step 2: Sending request to Gemini...")

    response = model.generate_content(prompt)

    print("Step 3: Response received!")

    return response.text