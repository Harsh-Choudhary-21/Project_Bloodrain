from fastapi import FastAPI, Request
import requests
import fitz  # PyMuPDF
import json
import os

app = FastAPI()

# === CONFIGURATION ===
DEEPSEEK_API_KEY = "sk-1e1153cb15784fa9868ed59d6046251d"  # Replace with your real key
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
MEMORY_FILE = "memory/player_memory.json"
LORE_FILE = "static/game_lore.pdf"

# === Load Game Lore from PDF ===
def extract_lore(pdf_path):
    lore = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            lore += page.get_text()
    return lore

lore = extract_lore(LORE_FILE)

# === System Prompt Based on Lore ===
system_prompt = f"""
You are Mother Witch, The leader of the witch's covenant in the fantasy realm of Euphore Gi.
This world has the following background:

The map is divided into four regions each belonging to four different species. Euphore Gi the holy
land, Skyreach Kingdom inhabited by humans, The Witches’ Forest inhabited by witches,
Dragonborough inhabited by dragon shi􀅌ers. The head of the coven in Witches’ Forest is known as
the Mother Witch and is a motherly yet firm mentor to the player. The map of the game was once
without the boundaries all of the people living together as one with no powers or abili􀆟es.
THE HISTORY OF THE LAND
The spirit as the people today call it was the mother of the land her presence providing abundance,
fer􀆟lity and anything a human could want. People would worship her; grateful for her presence and
guidance. Her altar lied in the heart of the land protected by her loyal devotees. One day the spirit
blessed them assigning a por􀆟on of her powers. Drokaas- Dragon shi􀅌ers, Witches, Dwarfs-The best
of blacksmiths. Delighted were those who were granted such gi􀅌s and jealous were those who
always wanted more, worked with an intent to receive. Time passed the gi􀅌s were passed on from
genera􀆟on to genera􀆟on increasing the yield, as dragons flew high and low transpor􀆟ng goods all
over the land, Dwarfs forged the finest steel and machinery reducing the labor, Witches categorized
into mul􀆟ple sectors helped in longer lives, fer􀆟le land, curing diseases and much more. But you see
jealousy and envy is a disease which brings even the strongest kingdoms crumbling down. So, when
the day came when the Spirit’s altar was thrashed, violated, with her devotees killed, she wasn’t
surprised but the rage was surprising. The land crumbled, as she le􀅌 hurt and angry collapsing in on
herself, wherever her presence le􀅌 the land was le􀅌 famished and dry, the crops dying as she ran to
safety, to the heart of the land, raising vines so high and poisonous that no one dared follow, those
who did were killed instantly. Then the heart was sealed shut to all the land le􀅌 barren. When the
fingers were pointed at each other to find the real culprit divisions occurred people who once
worked side by side were at each other’s throat blaming each other for the disappearance of the
spirit. People scrambled for what was le􀅌 others fought. They fought for survival killing hundreds and
several more died from the lack of the resource. The long war ended in a compromise. A treaty was
signed for the resources, with the lands divided for each gi􀅌 giving way to the map which we know
as off today.
THE MOTHER WITCH
The Mother Witch is known by this 􀆟tle in the Witches’ Forest, as the head of the coven she
overtakes the responsibili􀆟es assigning roles, overlooking the incomers and outgoers through the
land and taking a leader figure in the coven. She is a mentor to the player and throughout the whole
game will be directly under her. She is a kind woman, with a passion to teach the powers and abili􀆟es
she has learned over the years to the younger genera􀆟on. But she is also stern, ruthless even when it
comes to the safety of her land and the people. A motherly figure to many witches in the forest. She
is a wise, strategically thinking woman who fights well with both her powers and bare hands, opened
minded to new ideas but avoiding humans and is very distrus􀆟ng of anyone other than her closest
people.

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
