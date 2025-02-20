import streamlit as st
import groq
import time
import base64

# --- Load Favicon ---
def load_favicon(filepath):
    try:
        with open(filepath, "rb") as f:
            image_data = f.read()
        base64_encoded = base64.b64encode(image_data).decode('utf-8')
        return base64_encoded
    except FileNotFoundError:
        st.error(f"Favicon file not found: {filepath}")
        return None

def load_image(filepath):
    try:
        with open(filepath, "rb") as f:
            image_data = f.read()
        base64_encoded = base64.b64encode(image_data).decode('utf-8')
        return base64_encoded
    except FileNotFoundError:
        st.error(f"Image file not found: {filepath}")
        return None


favicon_path = "Picsart_25-02-19_20-54-44-943-removebg-preview.png" # Replace with your icon file
favicon_base64 = load_favicon(favicon_path)

# --- Configuration ---
st.set_page_config(
    page_title="CHAT MESH",  # Changed chatbot name here
    page_icon=f"data:image/png;base64,{favicon_base64}" if favicon_base64 else ":brain:",  # Use base64 if available, otherwise default
    layout="wide",  # Use wide layout
)

# --- CSS Styling ---
st.markdown(
    """
    <style>
    body {
        font-family: sans-serif;
        background-color: #1E1E1E; /* Dark background */
        color: #FFFFFF; /* Light text for contrast */
    }

    .stApp {
        background-color: #282828; /* Slightly lighter container background */
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
        padding: 10px;
    }

    h1 {
        color: #FFFFFF !important; /* White header */
        text-align: left;
        margin-bottom: 0px;
    }

    .stTextInput>label {
        color: #FFFFFF; /* Light input label */
    }

    .stButton>button {
        background-color: #4CAF50; /* Green button */
        color: #FFFFFF; /* Light text on button */
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }

    .stButton>button:hover {
        background-color: #388E3C;
    }

    .stAlert {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 10px;
        margin-top: 10px;
    }

    .chat-message {
        padding: 10px;
        margin-bottom: 5px;
        border-radius: 5px;
        color: #FFFFFF; /* White text in chat messages */
    }

    .user-message {
        background-color: #4CAF50; /* Green for user messages */
        text-align: right;
    }

    .bot-message {
        background-color: #2c3e50; /* Darker blue for bot messages */
        text-align: left;
    }

     p {
        color: #FFFFFF; /* White paragraph text */
    }

    /* Sidebar styles */
    [data-testid="stSidebar"] {
        background-color: #1E1E1E;
        color: #FFFFFF;
    }

    [data-testid="stSidebar"] h1 {
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] .stButton>button {
        background-color: #61dafb;
        color: #282c34;
    }

    /* Center the image */
    .image-container {
        display: flex;
        justify-content: center;
        margin-bottom: 20px; /* Adjust as needed */
    }

    .chatbot-image {
        width: 500px; /* Adjust as needed */
        border-radius: 10px; /* Optional: for rounded corners */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


def clear_chat():
    """Clears the chat history in session state."""
    st.session_state.messages = []

def logout():
    """Logs the user out."""
    st.session_state.logged_in = False
    st.session_state.messages = []

# --- Sidebar ---
def sidebar():
    with st.sidebar:
        st.image("https://avatars.githubusercontent.com/u/105322807?s=200&v=4", width=80)  # Replace with your logo
        st.title("CHAT MESH")  # Changed chatbot name here
        st.markdown("[AI Chat Helper](#)")
        st.markdown("[Templates](https://streamlit.io) [PRO](https://streamlit.io)")  # Replace with your links
        st.markdown("[My Projects](https://streamlit.io) [PRO](https://streamlit.io)")
        st.markdown("[Statistics](https://streamlit.io) [PRO](https://streamlit.io)")
        st.markdown("[Settings](https://streamlit.io)")
        st.markdown("[Updates & FAQ](https://streamlit.io)")

        st.markdown("---")
        st.subheader("Pro Plan")
        st.markdown("Strengthen artificial intelligence: get plan!")
        st.markdown("$10/mo [Get](https://streamlit.io)")  # Replace with your link

        st.markdown("---")
        st.button("Log Out", on_click=logout) # Removed pass, already handled by `logout`
        st.markdown("---")
        new_chat_button = st.button("New Chat", on_click=clear_chat)

# --- Initialize Groq Client ---
try:
    groq_api_key = "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"  # Use the provided API key
    client = groq.Client(api_key=groq_api_key)
    model_available = True
except Exception as e:
    st.error(f"Error initializing Groq client: {e}")
    print(e)  # Print the actual error message for debugging.
    model_available = False


def generate_response(prompt, history):
    """Generates a response from the Groq model with typing effect, considering chat history."""
    try:
        # Add a system message to set the bot's persona
        system_message = {
            "role": "system",
            "content": "You are a helpful and friendly assistant. When greeted, respond with a warm welcome and offer assistance.",
        }

        messages = [system_message]  # Start with the system message
        for role, content in history:
            messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",  # You can change the model if needed
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=0.7,
            stream=True,  # Enable streaming for typing effect
        )

        full_response = ""
        placeholder = st.empty()  # Create an empty placeholder to update
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                full_response += chunk.choices[0].delta.content
                placeholder.markdown(f'<span style="color:#FFFFFF;">{full_response}</span>▌', unsafe_allow_html=True)  # Add a cursor with white color
                time.sleep(0.05)  # Adjust the typing speed here (increased to 0.05)
        placeholder.markdown(f'<span style="color:#FFFFFF;">{full_response}</span>', unsafe_allow_html=True)  # remove cursor when typing is done

        return full_response

    except Exception as e:
        st.error(f"Error generating response: {e}")
        return "Sorry, I encountered an error."

# --- Main App Logic ---

if not st.session_state.logged_in:
    # --- Login Page ---
    st.title("Welcome to CHAT MESH")  # Changed chatbot name here
    st.write("Please log in to continue.")
    username = st.text_input("Username", value="mg13")  # Default username
    password = st.text_input("Password", type="password", value="manuel123")  # Default password
    if st.button("Log In"):
        # Authentication logic (using the default credentials)
        if username == "mg13" and password == "manuel123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid credentials.")
else:
    # --- Chat Interface ---
    sidebar()  # Display the sidebar

    # --- Top Image ---
    image_path = "my_image.png"  # Replace with your image file name
    image_base64 = load_image(image_path)
    if image_base64:
        st.markdown(
            f"""
            <div class="image-container">
                <img class="chatbot-image" src="data:image/png;base64,{image_base64}" alt="Chatbot Image">
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.warning("Could not load image. Make sure the file exists and is accessible.")

    # No columns needed now that we're not using the right panel
    ##st.title("CHAT MESH")  # Changed chatbot name here

    # --- Chat Messages ---
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # --- Chat Input (Moved to the Bottom) ---
    if model_available:
        if prompt := st.chat_input("Start typing"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            # Display user message in chat container
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate a response

            with st.chat_message("assistant"):  # Add assistant chat message here
                # Prepare the chat history for the model
                chat_history = [(msg["role"], msg["content"]) for msg in st.session_state.messages]
                full_response = generate_response(prompt, chat_history)

            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
    else:
        st.warning("The Groq model is not available.")