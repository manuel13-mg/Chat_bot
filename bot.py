import streamlit as st
import groq
import re
import time
from transformers import pipeline
from bs4 import BeautifulSoup
import base64
import os

# --- Configuration ---
st.set_page_config(
    page_title="TranquilTalk",
    page_icon="bg1.jpg",  # Local file path for the icon
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- Image Handling ---
def load_image(filepath):
    try:
        with open(filepath, "rb") as f:
            image_data = f.read()
        base64_encoded = base64.b64encode(image_data).decode('utf-8')
        return f"data:image/jpeg;base64,{base64_encoded}"
    except FileNotFoundError:
        st.error(f"Image file not found: {filepath}")
        return None

# --- Load Images (Ensure correct file paths!) ---
bot_image_path = "img.jpg"  # Local file path for bot message bg
background_path = "bg1.jpg"  # Local file path for the main background
icon_path = "bg1.jpg"       # Local file path for the icon
header_image_path = "img2.png"

# --- Display Header Image ---
st.image(header_image_path, use_container_width=True)

# --- CSS Styling ---
st.markdown(
    f"""
    <style>
    body {{
        font-family: Arial, sans-serif;
        background-color: #000000; /* Black background */
        color: #ffffff;
        background-image: url("data:image/jpeg;base64,{load_image(background_path)}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    
    .header {{
        width: 100%;
        text-align: center;
        margin-bottom: 20px;
    }}

    .stApp {{
        max-width: 800px;
        margin: 0 auto;
        padding: 30px;
        background-color: rgba(30, 30, 30, 0.8);
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(128, 128, 128, 0.1);
    }}

    .stTextInput>label {{
        color: #d3d3d3;
    }}

    .stButton>button {{
        background-color: #add8e6;
        color: #000000;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }}

    .stButton>button:hover {{
        background-color: #b0c4de;
    }}

    .user-message {{
        background-color: #333333;
        color: #ffffff;
        text-align: right;
        margin-left: 20%;
    }}

    .bot-message {{
        background-color: #2e2e2e;
        color: #ffffff;
        text-align: left;
        margin-right: 20%;
        border-radius: 10px;
        padding: 10px;
        word-break: break-word;
        background-image: url("data:image/png;base64,{load_image(bot_image_path)}");
        background-size: cover;
        background-repeat: no-repeat;
    }}

    .quote {{
        font-style: italic;
        margin-top: 10px;
        color: #d3d3d3;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Display Header Image ---
st.image(header_image_path, use_container_width=True)

# --- Sentiment Analysis Initialization ---
try:
    sentiment_pipeline = pipeline("sentiment-analysis")
    sentiment_analysis_available = True
except Exception as e:
    st.error(f"Error initializing sentiment analysis: {e}")
    sentiment_analysis_available = False

# --- Groq API Initialization ---
try:
    groq_api_key = "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"  # Use env var or fallback
    client = groq.Client(api_key=groq_api_key)
    model_available = True
except Exception as e:
    st.error(f"Error initializing Groq client: {e}")
    model_available = False

def extract_quote_text(html_string):
    """Extracts the text content from a <p class='quote'> element."""
    soup = BeautifulSoup(html_string, "html.parser")
    quote_element = soup.find("p", class_="quote")
    return str(quote_element) if quote_element else None

# --- Emotionally Aware Response Function ---
def get_bot_response(user_input: str, chat_history: str) -> str:
    """Generates an empathetic and supportive response from the bot, with a quote."""
    if not model_available or not sentiment_analysis_available:
        return "I'm sorry, I'm not fully operational right now. Please try again later."

    try:
        sentiment = sentiment_pipeline(user_input)[0]
        user_sentiment = sentiment["label"]
        user_score = sentiment["score"]

        prompt_prefix = f"Previous conversation: {chat_history}\n\nUser's message: '{user_input}'. They seem to be feeling {user_sentiment} (confidence: {user_score:.2f})."

        prompt = f"""{prompt_prefix} Respond warmly and with empathy. Offer some gentle advice or strategies for coping, blending it naturally with words of encouragement. Generate a short, relevant motivational quote at the end."""

        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="mixtral-8x7b-32768",
            max_tokens=350,
            temperature=0.7,
            top_p=0.6,
        )

        response = chat_completion.choices[0].message.content
        response = re.sub(r"```.*?```", "", response, flags=re.DOTALL).strip()
        sentence_array = response.split("\n")
        quote = sentence_array.pop()
        formatted_quote = f"<p class='quote'>{quote}</p>"

        return f"{'\n'.join(sentence_array)}\n{formatted_quote}"

    except Exception as e:
        return "I'm sorry, I'm having a bit of trouble processing things right now."

# --- Streamlit UI ---
# st.title("TranquilTalk")  # Uncomment if you want a title

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

if prompt := st.chat_input("How are you feeling today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt, unsafe_allow_html=True)

    chat_history = "\n---\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[:-1]])

    html_element = extract_quote_text(prompt)
    if html_element:
        st.markdown(html_element, unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": html_element})
    else:
        bot_response = get_bot_response(prompt, chat_history)
        with st.chat_message("assistant"):
            full_response = ""
            message_placeholder = st.empty()
            for chunk in bot_response.split():
                full_response += chunk + " "
                time.sleep(0.04)
                message_placeholder.markdown(f"<div style='word-break: break-word;'>{full_response}▌</div>", unsafe_allow_html=True)
            message_placeholder.markdown(f"<div style='word-break: break-word;'>{full_response}</div>", unsafe_allow_html=True)

        st.session_state.messages.append({"role": "assistant", "content": bot_response})
