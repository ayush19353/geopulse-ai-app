import os
import requests
import urllib3
import json 
import time 
from datetime import date
from openai import OpenAI
from PIL import Image 
from io import BytesIO 

# --- 0. Disable Annoying Warnings ---
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- 1.5 COMPANY PROFILES ---
CITIES = ["Delhi", "Mumbai", "Bengaluru", "Kolkata", "Chennai", "Hyderabad"]
CITY_STATES = {
    "Delhi": "Delhi", "Mumbai": "Maharashtra", "Bengaluru": "Karnataka",
    "Kolkata": "West Bengal", "Chennai": "Tamil Nadu", "Hyderabad": "Telangana"
}
COMPANY_PROFILES = {
    "Fashion": {
        "h&m": { 
            "industry": "Fashion",
            "voice": "Trendy, affordable, inclusive, and fun. Focus on self-expression and seasonal styles. Use emojis. (e.g., #HM)",
            "product_examples": ["graphic tees", "summer dresses", "denim jackets"]
        },
        "zara": { 
            "industry": "Fashion",
            "voice": "High-fashion, sophisticated, minimalist, and fast-moving. Less emojis.", 
            "product_examples": ["blazers", "structured coats", "leather boots"] 
        }
    },
    "Food & Q-Commerce": {
        "zomato": { 
            "industry": "Food & Q-Commerce",
            "voice": "Witty, playful, relatable, and very food-centric. Uses humor, puns.", 
            "product_examples": ["Biryani", "Pizza", "Restaurant deals"] 
        },
        "swiggy": { 
            "industry": "Food & Q-Commerce",
            "voice": "Fast, reliable, and convenient. Focus on speed ('Delivered in minutes').", 
            "product_examples": ["Restaurant food", "Instamart groceries", "Snacks"] 
        }
    },
    "Electronics": {
        "croma": { 
            "industry": "Electronics",
            "voice": "Helpful, tech-savvy, and trustworthy. Focus on features, sales, offers.", 
            "product_examples": ["Smartphones", "Laptops", "Air Conditioners"] 
        },
        "reliance digital": { 
            "industry": "Electronics",
            "voice": "Wide range, best prices, and cutting-edge technology. Focus on big deals.", 
            "product_examples": ["New-launch TVs", "Gaming laptops", "Smart watches"] 
        }
    }
}

# --- 2. PUBLISHER FUNCTIONS ---
def publish_to_telegram(keys, message_text, image_path, hashtags):
    print(f"[Publisher] Attempting to post to Telegram...")
    url = f"https.://api.telegram.org/bot{keys['TELEGRAM_BOT_TOKEN']}/sendPhoto"
    try:
        hashtag_string = " ".join(hashtags)
        full_caption = f"{message_text}\n\n{hashtag_string}"
        
        with open(image_path, 'rb') as photo_file:
            payload_data = {'chat_id': keys['TELEGRAM_CHAT_ID'], 'caption': full_caption, 'parse_mode': 'Markdown'}
            files_to_send = {'photo': photo_file}
            response = requests.post(url, data=payload_data, files=files_to_send)
            response.raise_for_status() 
            print("[Publisher] ✅ SUCCESS! Post sent to your Telegram channel.")
            return True, "Success"
    except Exception as e:
        print(f"[Publisher] ❌ FAILED to post to Telegram: {e}")
        return False, str(e)

def publish_to_discord(keys, message_text, image_path, hashtags):
    print(f"[Publisher] Attempting to post to Discord...")
    try:
        hashtag_string = " ".join(hashtags)
        full_message = f"{message_text}\n\n{hashtag_string}"
        
        payload_json = json.dumps({'content': full_message})
        with open(image_path, 'rb') as image_file:
            files_to_send = {
                'file1': (os.path.basename(image_path), image_file, 'image/png'),
                'payload_json': (None, payload_json)
            }
            response = requests.post(keys['DISCORD_WEBHOOK_URL'], files=files_to_send)
            response.raise_for_status() 
            print("[Publisher] ✅ SUCCESS! Post sent to your Discord channel.")
            return True, "Success"
    except Exception as e:
        print(f"[Publisher] ❌ FAILED to post to Discord: {e}")
        return False, str(e)


# --- 3. CREATIVE ASSETS GENERATOR (OpenAI) ---

def generate_image_with_dalle(openai_client, image_prompt):
    """
    Uses DALL-E 3 to generate an image, download it, and save it to a temp file.
    """
    print("[DALL-E] Generating image... (Call 3)")
    try:
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=image_prompt,
            n=1,
            size="1024x1024",
            quality="standard",
            response_format="url" 
        )
        image_url = response.data[0].url
        print(f"[DALL-E] ✅ Image generated: {image_url}")
        
        print("[DALL-E] Downloading image...")
        image_response = requests.get(image_url)
        image_response.raise_for_status()
        
        image = Image.open(BytesIO(image_response.content))
        temp_image_path = "temp_image.png"
        image.save(temp_image_path)
        
        print(f"[DALL-E] ✅ Image saved to {temp_image_path}")
        return temp_image_path
        
    except Exception as e:
        print(f"[DALL-E] ❌ FAILED to generate image: {e}")
        raise e

