# Milestone 1, Part 2 — Connecting a real LLM

## Provider decision
- Gemini free tier (AI Studio key, no credit card). Backup: Groq.
- Why it barely matters yet: my agent uses my own JSON protocol, so the LLM only needs text in -> text out. Provider-native tool calling comes later (Milestone 3) for comparison.
- Free tier caveat: content may be used by Google to improve products -> fine for learning, NOT for real users' data later.

## Experiment 1: does the LLM remember? (two separate calls)
- Call 1: "My name is Kavi. Remember it." -> "Got it, Kavi!"
- Call 2: "What is my name?" -> "I don't know your name yet..."
- Lesson: the LLM is stateless. Each call contains ONLY what I send. Call 2 never saw "Kavi".
- Lesson: "Got it" / "I've saved it" is just generated text. Nothing was stored. What the model SAYS it does is not what the code does.

## How "memory" works
- My code keeps a history list and resends ALL of it on every call.
- The memory lives in my laptop's RAM -> gone when the program ends (persistent memory = Milestone 4).

## What happens in one call (step 1 trace)
1. history list built on my laptop (Google knows nothing yet)
2. SDK converts list -> JSON, sends HTTPS request with key + model name
3. Google checks key/limits, model reads ONLY the request contents, generates reply token by token
4. Google returns reply + token counts, then keeps nothing
5. SDK returns response; .text extracts the reply

## Real token numbers (one short call)
- input 10, visible reply 25, hidden thinking 239, total 274
- ~87% of tokens were hidden "thinking", billed like output (the expensive kind)
- Short visible reply != cheap call. Thinking can be turned down per call (Milestone 4 cost control).
- Thinking tokens are NOT in response.text, so they never enter history and are never resent.

## Prediction lesson
- Second call sends EVERYTHING in history: turn 1 (10) + reply (25) + new question (~6) ≈ 41 tokens.
- I first predicted 31 (forgot turn 1), then 270 (wrongly added thinking). Rule: if it isn't in history, it isn't sent. I decide what goes into history -> that controls both what the model knows and what I pay.

## Milestone 4 to-do list (found in this part)
- 503 "high demand" errors happen -> call_llm needs retry with backoff + fallback model
- Control thinking tokens for cost
- Persistent memory (history survives between runs)
- Divide-by-zero crash in calculator (from Part 1)

## Next
- Steps 2 & 3: append the model reply to history, then ask "What is my name?" with full history; check prompt_token_count ≈ 41.
