import os
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def call_llm(prompt):
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt,
    )
    return response.text

# 3. the two-call experiment
print(call_llm("My name is Kavi. Remember it."))
print(call_llm("What is my name?"))