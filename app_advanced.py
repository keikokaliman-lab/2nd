import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Advanced AI Chatbot",
    page_icon="🤖",
    layout="centered"
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# App title
st.title("🤖 Advanced AI Chatbot")

# Sidebar with settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Model selection
    model = st.selectbox(
        "Choose Model",
        ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"],
        index=0
    )
    
    # Temperature slider
    temperature = st.slider(
        "Temperature (Creativity)",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        help="Higher values make output more random, lower values more focused"
    )
    
    # System prompt
    system_prompt = st.text_area(
        "System Prompt (Optional)",
        placeholder="e.g., You are a helpful coding assistant...",
        help="Define the chatbot's personality and behavior"
    )
    
    st.divider()
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    
    # Download chat history
    if st.button("💾 Download Chat"):
        chat_text = "\n\n".join([
            f"{m['role'].upper()}: {m['content']}" 
            for m in st.session_state.messages
        ])
        st.download_button(
            label="Download as TXT",
            data=chat_text,
            file_name="chat_history.txt",
            mime="text/plain"
        )
    
    st.divider()
    
    # Stats
    st.subheader("📊 Stats")
    st.metric("Messages", len(st.session_state.messages))
    
    st.divider()
    
    st.caption("Built with Streamlit & OpenAI")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Prepare messages for API
    api_messages = []
    
    # Add system prompt if provided
    if system_prompt:
        api_messages.append({"role": "system", "content": system_prompt})
    
    # Add chat history
    api_messages.extend([
        {"role": m["role"], "content": m["content"]} 
        for m in st.session_state.messages
    ])
    
    # Get AI response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Stream the response
            for response in client.chat.completions.create(
                model=model,
                messages=api_messages,
                temperature=temperature,
                stream=True,
            ):
                if response.choices[0].delta.content is not None:
                    full_response += response.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({
                "role": "assistant", 
                "content": full_response
            })
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info("Make sure your OpenAI API key is set correctly in the .env file")


