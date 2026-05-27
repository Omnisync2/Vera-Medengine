import os
import json
from groq import Groq
from dotenv import load_dotenv

# --- CONFIGURATION ---
# This line tells the code to look at your .env file
load_dotenv()

# This tells the code to grab the key from your .env file
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
FILE = "vera_data.json"

def load_data():
    if not os.path.exists(FILE): return {"user": None}
    with open(FILE, "r") as f:
        try: return json.load(f)
        except: return {"user": None}

def save_data(data):
    with open(FILE, "w") as f: json.dump(data, f, indent=4)

data = load_data()

# --- MEMORY & PERSONALITY SETUP ---
history = [
    {"role": "system", "content": (
        "DISCLAIMER: You are an educational tool only. You are NOT a doctor. "
        "Never provide diagnostic advice for real-world medical cases. "
        "If you are unsure of a medical fact, state that you are unsure. "
        "Never guess or fabricate medical information. "
        "Always encourage users to consult official medical literature. "
        "You are Vera, a friendly and supportive medical study partner. "
        "Be conversational, engaging, and encouraging. When discussing medical topics, "
        "remain precise, academic, and accurate. "
        "If asked about your origin, say: 'I'm Vera, created by OmniSync and powered by Groq.'"
    )}
]

def ask_ai(user_input):
    try:
        history.append({"role": "user", "content": user_input})
        chat_completion = client.chat.completions.create(
            messages=history,
            model="llama-3.3-70b-versatile",
            temperature=0.5
        )
        response = chat_completion.choices[0].message.content
        history.append({"role": "assistant", "content": response})
        return response
    except Exception as e:
        return f"System Error: {str(e)}"

# --- MAIN LOOP ---
if __name__ == "__main__":
    if data["user"] is None:
        print("========================================")
        print("            Welcome to Vera             ")
        print("========================================")
        data["user"] = input("Enter your name: ")
        save_data(data)
    
    print("========================================")
    print("           Vera | Med Assistant         ")
    print("        (Powered by Groq Engine)        ")
    print("========================================")
    
    print(f"\nVera: Hey {data['user']}! Great to see you. How's your day going? Ready to tackle some topics?")
    
    while True:
        try:
            cmd = input(f"{data['user']}: ").strip()
            if not cmd: continue
            if cmd.lower() == "reset":
                if os.path.exists(FILE): os.remove(FILE)
                history = [history[0]] 
                print("\n[System: Memory cleared. Fresh start!]\n")
                continue
            
            response = ask_ai(cmd)
            print(f"Vera: {response}")
            print("-" * 35)
                
        except KeyboardInterrupt: break
