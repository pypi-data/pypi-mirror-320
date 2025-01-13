from huggingface_hub import HfApi, create_repo, upload_file, add_space_variable
from dataclasses import dataclass, field
from typing import Optional
import os


class LicenseManager:
    VALID_LICENSE_KEY = "beta2025"

    @staticmethod
    def validate_license(license_key: str) -> bool:
        """Validate the provided license key."""
        return license_key == LicenseManager.VALID_LICENSE_KEY

@dataclass
class DeploymentResult:
    assistant_url: str
    demo_url: str = None
    integration_guide_url: str = None
    space_status: str = None
    build_logs_url: str = None
    embed_url: str = None    # Add this field


class FAQAssistant:
    def __init__(self, hf_token: str, openai_api_key: str, license_key: str):
        if not LicenseManager.validate_license(license_key):
            raise ValueError("Invalid license key. Please provide a valid license key to use this SDK.")

        self.hf_token = hf_token
        self.openai_api_key = openai_api_key
        self.config = None
        self.api = HfApi(token=hf_token)

    def _generate_streamlit_config(self) -> str:
        """Generate content for .streamlit/config.toml file."""
        return f'''[theme]
        primaryColor = "{self.config.get('PRIMARY_COLOR', '#6B46C1')}"
        secondaryColor = "{self.config.get('SECONDARY_COLOR', '#FF7F50')}"
        backgroundColor = "#FFFFFF"
        secondaryBackgroundColor = "#F0F2F6"
        textColor = "#262730"
        font = "sans serif"

        [server]
        enableCORS = false
        enableXsrfProtection = false

        [browser]
        gatherUsageStats = false

        [runner]
        fastReruns = true

        [client]
        showErrorDetails = false
        toolbarMode = "minimal"'''

    def configure(self,
             # Required OpenAI Settings
             assistant_id: str,

             # Branding & Identity
             agent_name: str,
             agent_subtitle: str,
             logo_url: str = None,
             primary_color: str = "#6B46C1",
             secondary_color: str = "#FF7F50",

             # Chat Interface
             welcome_message: str = None,
             chat_input_placeholder: str = "Ask me anything...",
             thinking_message: str = "Thinking...",
             typing_speed: float = 0.01,

             # UI Elements
             page_icon: str = "🤖",
             user_avatar: str = None,
             assistant_avatar: str = None,

             hf_username=None,
             HF_USERNAME=None,
             space_name=None,
             demo_space_name=None,

             # Conversation Flow
             conversation_starters: list = None,

             # Demo Website
             demo_website: bool = False,
             demo_website_config: dict = None,
             # New Demo Website Fields
             hero_title: str = None,
             hero_subtitle: str = None,
             hero_description: str = None,
             bg_image: str = None):


      self.config = {
          "ASSISTANT_ID": assistant_id,
          "AVATAR_CONFIG": {
              "user": user_avatar or "https://tezzyboy.s3.amazonaws.com/avatars/user_20241221_183530_c2d3a83c.svg",
              "assistant": assistant_avatar or "https://tezzyboy.s3.amazonaws.com/avatars/avatar_20241221_180909_5c30ae3f.svg"
          },
          "LOGO_URL": logo_url,
          "AGENT_NAME": agent_name,
          "HF_USERNAME": hf_username,
          "SPACE_NAME": space_name,
          "AGENT_SUBTITLE": agent_subtitle,
          "WELCOME_MESSAGE": welcome_message or f"Hello! I'm {agent_name}. How can I assist you today?",
          "CHAT_INPUT_PLACEHOLDER": chat_input_placeholder,
          "CONVERSATION_STARTERS": conversation_starters or [
              {"text": "Who are you?", "id": "id1"},
              {"text": "What can you help me with?", "id": "id2"}
          ],
          "PAGE_ICON": page_icon,
          "PRIMARY_COLOR": primary_color,
          "SECONDARY_COLOR": secondary_color,
          "THINKING_MESSAGE": thinking_message,
          "TYPING_SPEED": typing_speed,
          # Add demo website fields to main config
          "HERO_TITLE": hero_title or agent_name,
          "HERO_SUBTITLE": hero_subtitle or agent_subtitle,
          "HERO_DESCRIPTION": hero_description,
          "BG_IMAGE": bg_image
      }

      self.demo_website = demo_website
      self.demo_website_config = demo_website_config or {
          "title": hero_title or agent_name,
          "subtitle": hero_subtitle or agent_subtitle,
          "description": hero_description or "Get instant answers to your questions!",
          "features": [
              "24/7 AI Support",
              "Instant Information",
              "Smart Assistance",
              "Quick Responses"
          ],
          "header_color": primary_color,
          "button_color": secondary_color,
          "enable_faq_section": True,
          "enable_contact_form": True,
          "bg_image": bg_image
      }

      return self

    def _write_file(self, filename: str, content: str):
            """Write content to a temporary file."""
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)

    def _generate_config_file(self) -> str:
        """Generate config.py content."""
        config_content = "# OpenAI Assistant Configuration\n"
        for key, value in self.config.items():
            config_content += f"{key} = {repr(value)}\n\n"
        return config_content

    def _get_app_content(self) -> str:
        """Get the content for app.py"""
        return '''import streamlit as st
import time
from openai import OpenAI
import os
from config import *  # Import all configurations
from customcss1 import CUSTOM_CSS

my_secret = os.environ['OPENAI_API_KEY']
client = OpenAI(api_key=my_secret)

# Thinking Animation
THINKING_DOTS = ["", ".", "..", "..."]
THINKING_INTERVAL = 0.5  # seconds

def ensure_single_thread_id():
    if "thread_id" not in st.session_state:
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id
    return st.session_state.thread_id

def get_avatar(role):
    return AVATAR_CONFIG.get(role)

def get_assistant_response(prompt, thread_id, assistant_id):
    message_placeholder = st.empty()
    i = 0

    # Create message
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=prompt
    )

    # Start streaming
    stream = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
        stream=True
    )

    full_response = ""

    # Stream the response
    for event in stream:
        if not full_response:
            message_placeholder.markdown(f"*Thinking{THINKING_DOTS[i % len(THINKING_DOTS)]}*", unsafe_allow_html=True)
            i += 1
            time.sleep(THINKING_INTERVAL)

        if event.data.object == "thread.message.delta":
            for content in event.data.delta.content:
                if content.type == 'text':
                    full_response += content.text.value
                    formatted_response = f'<div class="fade-in assistant-message">{full_response}▌</div>'
                    message_placeholder.markdown(formatted_response, unsafe_allow_html=True)
                    time.sleep(0.01)

    # Final display without cursor
    formatted_response = f'<div class="fade-in assistant-message">{full_response}</div>'
    message_placeholder.markdown(formatted_response, unsafe_allow_html=True)
    return full_response

st.set_page_config(page_icon=PAGE_ICON)

# Apply custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.markdown("""
    <script>
        function scrollToStarters() {
            setTimeout(() => {
                const container = document.querySelector('.chat-container');
                if (container) {
                    container.scrollTop = container.scrollHeight / 2;
                }
            }, 1000);
        }
        window.addEventListener('load', scrollToStarters);
    </script>
""", unsafe_allow_html=True)

# Logo and header
st.markdown(f"""
    <div class="logo-container">
        <img src="{LOGO_URL}" alt="Logo" class="round-logo">
        <div class="concierge-header">{AGENT_NAME}</div>
        <div class="concierge-subtitle">{AGENT_SUBTITLE}</div>
    </div>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_starter_selected" not in st.session_state:
    st.session_state.conversation_starter_selected = False
if "conversation_starter" not in st.session_state:
    st.session_state.conversation_starter = ""

# Add initial welcome message only once
if 'welcome_message_displayed' not in st.session_state:
    st.session_state.messages.append({"role": "assistant", "content": WELCOME_MESSAGE})
    st.session_state.welcome_message_displayed = True

st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display chat history
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"], avatar=get_avatar(message["role"])):
        if idx == 0 and message["role"] == "assistant":
            st.markdown(f'<div class="fade-in">{message["content"]}</div>', unsafe_allow_html=True)
            # Conversation starter buttons
            col1, col2, col3 = st.columns([1,1,1])
            with col2:
                for starter in CONVERSATION_STARTERS:
                    if st.button(starter["text"]):
                        st.session_state.conversation_starter = starter["text"]
                        st.session_state.conversation_starter_selected = True
        else:
            st.markdown(message["content"], unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Chat input
prompt = st.chat_input(CHAT_INPUT_PLACEHOLDER)
if st.session_state.conversation_starter_selected and not prompt:
    prompt = st.session_state.conversation_starter
    st.session_state.conversation_starter_selected = False

if prompt:
    with st.chat_message("user", avatar=get_avatar("user")):
        st.markdown(prompt, unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": prompt})

    thread_id = ensure_single_thread_id()

    with st.chat_message("assistant", avatar=get_avatar("assistant")):
        assistant_response = get_assistant_response(prompt, thread_id, ASSISTANT_ID)
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
'''


    def _get_css_content(self) -> str:
            """Get the content for customcss1.py"""

            return '''CUSTOM_CSS = """
        <style>
        /* Hide default elements */
        header {visibility: hidden;}
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}

        /* Basic resets and container setup */
        .reportview-container .main .block-container {
            padding-top: 0;
            max-width: 700px;
            padding-right: 1rem;
            padding-left: 1rem;
        }

        /* Animations */
        @keyframes fadeIn {
            0% {opacity: 0;}
            100% {opacity: 1;}
        }

        /* Logo and header styling */
        .logo-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-top: 0;
            padding-top: 0.5rem;
        }

        .round-logo {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            margin-top: 0.5rem;
            padding: 2px;
            opacity: 0;
            animation: fadeIn 1.5s ease-out forwards;
            object-fit: cover;
            aspect-ratio: 1 / 1;
            overflow: hidden;
        }

        .concierge-header {
            font-size: 1.25rem;
            text-align: center;
            margin-top: 0.5rem;
            margin-bottom: 0;
            font-weight: 500;
        }

        .concierge-subtitle {
            text-align: center;
            font-size: 0.9rem;
            margin-top: 0.25rem;
            margin-bottom: 0.5rem;
            padding: 4px 12px;
            border-radius: 4px;
            animation: highlightText 7s ease-in-out infinite;
            display: inline-block;
        }

        /* Chat styling */
        .chat-container {
            display: flex;
            flex-direction: column;
            gap: 1rem;
            padding-bottom: 70px;
        }

        .stChatMessage {
            background-color: #ffffff;
            border-radius: 15px;
            padding: 1.5rem !important;
            margin-bottom: 1rem;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }

        .assistant-message {
            width: 100% !important;
            max-width: 100% !important;
            word-break: break-word !important;
            white-space: pre-wrap !important;
        }

        /* Button styling */
        .stButton > button {
            background-color: #ffffff !important;
            color: #1E88E5 !important;
            border: 1px solid #E3E3E3 !important;
            border-radius: 8px !important;
            padding: 10px 20px !important;
            font-size: 0.9rem !important;
            font-weight: normal !important;
            width: 90% !important;
            margin: 0 auto !important;
            box-shadow: none !important;
            transition: all 0.2s ease;
        }

        .stButton > button:hover {
            background-color: #FF7F50 !important;
            color: white !important;
            border-color: #FF7F50 !important;
            transform: translateY(-1px);
        }

        /* Chat input styling */
        .stChatInput {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: white;
            padding: 1rem;
            border-top: none !important;
            box-shadow: none !important;

            <style>
        }
    """'''

    def _generate_requirements(self) -> str:
        """Generate requirements.txt content."""
        return '''streamlit==1.31.0
openai==1.55.0
python-dotenv==1.0.0
httpx>=0.26.0,<0.29.0
supabase==2.11.0'''

    def _generate_gitignore(self) -> str:
        """Generate .gitignore content."""
        return '''.env
__pycache__/
*.pyc
.DS_Store'''

    def _create_demo_website_content(self, assistant_url: str) -> str:
      bg_image = self.config.get('BG_IMAGE', 'https://i.ibb.co/XjsG1W8/Minimalist-Beige-Cream-Brand-Proposal-Presentation-1.png')
      background_style = f"url('{bg_image}') center/cover no-repeat;" if bg_image else ""

      return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.config['AGENT_NAME']}</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {{
            --primary-color: {self.config.get('PRIMARY_COLOR', '#2B6CB0')};
            --secondary-color: {self.config.get('SECONDARY_COLOR', '#4299E1')};
            --accent-color: #48BB78;
            --text-color: #333;
            --light-gray: #f5f6fa;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Arial', sans-serif;
        }}

        body {{
            line-height: 1.6;
            overflow-x: hidden;
        }}

        /* Navigation */
        nav {{
            position: fixed;
            width: 100%;
            padding: 1rem 5%;
            background: rgba(255, 255, 255, 0.95);
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 1000;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }}

        .logo {{
            font-size: 1.8rem;
            font-weight: bold;
            color: var(--primary-color);
        }}

        .nav-links {{
            display: flex;
            gap: 2rem;
        }}

        .nav-links a {{
            text-decoration: none;
            color: var(--text-color);
            font-weight: 500;
            transition: color 0.3s ease;
        }}

        .nav-links a:hover {{
            color: var(--secondary-color);
        }}

        /* Hero Section */
        .hero {{
            position: relative;
            width: 100%;
            height: 100vh;
            background: url('{bg_image}') center/cover no-repeat;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }}

        .hero-overlay {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.7);
            z-index: 1;
        }}

        .hero-content {{
            position: relative;
            z-index: 2;
            color: white;
            text-align: center;
            padding: 2rem;
        }}

        .hero h1 {{
            font-size: 3.5rem;
            margin-bottom: 1rem;
            animation: fadeInUp 1s ease;
            color: white;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}

        .hero p {{
            font-size: 1.2rem;
            margin-bottom: 2rem;
            animation: fadeInUp 1s ease 0.3s;
            opacity: 0;
            animation-fill-mode: forwards;
            color: white;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }}

        /* Form Styles */
        .cta-form {{
            display: flex;
            gap: 1rem;
            justify-content: center;
            margin-top: 2rem;
            animation: fadeInUp 1s ease 0.6s;
            opacity: 0;
            animation-fill-mode: forwards;
        }}

        .cta-input {{
            padding: 1rem 1.5rem;
            border: none;
            border-radius: 5px;
            font-size: 1rem;
            width: 300px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        .cta-button {{
            padding: 1rem 2rem;
            background: var(--accent-color);
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        .cta-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }}

        /* Chat Widget */
        .chat-widget {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
        }}

        .chat-toggle-button {{
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background-color: {self.config["PRIMARY_COLOR"]};
            color: white;
            border: none;
            cursor: pointer;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
            transition: transform 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .chat-toggle-button:hover {{
            transform: scale(1.1);
        }}

        .chat-toggle-button i {{
            font-size: 24px;
        }}

        .chat-window {{
            position: fixed;
            bottom: 100px;
            right: 20px;
            width: 380px;
            height: 600px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 5px 40px rgba(0, 0, 0, 0.16);
            display: flex;
            flex-direction: column;
            transition: transform 0.3s ease, opacity 0.3s ease;
            transform-origin: bottom right;
        }}

        .chat-window.hidden {{
            opacity: 0;
            transform: scale(0.5);
            pointer-events: none;
        }}

        .chat-header {{
            background-color: {self.config["PRIMARY_COLOR"]};
            padding: 15px;
            border-radius: 12px 12px 0 0;
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .agent-info {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .agent-info img {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            object-fit: cover;
        }}

        .close-button {{
            background: none;
            border: none;
            color: white;
            cursor: pointer;
            font-size: 20px;
            padding: 5px;
        }}

        .chat-content {{
            flex: 1;
            overflow: hidden;
        }}

        .chat-content iframe {{
            width: 100%;
            height: 100%;
            border: none;
        }}

        /* Animations */
        @keyframes fadeIn {{
            0% {{ opacity: 0; }}
            100% {{ opacity: 1; }}
        }}

        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        @keyframes zoomInOut {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.04); }}
            100% {{ transform: scale(1); }}
        }}

        @keyframes scaleIn {{
            from {{
                opacity: 0;
                transform: scale(0.9);
            }}
            to {{
                opacity: 1;
                transform: scale(1);
            }}
        }}

        /* Mobile Responsiveness */
        @media (max-width: 768px) {{
            .nav-links {{ display: none; }}
            .hero h1 {{ font-size: 2.5rem; }}
            .chat-window {{
                width: 100%;
                height: 100%;
                bottom: 0;
                right: 0;
                border-radius: 0;
            }}
            .chat-header {{
                border-radius: 0;
            }}
            .cta-form {{
                flex-direction: column;
                padding: 0 1rem;
            }}
            .cta-input {{ width: 100%; }}
        }}
    </style>
</head>
<body>
    <nav>
        <div class="logo">{self.config['AGENT_NAME']}</div>
        <div class="nav-links">
            <a href="#home">Home</a>
            <a href="#about">About</a>
            <a href="#services">Services</a>
            <a href="#contact">Contact</a>
        </div>
    </nav>

    <section class="hero">
        <div class="hero-overlay"></div>
        <div class="hero-content">
            <h1>{self.config['HERO_TITLE']}</h1>
            <p>{self.config['HERO_SUBTITLE']}</p>
            <p>{self.config['HERO_DESCRIPTION']}</p>
            <div class="cta-form">
                <input type="email" class="cta-input" placeholder="Enter your email" required>
                <button class="cta-button">Get Started</button>
            </div>
        </div>
    </section>

    <!-- Chat Widget -->
    <div id="chat-widget" class="chat-widget">
        <button id="chat-button" class="chat-toggle-button">
            <i class="fas fa-comments"></i>
        </button>
        <div id="chat-window" class="chat-window hidden">
            <div class="chat-header">
                <div class="agent-info">
                    <img src="{self.config['LOGO_URL']}" alt="{self.config['AGENT_NAME']}">
                    <span>{self.config['AGENT_NAME']}</span>
                </div>
                <button id="close-chat" class="close-button">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="chat-content">
                <iframe src="https://{self.config['HF_USERNAME']}-{self.config['SPACE_NAME']}.hf.space/?embed=true"></iframe>
            </div>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const chatButton = document.getElementById('chat-button');
            const chatWindow = document.getElementById('chat-window');
            const closeChat = document.getElementById('close-chat');

            function toggleChat() {{
                chatWindow.classList.toggle('hidden');
            }}

            chatButton.addEventListener('click', toggleChat);
            closeChat.addEventListener('click', toggleChat);
        }});
    </script>
