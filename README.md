# geopulse-ai-app



# 🚀 GeoPulse AI Publisher

This is an AI-powered marketing tool that analyzes real-time, hyper-local signals (Weather, AQI, Holidays, and News) to generate and publish complete, brand-safe social media posts.

The AI pipeline is a multi-step, "Human-in-the-Loop" (HITL) system:

1.  **Fetch:** Gathers live data from 4 different APIs.
2.  **Strategize (Call 1):** An AI Strategist (GPT-4o) analyzes the data, identifies brand-safe triggers (with a fallback for "ambient" triggers), and provides a "Chain-of-Thought" reasoning for its ranked suggestions.
3.  **Approve (HITL):** The user reviews the AI's suggestions and approves or overrides the final trigger.
4.  **Create (Call 2):** An AI Creative (GPT-4o) generates a complete, brand-aligned post, an image prompt, hashtags, and a predictive impact analysis.
5.  **Generate (Call 3):** DALL-E 3 generates a unique, photorealistic image based on the AI-generated prompt.
6.  **Publish:** The final post (image + caption + hashtags) is automatically published to both Discord and Telegram.

## 🛠️ How to Run This Project Locally

Follow these steps to set up and run the application on your own machine.

### 1\. Download the Project

You can either clone this repository or download it as a ZIP.

**With Git (Recommended):**

```bash
git clone https://github.com/YourUsername/geopulse-ai-app.git
cd geopulse-ai-app
```

**As a ZIP:**

1.  Click the green **"\< \> Code"** button on this repository's main page.
2.  Select **"Download ZIP"**.
3.  Unzip the file and open the folder in your terminal.

### 2\. Install Dependencies

You must have Python 3.9+ installed. From your terminal, navigate into the project folder (`geopulse_app/`) and run:

```bash
pip install -r requirements.txt
```

*(Use `pip3` if `pip` is mapped to an older Python version)*

### 3\. Add Your API Keys (CRITICAL)

This app requires 8 secret API keys to function. It is designed to read them from a `secrets.toml` file, which you must create.

1.  While inside the `geopulse_app` folder in your terminal, create the `.streamlit` directory:

    ```bash
    mkdir .streamlit
    ```

2.  Now, create and edit the `secrets.toml` file using a terminal editor:

    ```bash
    nano .streamlit/secrets.toml
    ```

3.  **Paste the following content** into the editor. Replace **every** `"...your_key_here..."` with your actual, valid API key.

    ```toml
    # -------------------------------------
    # GeoPulse AI Secret Keys
    # -------------------------------------

    # --- 1. Signal API Keys ---
    OPENWEATHER_API_KEY = "...your_openweather_key_here..."
    IQAIR_API_KEY = "...your_iqair_key_here..."
    CALENDARIFIC_API_KEY = "...your_calendarific_key_here..."
    NEWS_API_KEY = "...your_newsapi_key_here..."

    # --- 2. AI Keys (Text & Image) ---
    # Must be a "Secret Key" (sk-...) not a "Project Key" (sk-proj-...)
    # Must have billing credits ($5+) added to your OpenAI account.
    OPENAI_API_KEY = "sk-..."

    # --- 3. Publisher Keys ---
    TELEGRAM_BOT_TOKEN = "...your_bot_token_from_botfather..."
    TELEGRAM_CHAT_ID = "-100...your_channel_id_here..."
    DISCORD_WEBHOOK_URL = "httpss://discord.com/api/webhooks/..."
    ```

4.  To save and exit `nano`:

      * Press **`Ctrl + O`** (to "Write **O**ut").
      * Press **`Enter`** (to confirm the file name).
      * Press **`Ctrl + X`** (to E**x**it).

### 4\. Run the Streamlit App

You're all set\! From your terminal, run:

```bash
streamlit run app.py
```

Your browser will automatically open to `http://localhost:8501`, and your GeoPulse AI Publisher will be live.
