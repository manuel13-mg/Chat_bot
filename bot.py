import streamlit as st
import groq
import re
import time
from transformers import pipeline
from bs4 import BeautifulSoup

# --- Configuration ---
st.set_page_config(
    page_title="TranquilTalk",
    page_icon=":heart:",  # Reverted back to heart icon
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- Load Images ---
background_image = "imgss.jpg"  # Local file path for background

# --- CSS Styling ---
st.markdown(
    f"""
<style>
body {{
    font-family: Arial, sans-serif;
    background-color: #000000;
    color: #ffffff;
    background-image: url("{background_image}");
    background-size: cover;
    background-repeat: no-repeat;
}}

.stApp {{
    max-width: 800px;
    margin: 0 auto;
    padding: 30px;
    background-color: rgba(30, 30, 30, 0.8); /* Dark Gray with transparency */
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(128, 128, 128, 0.1);
}}

h1 {{
    color: #ffffff !important;
    text-align: center;
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

# --- Sentiment Analysis Initialization ---
try:
    sentiment_pipeline = pipeline("sentiment-analysis")
    sentiment_analysis_available = True
except Exception as e:
    st.error(f"Error initializing sentiment analysis: {e}")
    sentiment_analysis_available = False

# --- Groq API Initialization ---
try:
    groq_api_key = "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"
    client = groq.Client(api_key=groq_api_key)
    model_available = True
except Exception as e:
    st.error(f"Error initializing Groq client: {e}")
    model_available = True

def extract_quote_text(html_string):
    """Extracts the text content from a <p class='quote'> element."""
    soup = BeautifulSoup(html_string, "html.parser")
    quote_element = soup.find("p", class_="quote")

    if quote_element:
        return str(quote_element)
    else:
        return None

# --- Emotionally Aware Response Function ---
def get_bot_response(user_input: str, chat_history: str) -> str:
    """Generates an empathetic and supportive response from the bot, with a quote."""
    if not model_available:
        return "I'm having trouble connecting. Can't offer advice right now."

    if not sentiment_analysis_available:
        return "I'm not feeling so sensitive right now, can't offer advice."

    try:
        # Analyze user sentiment
        sentiment = sentiment_pipeline(user_input)[0]
        user_sentiment = sentiment["label"]
        user_score = sentiment["score"]

        # Include chat history in the prompt
        prompt_prefix = f"""Previous conversation: {chat_history}\n\nUser's message: '{user_input}'. They seem to be feeling {user_sentiment} (confidence: {user_score:.2f})."""

        prompt = f"""{prompt_prefix} Respond in a warm, human-like way. Acknowledge their feelings with empathy. Then, offer some gentle advice or strategies for coping, blending it naturally with words of encouragement. Use the previous conversation to make the response more relevant and personalized. Generate a short, relevant motivational quote yourself at the end."""

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="mixtral-8x7b-32768",
            max_tokens=350,
            temperature=0.7,
            top_p=0.6,
        )

        response = chat_completion.choices[0].message.content
        response = re.sub(r"```.*?```", "", response, flags=re.DOTALL)
        response = response.strip()

        # Separate the quote from the response
        sentence_array = response.split("\n")
        quote = sentence_array[-1]
        formatted_quote = f"<p class='quote'>{quote}</p>"
        sentence_array.pop()
        response = "\n".join(sentence_array)

        return f"{response}\n{formatted_quote}"

    except Exception as e:
        return "I'm sorry, I'm having a bit of trouble processing things right now."

# --- Streamlit UI ---
st.title("TranquilTalk")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# React to user input
if prompt := st.chat_input("How are you feeling today?"):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt, unsafe_allow_html=True)

    # Prepare chat history for the prompt
    chat_history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[:-1]]) # Exclude the current prompt from the chat history

    # Check if the input is an HTML element to extract and display
    html_element = extract_quote_text(prompt)
    if html_element:
        st.markdown(html_element, unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": html_element})
    else:
        # Get bot response with chat history
        bot_response = get_bot_response(prompt, chat_history)

        # Display bot message with typing effect
        with st.chat_message("assistant"):
            full_response = ""
            message_placeholder = st.empty()
            for chunk in bot_response.split():
                full_response += chunk + " "
                time.sleep(0.04)
                message_placeholder.markdown(f"<div style='word-break: break-word;'>{full_response}▌</div>", unsafe_allow_html=True)
            message_placeholder.markdown(f"<div style='word-break: break-word;'>{full_response}</div>", unsafe_allow_html=True)

        st.session_state.messages.append({"role": "assistant", "content": bot_response})