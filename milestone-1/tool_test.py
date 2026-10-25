import json
from datetime import datetime

# ---------- 1. The tools: plain Python functions ----------

def get_current_time(tool_input):
    return datetime.now().strftime("%H:%M")

def calculator(tool_input):
    allowed = "0123456789/-+().* "
    for ch in tool_input:
            if ch not in allowed:
                return f"ERROR: '{ch}' is not allowed"
    return str(eval(tool_input))

def word_count(tool_input):
    return str(len(tool_input.split()))

# ---------- 2. The lookup: tool name (text) → real function ----------

TOOLS = {
    "get_current_time": get_current_time,
    "calculator": calculator,
    "word_count": word_count
}

# ---------- 3. Run whatever tool a note asks for ----------

def run_tool(note):
    

    name = note["tool"]
    tool_input = note["input"]

    if name not in TOOLS:
        return f"ERROR: no tool called {name}"

    func = TOOLS[name]
    return func(tool_input)

# ---------- 4. Test with a fake LLM reply (no LLM yet) ----------

reply_text = '{"tool": "calculator", "input": "(10 + 2) / 4"}'
note = json.loads(reply_text)                             # text → dict
result = run_tool(note)
print(result)   # 35
