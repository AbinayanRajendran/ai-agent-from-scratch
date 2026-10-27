import os
from google import genai

# The client is created ONCE, here at the top, and kept in a variable.
# If it is not stored (e.g. a one-liner like genai.Client(...).models.generate_content(...)),
# Python garbage-collects it and closes its connection, and you get:
#   RuntimeError: Cannot send a request, as the client has been closed
# The API key comes from the GEMINI_API_KEY environment variable and is NEVER
# written in code, so it can't leak into git.
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# call_llm wraps EVERY LLM call. The rest of the agent only ever calls call_llm,
# so it never knows which provider is behind it. That makes switching providers
# easy, and retry/fallback logic will live here later.
# prompt = the full history list (all turns), not a single message.
# The function must use its OWN input (prompt), never reach outside for a global variable.
def call_llm(prompt):
    response = client.models.generate_content(
        # The model is a PINNED version, not a "-latest" alias, so Google can't
        # silently swap the model under me.
        # gemini-3.8-flash returned 503 (high demand), so I use gemini-3.5-flash.
        # Fallback order: gemini-3.5-flash -> gemini-2.5-flash.
        model="gemini-3.5-flash",
        contents=prompt,
    )
    # Shows the token counts Google bills for this call (input, output, thinking).
    print(response.usage_metadata)
    return response.text

# 3. the two-call experiment
# These two lines proved the LLM is STATELESS: each call contains ONLY what I send.
# Call 1 ("My name is Kavi") got "Got it, Kavi!", but call 2 ("What is my name?")
# said it didn't know, because call 2 never saw call 1. "Got it" was just generated
# text; nothing was stored.
#print(call_llm("My name is Kavi. Remember it."))
#print(call_llm("What is my name?"))

# 3. the experiment, with memory
# A list written alone on a line does nothing. It must be stored in a variable
# (history) and grown with .append(). history is MY Python variable, not a field.
history = []                     # start: 0 turns

# "role", "parts" and "text" are FIXED field names Gemini requires, and so are the
# role values "user" / "model". Only the message text is my own data.
history.append({"role": "user", "parts": [{"text": "My name is Kavi. Remember it."}]})
print(len(history))              # should print 1

reply = call_llm(history)        # send ALL turns so far
print(reply)

# Step 2: add the model's OWN reply to history as a "model" turn, so on the next
# call the model can see what it said before. This is what turns separate calls
# into a conversation.
# - .append() keeps the list and adds to the end. "history = reply" would REPLACE
#   the list with a string (I tried it: len printed 62 = characters, not turns,
#   a silent wrong answer with no error).
# - Quotes rule: WITH quotes = literal fixed text ("role", "text", "user", "model").
#   WITHOUT quotes = look up a variable (reply). Writing user without quotes gives
#   NameError. Writing "reply" with quotes would send the literal word "reply".
# - The role must be "model" because Gemini wrote that text; labelling it "user"
#   would make the model think I said it.
history.append({"role": "model", "parts": [{"text": reply}]})
print(len(history))   # checks the COUNT (should be 2)
# Checks the CONTENTS: the count alone can't catch a wrong role or the literal
# word "reply".
print(history)

# Step 3: ask the follow-up. Same pattern as step 1: a "user" turn appended to
# history, then the WHOLE history is sent, so the model can see "Kavi" from turn 1.
history.append({"role": "user", "parts": [{"text": "What is my name?"}]})
print(len(history))   # should print 3

reply2 = call_llm(history)   # stored in its own variable so `reply` isn't overwritten
print(reply2)
