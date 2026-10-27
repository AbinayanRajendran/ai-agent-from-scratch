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

## Step 2 — adding the model's reply to history
- Working line: history.append({"role": "model", "parts": [{"text": reply}]})
- Mistakes I made and what they taught me:
  1. history = reply -> replaced the list with a string; len gave 62 (characters). = reassigns, .append() adds.
  2. "role": user (no quotes) -> NameError: Python looks for a variable called user.
  3. "text": "reply" (with quotes) -> would store the literal word "reply", and len would still say 2 — silent wrong answer.
  4. role "user" for Gemini's text -> model would think I said its words.
- Rule: for every value ask "fixed label or my changing data?" Fixed label -> quotes. Data in a variable -> no quotes.
- Verification habit: print the count AND print the contents. A correct count doesn't prove correct data.
- Same input, different runs: reply 25/21/22 tokens, thinking 239/293/133 tokens. LLMs are not deterministic, and cost per call varies even for identical input.
- Next: Step 3 — append "What is my name?", call with full history, check the model now answers "Kavi" and prompt_token_count ≈ turn1 + reply + question.

## Step 3 — the model remembers + a hidden bug
- Step 3 appended "What is my name?" as a user turn and sent the whole 3-turn history -> model answered "Your name is Kavi!"
- Token check confirmed the rule: 2nd call input = turn 1 + reply + question (e.g. 10 + 20 + 6 ≈ 37, extra 1 = formatting).
- Bug found: call_llm(prompt) received the list as `prompt` but used `contents=history` — it ignored its own input and grabbed the global variable. It only worked by luck.
- Why it matters: with several users/conversations, the function would silently send the wrong conversation — mixed-up private data, no error.
- Fix: contents=prompt. Rule: a function uses its own inputs, not outside variables.
- `contents=` is NOT a variable — it's the name of an input slot on Google's generate_content function (fixed label, my value). `=` inside a call's brackets fills a slot; `=` on its own line creates a variable.
- Demo that proved it: greet(name) returning "Hello " + person printed "Hello Kavi" for greet("Arun"). The function received Arun but never read it.
- Memory half of Part 2 DONE. Next: build the loop (LLM -> JSON -> tool -> observation -> repeat).