</body>
</html>"""

    def _generate_features_list(self) -> str:
        """Generate HTML list of features."""
        features = self.demo_website_config.get('features', [
            "24/7 AI Support",
            "Instant Answers",
            "Smart Assistance"
        ])
        return '\n'.join([f'<li>{feature}</li>' for feature in features])

    def _generate_faq_items(self) -> str:
        """Generate FAQ items HTML."""
        return '\n'.join([
            f'<div class="faq-item"><h4>{starter["text"]}</h4></div>'
            for starter in self.config['CONVERSATION_STARTERS']
        ])

    def _deploy_demo_website(self, space_id: str) -> str:
        """Deploy demo website to a separate Space."""
        try:
            # Try to delete existing demo space
            try:
                self.api.delete_repo(
                    repo_id=space_id,
                    repo_type="space",
                    token=self.hf_token
                )
                print(f"Deleted existing demo space: {space_id}")
            except Exception as e:
                print(f"No existing demo space to delete or error: {e}")

            # Create new space for demo
            create_repo(
                space_id,
                repo_type="space",
                space_sdk="static",
                token=self.hf_token
            )
            print(f"Created demo space: {space_id}")

            # Create and upload index.html
            demo_content = self._create_demo_website_content(
                f"https://huggingface.co/spaces/{space_id}"
            )
            self._write_file('index.html', demo_content)

            # Upload to Hugging Face
            self.api.upload_file(
                path_or_fileobj='index.html',
                path_in_repo='index.html',
                repo_id=space_id,
                repo_type="space"
            )
            print("Uploaded demo website files")

            # Clean up
            os.remove('index.html')

            return f"https://huggingface.co/spaces/{space_id}"

        except Exception as e:
            print(f"Error deploying demo website: {e}")
            return None


    def deploy(self, hf_username: str, space_name: str, deploy_demo: bool = True, demo_space_name: str = None):
            """Deploy the assistant and optionally a demo website."""
            if not self.config:
                raise ValueError("Assistant must be configured before deployment")

            space_id = f"{hf_username}/{space_name}"
            result = DeploymentResult(
                assistant_url=f"https://huggingface.co/spaces/{space_id}",
                space_status="deploying"
            )

            try:
                # Try to delete existing space
                try:
                    # In the deploy method, add after deploying the main assistant:
                    if self.demo_website and deploy_demo:
                        demo_space_id = f"{hf_username}/{demo_space_name or f'demo-{space_name}'}"
                        result.demo_url = self._deploy_demo_website(demo_space_id)
                        if result.demo_url:
                            print(f"Demo website deployed at: {result.demo_url}")
                    self.api.delete_repo(
                        repo_id=space_id,
                        repo_type="space",
                        token=self.hf_token
                    )
                    print(f"Deleted existing space: {space_id}")
                except Exception as e:
                    print(f"No existing space to delete or error: {e}")

                # Create new space
                create_repo(
                    space_id,
                    repo_type="space",
                    space_sdk="streamlit",
                    token=self.hf_token
                )
                print(f"Created new Space: {space_id}")

                # Add secrets
                add_space_variable(
                    repo_id=space_id,
                    key="OPENAI_API_KEY",
                    value=self.openai_api_key,
                    token=self.hf_token
                )
                print("Added OPENAI_API_KEY to Space secrets")

                # Generate and upload files
                files = {
                    'app.py': self._get_app_content(),
                    'config.py': self._generate_config_file(),
                    'customcss1.py': self._get_css_content(),
                    'requirements.txt': self._generate_requirements(),
                    '.gitignore': self._generate_gitignore()
                }

                # Create .streamlit directory and config file
                os.makedirs('.streamlit', exist_ok=True)
                streamlit_config = self._generate_streamlit_config()
                with open('.streamlit/config.toml', 'w') as f:
                    f.write(streamlit_config)

                

                for filename, content in files.items():
                    # Write file locally
                    self._write_file(filename, content)

                    # Upload to Hugging Face
                    self.api.upload_file(
                        path_or_fileobj=filename,
                        path_in_repo=filename,
                        repo_id=space_id,
                        repo_type="space"
                    )
                    print(f"Uploaded {filename}")

                    # Clean up local file
                    os.remove(filename)

                result.space_status = "deployed"

                # Upload .streamlit/config.toml
                    self.api.upload_file(
                        path_or_fileobj='.streamlit/config.toml',
                        path_in_repo='.streamlit/config.toml',
                        repo_id=space_id,
                        repo_type="space"
                    )
                    print("Uploaded .streamlit/config.toml")

                print(f"\n=== 🎉 Deployment Complete! ===")
                print(f"Assistant URL: {result.assistant_url}")
                print(f"Demo Website: {result.demo_url}")

                print("\n=== 🔌 Integration Code ===")
                print("Add this code to your website:")
                print(f"""
            <!-- Chat Widget -->
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">

            <div id="chat-widget" class="chat-widget">
                <button id="chat-button" class="chat-toggle-button">
                    <i class="fas fa-comments"></i>
                </button>
                <div id="chat-window" class="chat-window hidden">
                    <div class="chat-header">
                        <div class="agent-info">
                            <img src="{self.config['LOGO_URL']}" alt="{self.config['AGENT_NAME']}">
                            <span>{self.config['AGENT_NAME']}</span>
                        </div>
                        <button id="close-chat" class="close-button">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="chat-content">
                        <iframe src="https://{hf_username}-{space_name}.hf.space/?embed=true" frameborder="0" width="100%" height="100%"></iframe>
                    </div>
                </div>
            </div>

            <style>
            .chat-widget {{
                position: fixed;
                bottom: 20px;
                right: 20px;
                z-index: 1000;
            }}

            .chat-toggle-button {{
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background-color: {self.config.get('PRIMARY_COLOR', '#6B46C1')};
                color: white;
                border: none;
                cursor: pointer;
                box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                display: flex;
                align-items: center;
                justify-content: center;
                transition: transform 0.3s ease;
            }}

            .chat-toggle-button:hover {{
                transform: scale(1.1);
            }}

            .chat-toggle-button i {{
                font-size: 24px;
            }}

            .chat-window {{
                position: fixed;
                bottom: 100px;
                right: 20px;
                width: 380px;
                height: 600px;
                background: white;
                border-radius: 12px;
                box-shadow: 0 5px 40px rgba(0,0,0,0.16);
                display: none;
            }}

            .chat-window.active {{
                display: block;
            }}

            .chat-header {{
                background-color: {self.config.get('PRIMARY_COLOR', '#6B46C1')};
                padding: 15px;
                border-radius: 12px 12px 0 0;
                color: white;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}

            .agent-info {{
                display: flex;
                align-items: center;
                gap: 10px;
            }}

            .agent-info img {{
                width: 40px;
                height: 40px;
                border-radius: 50%;
            }}

            .close-button {{
                background: none;
                border: none;
                color: white;
                cursor: pointer;
                font-size: 20px;
                padding: 5px;
            }}

            .chat-content {{
                height: calc(100% - 70px);
            }}

            .chat-content iframe {{
                width: 100%;
                height: 100%;
                border: none;
            }}
            </style>

            <script>
            document.addEventListener('DOMContentLoaded', function() {{
                const chatButton = document.getElementById('chat-button');
                const chatWindow = document.getElementById('chat-window');
                const closeChat = document.querySelector('.close-button');

                chatButton.addEventListener('click', () => {{
                    chatWindow.classList.toggle('active');
                }});

                closeChat.addEventListener('click', () => {{
                    chatWindow.classList.remove('active');
                }});
            }});
            </script>
            """)

                print("\n📱 Integration Options:")
                print("1. Copy the full widget code for a floating chat button")
                print("2. Or use this simple iframe for a basic embed:")
                print(f"""<iframe
                src="https://{hf_username}-{space_name}.hf.space/?embed=true"
                frameborder="0"
                width="100%"
                height="700px">
            </iframe>""")

                return result



            except Exception as e:
                print(f"Error in deployment: {str(e)}")
                result.space_status = "error"
                raise
