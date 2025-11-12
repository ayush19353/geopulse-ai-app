Here's the direct streamlit link to access the app - 
#  GeoPulse AI Publisher

This is an AI-powered marketing tool that analyzes real-time, hyper-local signals (Weather, AQI, Holidays, and News) to generate and publish complete, brand-safe social media posts.

The AI pipeline is a multi-step, "Human-in-the-Loop" (HITL) system:

1.  **Fetch:** Gathers live data from 4 different APIs.
2.  **Strategize (Call 1):** An AI Strategist (GPT-4o) analyzes the data, identifies brand-safe triggers (with a fallback for "ambient" triggers), and provides a "Chain-of-Thought" reasoning for its ranked suggestions.
3.  **Approve (HITL):** The user reviews the AI's suggestions and approves or overrides the final trigger.
4.  **Create (Call 2):** An AI Creative (GPT-4o) generates a complete, brand-aligned post, an image prompt, hashtags, and a predictive impact analysis.
5.  **Generate (Call 3):** DALL-E 3 generates a unique, photorealistic image based on the AI-generated prompt.
6.  **Publish:** The final post (image + caption + hashtags) is automatically published to both Discord and Telegram.

-----

## 🛠️ How to Run This Project

Follow these steps to set up and run the application on your own machine.

### Step 1: Download the Project

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

### Step 2: Install Dependencies

You must have Python 3.9+ installed. From your terminal, navigate into the project folder (`geopulse_app/`) and run:

```bash
pip install -r requirements.txt
```

*(Use `pip3` if `pip` is mapped to an older Python version)*

### Step 3: Get Your 8 API Keys (CRITICAL)

This app will not run without 8 secret API keys. Follow these steps to get them.

#### 1\. Signal Keys (Weather, AQI, Holiday, News)

  * **OPENWEATHER\_API\_KEY:**
    1.  Go to [openweathermap.org](https://openweathermap.org) and sign up.
    2.  Go to your "API keys" tab to find your key.
  * **IQAIR\_API\_KEY:**
    1.  Go to [iqair.com/commercial/air-quality-api](https://www.google.com/search?q=https://www.iqair.com/commercial/air-quality-api) and click "Get free API access."
    2.  Choose the free "Community" plan and find the key on your dashboard.
  * **CALENDARIFIC\_API\_KEY:**
    1.  Go to [calendarific.com](https://calendarific.com/) and sign up for the free plan.
    2.  Find the key on your account dashboard.
  * **NEWS\_API\_KEY:**
    1.  Go to [newsapi.org](https://newsapi.org/) and click "Get API Key."
    2.  Choose the free "Developer" plan and find the key on your dashboard.

#### 2\. AI Key (OpenAI for Text & DALL-E for Images)

This is the most important key and requires a paid account.

1.  Go to [platform.openai.com](https://platform.openai.com) and create an account.
2.  **CRITICAL:** You must go to the **"Billing"** section and add credits (e.g., $5). The API will not work without this.
3.  Go to the **"API keys"** section.
4.  Click **"+ Create new secret key"**.
5.  Copy the key (it starts with `sk-...`). **Do not use a "Project Key" (sk-proj-...).**

#### 3\. Publisher Keys (Discord & Telegram)

  * **DISCORD\_WEBHOOK\_URL:**
    1.  Create a new Discord server and a new channel (e.g., `#geopulse-alerts`).
    2.  Right-click the channel name -\> **"Edit channel"** -\> **"Integrations"**.
    3.  Click **"Create Webhook"**.
    4.  Name it "GeoPulse Bot" and click **"Copy Webhook URL"**.
  * **TELEGRAM\_BOT\_TOKEN & TELEGRAM\_CHAT\_ID:**
    This is a 2-part process.
      * **Part A: Get the Bot Token**
        1.  In your Telegram app, search for the user **`@BotFather`** (the official one with a blue checkmark) and start a chat.
        2.  Type `/newbot` and send it.
        3.  Follow the prompts. Give it a name (e.g., `GeoPulse Project`) and a username (e.g., `MyGeoPulseTestBot`).
        4.  BotFather will give you your **`TELEGRAM_BOT_TOKEN`**. Copy it.
      * **Part B: Get the Chat ID**
        1.  In Telegram, create a new **public** channel (e.g., "GeoPulse Demo").
        2.  Go to your channel's settings -\> **"Administrators"** -\> **"Add Administrator"**.
        3.  Search for your bot's **username** (e.g., `@MyGeoPulseTestBot`) and add it as an admin.
        4.  Post a test message (e.g., "hello") in your public channel.
        5.  Open a new browser tab and paste this URL, replacing `<YOUR_TOKEN_HERE>` with your new token:
            `https://api.telegram.org/bot<YOUR_TOKEN_HERE>/getUpdates`
        6.  You will see a line of text. Look for `... "chat":{"id":-100...`.
        7.  Copy that number (including the `-100`). This is your **`TELEGRAM_CHAT_ID`**.

### Step 4: Create Your `secrets.toml` File

Now that you have all 8 keys, you must store them securely.

1.  While inside the `geopulse_app` folder in your terminal, create the `.streamlit` directory:

    ```bash
    mkdir .streamlit
    ```

2.  Now, create and edit the `secrets.toml` file using a terminal editor:

    ```bash
    nano .streamlit/secrets.toml
    ```

3.  **Paste the following content** into the editor. Replace **every** placeholder with your 8 API keys.

    ```toml
    # -------------------------------------
    # GeoPulse AI Secret Keys
    # -------------------------------------

    # --- 1. Signal API Keys ---
    OPENWEATHER_API_KEY = "your_openweather_key_here"
    IQAIR_API_KEY = "your_iqair_key_here"
    CALENDARIFIC_API_KEY = "your_calendarific_key_here"
    NEWS_API_KEY = "your_newsapi_key_here"

    # --- 2. AI Keys (Text & Image) ---
    OPENAI_API_KEY = "sk-..."

    # --- 3. Publisher Keys ---
    TELEGRAM_BOT_TOKEN = "your_bot_token_from_botfather"
    TELEGRAM_CHAT_ID = "-100your_channel_id_here"
    DISCORD_WEBHOOK_URL = "httpss://discord.com/api/webhooks/..."
    ```

4.  To save and exit `nano`:

      * Press **`Ctrl + O`** (to "Write **O**ut").
      * Press **`Enter`** (to confirm the file name).
      * Press **`Ctrl + X`** (to E**x**it).

### Step 5: Run the Streamlit App

You're all set\! From your terminal (still inside the `geopulse_app` folder), run:

```bash
streamlit run app.py
```

Your browser will automatically open to `http://localhost:8501`, and your GeoPulse AI Publisher will be live.
