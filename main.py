import openai
import tiktoken
import json
client = openai.OpenAI()

assistant_prompt = "You are a helpful assistant"
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
    while not check_under_context_limit(join_messages(memory), 4096, model) and ind > 1:
        ind -= 1
    resp = client.chat.completions.create(
        model=model,
        messages = memory[-ind:]
    )
    tr = resp.choices[0].message.content
    memory.append({"role": "assistant", "content": tr})
    print(resp.choices[0].message.content)
    return memory

memory = []
while True:
    user_input = input(">> ")
    if user_input == "Exit":
        break
    memory = follow_conversation(user_text=user_input, memory=memory, mem_size=10, model="gpt-3.5-turbo")

json.dump(memory, open("mem.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)