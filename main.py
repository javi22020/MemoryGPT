import openai
import tiktoken
import json
client = openai.OpenAI()

assistant_prompt = "Eres un asistente de programación. Devuelve tus respuestas en Markdown, con bloques de código si es necesario, y responde todas las peticiones del usuario."
def join_messages(memory: list[dict]):
    text = ""
    for m in memory:
        text += m.get("content")
    return text

def check_under_context_limit(text: str, limit: int, model: str):
    enc = tiktoken.encoding_for_model(model)
    numtokens = len(enc.encode(text))
    if numtokens <= limit:
        return True
    else:
        return False

def follow_conversation(user_text: str, memory: list[dict], mem_size: int, model: str):
    ind = min(mem_size, len(memory))
    if ind == 0:
        memory = [{"role": "system", "content": assistant_prompt}]
    memory.append({"role": "user", "content": user_text})
    while not check_under_context_limit(join_messages(memory), 128000, "gpt-3.5-turbo") and ind > 1:
        ind -= 1
    resp = client.chat.completions.create(
        model=model,
        messages = memory[-ind:]
    )
    tr = resp.choices[0].message.content
    memory.append({"role": "assistant", "content": tr})
    open("respuestas.md", "a", encoding="utf-8").write(tr)
    print(tr)
    return memory

prompt = open("prompt.txt", "r").read()
memory = []
while True:
    user_input = input(">> ").strip()
    if user_input == "Exit":
        break
    elif user_input == "Prompt":
        user_input = prompt
    memory = follow_conversation(user_text=user_input, memory=memory, mem_size=10, model="gpt-4-1106-preview")

json.dump(memory, open("mem.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)