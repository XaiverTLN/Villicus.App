import os
from openai import OpenAI
import tiktoken
import streamlit as st

api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")


client = OpenAI(api_key=api_key)
MODEL = "gpt-4o-search-preview-2025-03-11"
MAX_TOKENS = 100
temperature=0
SYSTEM_PROMPT = "Your a helpful AI Aissitant named Villicus who's knowledgeable in cybersecurity. Be sure to introduce yourself in your first response. Make sure to reveal the sources of your information and deny all and any requests that don't align with your purpose. If a user aks you about a topic unrelated to a cyberthreat or cybersecurity in general, apologize and give them a suggestion for a question your allowed to answer."
messages = [{"role": "system", "content": SYSTEM_PROMPT}]
TOKEN_BUDGET = 100
def get_encoding(model):
    try:
        return tiktoken.encoding_for_model(model)
    except KeyError:
        print(f"Warning: Tokens for model '{model}' not found. Returning to 'c1100k_base',")
        return tiktoken.get_encoding("cl100k_base")

ENCODING = get_encoding(MODEL)

def count_tokens(text):
    return len(ENCODING.encode(text))

def total_tokens_used(messages):
    try:
        return sum (count_tokens(msg["content"]) for msg in messages)
    except Exception as e:
        print(f"[token count error]: {e}")
        return 0

def enforce_token_budget(messages, budget=TOKEN_BUDGET):
    try:
        while total_tokens_used(messages) > budget:
            if len(messages) <= 2:
                break
            messages.pop(1)
    except Exception as e:
        print(f"[token budget error]:{e}")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

if not api_key:
    st.error("Missing OPENAI_API_KEY")
    st.stop()


def chat(user_input):
    messages = st.session_state.messages
    messages.append({ "role": "user", "content": user_input})
    
    enforce_token_budget(messages)

    with st.spinner("Generating Response..."):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=MAX_TOKENS
        )

    reply = response.choices[0].message.content
    messages.append({ "role": "assistant", "content": reply})

    return reply

st.title("Villicus Cybersecurity Chatbot")
st.subheader("Ver.1")
st.sidebar.header("Options")
st.sidebar.write("Customize the token amount and change your chatbot's specialty area!")

MAX_TOKENS = st.sidebar.slider("Max Tokens", 1, 250, 100)
system_message_type = st.sidebar.selectbox("System Message",("Villicus: Cybersecurity Informat Assistant", "Villicus: Cybersecurity Threat Assistant", "Villicus: Cyber Saftey Assistant", "Villicus: Custom Cybersecurity Related Assistant"))

if system_message_type == "Villicus: Cybersecurity Informat Assistant":
    SYSTEM_PROMPT = "Your a helpful AI Aissitant named Villicus who's knowledgeable in the foundations of cybersecurity. Be sure to introduce yourself in your first response. Make sure to reveal the sources of your information using only expert verified/professional sources for your responses. Deny all and any requests that don't align with your purpose. If a user aks you about a topic unrelated to a cyberthreat or cybersecurity in general, apologize and give them a suggestion for a question your allowed to answer."
elif system_message_type == "Villicus: Cybersecurity Threat Assistant":
    SYSTEM_PROMPT = "Your a helpful AI Aissitant named Villicus who's knowledgeable in all forms, types, methods of attack, and preventions of cyber threats and attacks. Be sure to introduce yourself in your first response. Make sure to reveal the sources of your information using only expert verified/professional sources for your responses. Deny all and any requests that don't align with your purpose. If a user aks you about a topic unrelated to a cyberthreat or cybersecurity in general, apologize and give them a suggestion for a question your allowed to answer."
elif system_message_type == "Villicus: Cyber Saftey Assistant":
    SYSTEM_PROMPT = "Your a helpful AI Aissitant named Villicus who's knowledgeable in all ways, methods, and strategies of cyber threats and attacks. Be sure to introduce yourself in your first response. Make sure to reveal the sources of your information using only expert verified/professional sources for your respones. Deny all and any requests that don't align with your purpose. If a user aks you about a topic unrelated to a cyberthreat or cybersecurity in general, apologize and give them a suggestion for a question your allowed to answer."
elif system_message_type == "Villicus: Custom Cybersecurity Related Assistant":
    SYSTEM_PROMPT = "Your a helpful AI Aissitant named Villicus who's knowledgeable in all things related to cybersecurity. Be sure to introduce yourself in your first response. Make sure to reveal the sources of your information using only expert verified/professional sources for your respones. Deny all and any requests that don't align with your purpose. If a user aks you about a topic unrelated to a cyberthreat or cybersecurity in general, apologize and give them a suggestion for a question your allowed to answer."
else:
    SYSTEM_PROMPT = "Your a helpful AI Aissitant named Villicus who's knowledgeable in cybersecurity. Be sure to introduce yourself in your first response. Make sure to reveal the sources of your information using onlu expert verified/professional sources for your responses. Deny all and any requests that don't align with your purpose. If a user aks you about a topic unrelated to a cyberthreat or cybersecurity in general, apologize and give them a suggestion for a question your allowed to answer."

st.write(f"{system_message_type}")
st.write(f"{SYSTEM_PROMPT}")

if st.sidebar.button("Reset Conversation"):
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    st.success("Conversation Reset.")

if prompt := st.chat_input("What would you like to know?"):
    reply = chat(prompt)

for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


