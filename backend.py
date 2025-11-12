import streamlit as st
from openai import OpenAI
import os
import backend # This imports your backend.py file

# --- 1. Page Configuration & Title ---
st.set_page_config(
    page_title="GeoPulse AI",
    page_icon="🚀",
    layout="wide"
)

# --- 1.5 (NEW) CUSTOM CSS THEME ---
def load_css():
    st.markdown("""
    <style>
    /* Main page background */
    .main .block-container {
        background-color: #0E1117; /* Dark background */
        color: #FAFAFA; /* Light text */
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1a1a2e; /* Dark purple/blue */
        border-right: 1px solid #3c3c5a;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #FAFAFA;
    }
    [data-testid="stSidebar"] [data-testid="stHeader"] {
        color: #FAFAFA;
    }

    /* Buttons */
    [data-testid="stButton"] button {
        background-color: #7540EE; /* Bright purple */
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 14px;
        transition: all 0.3s ease;
        font-weight: 600;
    }
    [data-testid="stButton"] button:hover {
        background-color: #5a2fd6; /* Darker purple */
        box-shadow: 0 4px 12px rgba(117, 64, 238, 0.4);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #FAFAFA;
    }
    
    /* Info boxes (like the 'Rationale') */
    [data-testid="stAlert"] {
        background-color: #1E1E3F; /* Dark blue */
        border: 1px solid #3c3c5a;
        border-radius: 8px;
        color: #FAFAFA;
    }
    [data-testid="stAlert"] * {
        color: #FAFAFA;
    }
    
    /* Radio buttons */
    [data-testid="stRadio"] label {
        background-color: #1E1E3F;
        border: 1px solid #3c3c5a;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 10px;
        transition: all 0.3s ease;
    }
    [data-testid="stRadio"] label:hover {
        border-color: #7540EE;
    }
    
    /* Image caption */
    [data-testid="stImage"] figcaption {
        color: #A0A0B0;
    }

    /* Expander (for signals) */
    [data-testid="stExpander"] summary {
        background-color: #1a1a2e;
        color: #FAFAFA;
        border-radius: 8px;
    }
    
    /* Metrics */
    [data-testid="stMetric"] {
        background-color: #1E1E3F;
        border: 1px solid #3c3c5a;
        border-radius: 8px;
        padding: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Load the CSS
load_css()


# --- 2. Load API Keys & Initialize Clients ---
try:
    keys = {
        "OPENWEATHER_API_KEY": st.secrets["OPENWEATHER_API_KEY"],
        "IQAIR_API_KEY": st.secrets["IQAIR_API_KEY"],
        "CALENDARIFIC_API_KEY": st.secrets["CALENDARIFIC_API_KEY"],
        "NEWS_API_KEY": st.secrets["NEWS_API_KEY"],
        "TELEGRAM_BOT_TOKEN": st.secrets["TELEGRAM_BOT_TOKEN"],
        "TELEGRAM_CHAT_ID": st.secrets["TELEGRAM_CHAT_ID"],
        "DISCORD_WEBHOOK_URL": st.secrets["DISCORD_WEBHOOK_URL"],
        "OPENAI_API_KEY": st.secrets["OPENAI_API_KEY"]
    }
    openai_client = OpenAI(api_key=keys["OPENAI_API_KEY"])
except KeyError as e:
    st.error(f"❌ Missing API Key in secrets.toml: {e}. Please add it and restart the app.")
    st.stop()

# --- 3. Initialize Session State ---
if 'step' not in st.session_state:
    st.session_state.step = "selection"
if 'company_profile' not in st.session_state:
    st.session_state.company_profile = {}
if 'city' not in st.session_state:
    st.session_state.city = ""
if 'live_signals' not in st.session_state:
    st.session_state.live_signals = {}
if 'ranked_triggers' not in st.session_state:
    st.session_state.ranked_triggers = []
if 'final_assets' not in st.session_state:
    st.session_state.final_assets = {}

# --- 4. Main App UI ---
st.title("🚀 GeoPulse AI Publisher")
st.markdown("Your AI co-pilot for creating hyper-local, real-time marketing campaigns.")

# --- 5. Sidebar Controls ---
st.sidebar.title("GeoPulse Controls 🎮")

# --- Step 1: Selection Form ---
st.sidebar.markdown("### Step 1: Choose Your Target")
industry_key = st.sidebar.selectbox("🛍️ Select an Industry:", list(backend.COMPANY_PROFILES.keys()))
brand_options = list(backend.COMPANY_PROFILES[industry_key].keys())
brand_key = st.sidebar.selectbox("🏷️ Select a Brand:", brand_options)
city_key = st.sidebar.selectbox("🏙️ Select a City:", backend.CITIES)
st.sidebar.markdown("---")
analyze_button = st.sidebar.button("🧠 Analyze Signals & Get Triggers", use_container_width=True, type="primary")

# --- 6. Main Content Area (Displays results based on step) ---
main_content = st.container()

if analyze_button:
    st.session_state.company_profile = backend.COMPANY_PROFILES[industry_key][brand_key].copy()
    st.session_state.company_profile['brand_name'] = brand_key.upper()
    st.session_state.company_profile['industry'] = industry_key 
    st.session_state.city = city_key
    
    try:
        with st.spinner(f"📡 Fetching live signals for {city_key}..."):
            st.session_state.live_signals = backend.fetch_live_signals(keys, city_key)
        
        with st.spinner("🤖 AI Strategist is analyzing signals... (Call 1)"):
            st.session_state.ranked_triggers = backend.get_dynamic_triggers_and_tone(
                openai_client, 
                st.session_state.live_signals, 
                st.session_state.company_profile
            )
        
        if not st.session_state.ranked_triggers:
            st.warning("AI Strategist found no brand-safe triggers. Please try different parameters.")
            st.session_state.step = "selection" 
        else:
            st.session_state.step = "approval" 
            st.rerun() 
    
    except Exception as e:
        st.error(f"An error occurred during analysis: {e}")
        st.session_state.step = "selection" 

# --- Step 2: Human-in-the-Loop (HITL) ---
if st.session_state.step == "approval":
    with main_content:
        st.header(f"Step 2: Human-in-the-Loop (HITL) 🧠")
        st.info(f"AI has analyzed **{st.session_state.city}** for **{st.session_state.company_profile['brand_name']}** and suggests these triggers. Please choose one.")

        with st.expander("Show Live Signals Data"):
            st.json(st.session_state.live_signals)
        
        trigger_options = []
        for trigger in st.session_state.ranked_triggers:
            option = f"**{trigger['trigger']}** (Tone: *{trigger['tone']}*) \n\n*AI Rationale: {trigger.get('reasoning', 'N/A')}*"
            trigger_options.append(option)
        
        custom_option = "Other (Type your own trigger)"
        trigger_options.append(custom_option)
        
        chosen_option = st.radio("Select the trigger to proceed:", trigger_options, index=0)
        
        chosen_trigger = ""
        chosen_tone = ""
        
        if chosen_option == custom_option:
            col1, col2 = st.columns(2)
            with col1:
                chosen_trigger = st.text_input("**Enter your custom trigger:**", "Mid-week blues")
            with col2:
                chosen_tone = st.text_input("**Enter your custom tone:**", "Playful and encouraging")
        else:
            for trigger in st.session_state.ranked_triggers:
                if trigger['trigger'] in chosen_option:
                    chosen_trigger = trigger['trigger']
                    chosen_tone = trigger['tone']
                    break

        st.markdown("---")
        
        if st.button("✍️ Generate Creative Assets", use_container_width=True, type="primary"):
            st.session_state.step = "generation"
            st.session_state.final_assets = {
                "trigger": chosen_trigger,
                "tone": chosen_tone
            }
            st.rerun()

# --- Step 3: Generation (Processing) (FIXED) ---
if st.session_state.step == "generation":
    with main_content:
        st.header("Step 3: AI Creative Generation 🎨")
        
        try:
            # Initialize asset variables
            post_text, hashtags, target_audience, predicted_impact_rating, predicted_impact_reasoning = (None, None, None, None, None)
            
            with st.spinner("🤖 AI Creative is writing the post and analysis... (Call 2)"):
                (
                    post_text, 
                    hashtags, 
                    target_audience, 
                    predicted_impact_rating,
                    predicted_impact_reasoning
                ) = backend.generate_creative_assets(
                    openai_client,
                    st.session_state.city,
                    st.session_state.final_assets["trigger"],
                    st.session_state.final_assets["tone"],
                    st.session_state.live_signals,
                    st.session_state.company_profile
                )
            
            # --- THIS IS THE FIX ---
            # We must check if the first call succeeded before trying the second
            if not post_text:
                st.error("❌ AI Creative (Call 2) failed to return valid text. This might be a temporary OpenAI issue. Please try again.")
                st.session_state.step = "approval" # Go back a step
                if st.button("Try Again"):
                    st.rerun()
            
            else:
                # --- If Call 2 succeeded, proceed to Call 3 ---
                with st.spinner(f"🎨 AI Director is writing a safe image prompt... (Call 3)"):
                    image_prompt = backend.generate_safe_image_prompt(
                        openai_client,
                        post_text,
                        st.session_state.company_profile
                    )
                
                if not image_prompt:
                    st.error("❌ AI (Call 3) failed to generate a safe image prompt. Please try again.")
                    st.session_state.step = "approval"
                    if st.button("Try Again"):
                        st.rerun()
                else:
                    # --- If Call 3 succeeded, proceed to Call 4 ---
                    with st.spinner(f"🖼️ DALL-E is generating image for: *{image_prompt}* (Call 4)"):
                        image_path = backend.generate_image_with_dalle(
                            openai_client,
                            image_prompt
                        )
                    
                    # --- Save all 6 assets ---
                    st.session_state.final_assets["post_text"] = post_text
                    st.session_state.final_assets["image_path"] = image_path
                    st.session_state.final_assets["hashtags"] = hashtags
                    st.session_state.final_assets["target_audience"] = target_audience
                    st.session_state.final_assets["predicted_impact_rating"] = predicted_impact_rating
                    st.session_state.final_assets["predicted_impact_reasoning"] = predicted_impact_reasoning
                    
                    st.session_state.step = "review"
                    st.rerun()
            # --- END OF FIX ---

        except Exception as e:
            st.error(f"An error occurred during generation: {e}")
            st.session_state.step = "approval" 
            if st.button("Try Again"):
                st.rerun()

# --- Step 4: Review & Publish (UPGRADED) ---
if st.session_state.step == "review":
    with main_content:
        st.header("Step 4: Review and Publish ✅")
        
        assets = st.session_state.final_assets
        st.info(f"**Trigger:** {assets['trigger']} | **Tone:** {assets['tone']} | **Brand:** {st.session_state.company_profile['brand_name']}")
        
        # --- NEW: AI Analysis Dashboard ---
        st.subheader("🤖 AI Analysis Dashboard")
        col1_metric, col2_metric, col3_metric = st.columns(3)
        with col1_metric:
            st.metric(label="Predicted Impact", value=assets.get('predicted_impact_rating', 'N/A'))
        with col2_metric:
            st.markdown("**Target Audience**")
            st.code(", ".join(assets.get('target_audience', [])))
        with col3_metric:
            st.markdown("**Hashtags**")
            st.code(" ".join(assets.get('hashtags', [])))
        
        st.markdown(f"**Impact Rationale:** *{assets.get('predicted_impact_reasoning', 'N/A')}*")
        st.markdown("---")
        
        # Side-by-side layout for review
        col1_img, col2_cap = st.columns([0.55, 0.45]) # Adjust column ratios
        
        with col1_img:
            st.subheader("Generated Post")
            if assets.get('image_path'):
                st.image(assets['image_path'], caption="AI-Generated Image", use_column_width=True)
            else:
                st.error("Image generation failed.")
        
        with col2_cap:
            st.subheader("Generated Caption")
            st.markdown(assets['post_text'])

        st.markdown("---")
        
        # Publish Buttons
        col1_pub, col2_pub = st.columns(2)
        with col1_pub:
            publish_disabled = assets.get('image_path') is None
            if st.button("🚀 PUBLISH POST", use_container_width=True, type="primary", disabled=publish_disabled):
                with st.spinner("Publishing to Discord & Telegram..."):
                    try:
                        backend.publish_to_discord(
                            keys, assets['post_text'], assets['image_path'], assets['hashtags']
                        )
                        backend.publish_to_telegram(
                            keys, assets['post_text'], assets['image_path'], assets['hashtags']
                        )
                        
                        st.success("🎉 Post published successfully to Discord & Telegram!")
                        st.balloons()
                        st.session_state.step = "done"
                        if os.path.exists(assets['image_path']):
                            os.remove(assets['image_path']) # Clean up
                        st.rerun()

                    except Exception as e:
                        st.error(f"An error occurred during publishing: {e}")
        
        with col2_pub:
            if st.button("Start Over", use_container_width=True):
                if os.path.exists(st.session_state.final_assets.get('image_path', '')):
                    os.remove(st.session_state.final_assets['image_path'])
                st.session_state.clear()
                st.rerun()

# --- Step 5: Done ---
if st.session_state.step == "done":
    with main_content:
        st.success("🎉 Campaign Published Successfully!")
        st.markdown("You can view the post in your configured Discord and Telegram channels.")
        if st.button("Generate Another Post", use_container_width=True, type="primary"):
            st.session_state.clear()
            st.rerun()