def generate_creative_assets(openai_client, city, trigger, tone, live_signal, company_profile):
    """
    This is the new master function.
    It generates post text, image prompt, hashtags, AND Audience/Impact analysis.
    """
    print(f"--- Generating Creative Assets for {city} ---")
    try:
        signal_summary = (
            f"Current conditions in {city}: "
            f"Weather is {live_signal.get('condition')} ({live_signal.get('temp')}°C), "
            f"AQI is {live_signal.get('aqi')}. "
            f"Today's Holiday: {live_signal.get('holiday', 'None')}. "
            f"Top Event/News: {live_signal.get('top_event', 'None')}."
        )
        
        # --- THIS IS THE FIX: A much stricter DALL-E SAFETY GUARDRAIL ---
        system_prompt = f"""
        You are an expert social media manager and marketing strategist for the brand *{company_profile['brand_name']}*.
        Your brand voice is: *{company_profile['voice']}*
        Your relevant products are: *{", ".join(company_profile['product_examples'])}*
        
        You MUST generate six things in a JSON format:
        1.  `post_text`: A short, ready-to-publish social media post (under 500 characters).
        2.  `image_prompt`: A concise, visually descriptive DALL-E prompt.
        3.  `hashtags`: A JSON array of 3-5 relevant and trending hashtags.
        4.  `target_audience`: A JSON array of 2-3 specific audience segments this post will appeal to.
        5.  `predicted_impact_rating`: A single rating ("High", "Medium", or "Low") of this post's potential.
        6.  `predicted_impact_reasoning`: A 1-sentence analysis of *why* this post will perform well.

        **DALL-E SAFETY GUARDRAIL (CRITICAL):**
        The `image_prompt` MUST be 100% brand-safe and positive.
        - **FOCUS ON THE POSITIVE SOLUTION, NOT THE NEGATIVE PROBLEM.**
        - **UNSAFE (Negative Problem):** "A person coughing in a hazy city."
        - **SAFE (Positive Solution):** "A happy person indoors, enjoying a fresh pizza, with a window showing a *blurry* city skyline."
        - **BE LITERAL AND DESCRIPTIVE.** Avoid all metaphors (e.g., "explosion of flavor", "killer deal").
        - **DO NOT** use any words related to violence, harm, negativity, or suffering (e.g., "attack", "choke", "trap", "suffer").
        - Your prompt must be a *literal description* of a positive, safe scene.
        
        Respond *ONLY* with a valid JSON object.
        """
        # --- END OF FIX ---
        
        user_prompt = f"""
        **City:** {city}
        **Live Data:** {signal_summary}
        **Chosen Trigger:** "{trigger}"
        **Chosen Tone:** "{tone}"
        """

        print("[OpenAI] Asking GPT-4o for full creative package... (Call 2)")
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            response_format={ "type": "json_object" }, 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        data = json.loads(response.choices[0].message.content)
        final_post_text = data.get("post_text")
        image_prompt = data.get("image_prompt")
        hashtags = data.get("hashtags")
        target_audience = data.get("target_audience") 
        predicted_impact_rating = data.get("predicted_impact_rating")
        predicted_impact_reasoning = data.get("predicted_impact_reasoning")
        
        if not all([final_post_text, image_prompt, hashtags, target_audience, predicted_impact_rating, predicted_impact_reasoning]):
            print(f"[OpenAI] ERROR: LLM JSON was missing one or more required keys. Got: {data}")
            raise Exception("LLM JSON was missing required keys.")
            
        print("[OpenAI] ✅ Full creative package generated.")
        print(f"[OpenAI] DALL-E Prompt: {image_prompt}")
        print(f"[OpenAI] Hashtags: {hashtags}")
        print(f"[OpenAI] Target Audience: {target_audience}")
        print(f"[OpenAI] Impact: {predicted_impact_rating} - {predicted_impact_reasoning}")

        image_file_path = generate_image_with_dalle(openai_client, image_prompt)
        
        return final_post_text, image_file_path, hashtags, target_audience, predicted_impact_rating, predicted_impact_reasoning

    except Exception as e:
        print(f"[OpenAI] ERROR generating creative assets: {e}")
        raise e

