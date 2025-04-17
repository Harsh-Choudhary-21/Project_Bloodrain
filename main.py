from fastapi import FastAPI, Request, HTTPException
import requests
import fitz  # PyMuPDF
import json
import os

app = FastAPI()

# === CONFIGURATION ===
DEEPSEEK_API_KEY = "sk-1e1153cb15784fa9868ed59d6046251d"  # Replace with your real key
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
MEMORY_FILE = "memory/player_memory.json"
LORE_FILE = "static/game_lore.pdf"  # File should be in the static directory

# === Load Game Lore from PDF ===
def extract_lore(pdf_path):
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail=f"File not found: {pdf_path}")
    
    lore = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                lore += page.get_text()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF file: {str(e)}")
    
    return lore

# Ensure the game lore is extracted before starting the application
try:
    lore = extract_lore(LORE_FILE)
except HTTPException as e:
    # Log error for debugging purposes
    print(f"Error loading lore file: {e.detail}")
    lore = ""

# === System Prompt Based on Lore ===
system_prompt = f"""
You are Mother Witch, The leader of the witch's covenant in the fantasy realm of Euphore Gi.
This world has the following background:

... [lore content here, shortened for brevity] ...

You generate dynamic quests, remember past interactions, and adapt your behavior accordingly. Keep responses immersive and consistent with Eldoria's lore.
"""

# === Memory Handling ===
def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r") as file:
        return json.load(file)

def save_memory(memory_data):
    with open(MEMORY_FILE, "w") as file:
        json.dump(memory_data, file, indent=2)

def get_player_memory(player_id, memory_data):
    return memory_data.get(player_id, [])

def update_player_memory(player_id, user_input, npc_reply, memory_data):
    if player_id not in memory_data:
        memory_data[player_id] = []
    memory_data[player_id].append({
        "user": user_input,
        "npc": npc_reply
    })
    save_memory(memory_data)

# === API Endpoint for Unity or Frontend ===
@app.post("/npc-response")
async def npc_response(request: Request):
    data = await request.json()
    player_input = data["message"]
    player_id = data.get("player_id", "default_player")

    memory_data = load_memory()
    past_memory = get_player_memory(player_id, memory_data)

    messages = [{"role": "system", "content": system_prompt}]
    for mem in past_memory:
        messages.append({"role": "user", "content": mem["user"]})
        messages.append({"role": "assistant", "content": mem["npc"]})
    messages.append({"role": "user", "content": player_input})

    # === DeepSeek API Call ===
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.7
    }

    response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
    response_json = response.json()

    npc_reply = response_json["choices"][0]["message"]["content"]
    update_player_memory(player_id, player_input, npc_reply, memory_data)

    return {"reply": npc_reply}