# --- 4. DYNAMIC STRATEGIST FUNCTION (OpenAI) ---
def get_dynamic_triggers_and_tone(openai_client, live_signal: dict, company_profile: dict):
    industry = company_profile['industry']
    print(f"[Strategist] Analyzing signals for a {industry} brand: {live_signal} (Call 1)")
    
    try:
        system_prompt = f"""
        You are a marketing strategist for a *{industry}* brand with this voice: *{company_profile['voice']}*.
        Your task is to analyze live data and identify *all* commercially-valuable triggers.
        
        Priority Guide:
        1.  **High Priority:** Mass Cultural Events (Holidays, Sports) and Safety/Urgency Triggers (Heavy Rain, AQI > 200).
        2.  **Low Priority:** Ambient Triggers (e.g., Clear Skies, Haze, regular news).
        
        **BRAND SAFETY GUARDRAIL:**
        You MUST ignore any triggers that are negative, tragic, or politically sensitive. Focus only on positive or neutral events.

        **FALLBACK RULE:**
        If no High Priority triggers are found, you MUST identify and return at least one Low Priority 'Ambient' trigger.
        
        **TASK:**
        Return a JSON object with a key "triggers", which is a JSON list of all *brand-safe* triggers, ranked by priority.
        For each trigger, provide a 'trigger', 'tone', and 'reasoning'.
        
        Respond *ONLY* with a valid JSON object.
        Example:
        {{"triggers": [
          {{"trigger": "India Cricket Match", "tone": "Passionate and exciting", "reasoning": "High-priority cultural event."}},
          {{"trigger": "Hazy Day", "tone": "Cozy and relaxed", "reasoning": "Low-priority ambient trigger."}}
        ]}}
        """
        user_prompt = f"Here is the live data: {live_signal}"
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            response_format={ "type": "json_object" }, 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        response_text = response.choices[0].message.content
        data = json.loads(response_text)
        ranked_triggers = data.get("triggers", []) 
        
        if not ranked_triggers:
             print("[Strategist] Error: LLM returned an empty list, but should have used fallback.")
             return []
             
        return ranked_triggers 
            
    except Exception as e:
        print(f"[Strategist] ERROR analyzing signals: {e}")
        raise e

# --- 5. SIGNAL FETCHER (API Calls) ---
def fetch_live_signals(keys, city: str):
    print(f"[Signal] Fetching all signals for: {city}")
    signals = {}
    today = date.today()
    
    # 1. Fetch Weather
    try:
        weather_url = f"https.://api.openweathermap.org/data/2.5/weather?q={city}&appid={keys['OPENWEATHER_API_KEY']}&units=metric"
        weather_res = requests.get(weather_url, verify=False)
        weather_res.raise_for_status()
        weather_data = weather_res.json()
        signals['temp'] = weather_data['main']['temp']
        signals['condition'] = weather_data['weather'][0]['main']
    except Exception as e:
        print(f"[Signal] FAILED to fetch Weather: {e}")
        signals['temp'] = "N/A"
        signals['condition'] = "N/A"

    # 2. Fetch AQI
    try:
        state = CITY_STATES.get(city) 
        if not state: raise Exception(f"City state not found for {city}")
        aqi_url = f"https.://api.iqair.com/v2/city?city={city}&state={state}&country=India&key={keys['IQAIR_API_KEY']}"
        aqi_res = requests.get(aqi_url, verify=False)
        aqi_res.raise_for_status()
        aqi_data = aqi_res.json()
        signals['aqi'] = aqi_data['data']['current']['pollution']['aqius']
    except Exception as e:
        print(f"[Signal] FAILED to fetch AQI: {e}")
        signals['aqi'] = "N/A"

    # 3. Fetch Holiday / Festival
    signals['holiday'] = "None" 
    try:
        cal_url = (f"https.://calendarific.com/api/v2/holidays"
                   f"?api_key={keys['CALENDARIFIC_API_KEY']}&country=IN&year={today.year}"
                   f"&month={today.month}&day={today.day}")
        cal_res = requests.get(cal_url, verify=False)
        cal_res.raise_for_status()
        holidays = cal_res.json().get('response', {}).get('holidays', [])
        if holidays: signals['holiday'] = holidays[0]['name']
    except Exception as e:
        print(f"[Signal] FAILED to fetch Holiday: {e}")

    # 4. Fetch Sports / Event News
    signals['top_event'] = "None" 
    try:
        news_url = (f"https.://newsapi.org/v2/everything"
                    f"?q=({city} AND (sports OR event OR match))"
                    f"&apiKey={keys['NEWS_API_KEY']}&sortBy=relevancy&pageSize=1")
        news_res = requests.get(news_url, verify=False)
        news_res.raise_for_status()
        articles = news_res.json().get('articles', [])
        if articles: signals['top_event'] = articles[0]['title']
    except Exception as e:
        print(f"[Signal] FAILED to fetch NewsAPI/Events: {e}")
        
    print(f"[Signal] Completed signal fetch: {signals}")
    return signals
