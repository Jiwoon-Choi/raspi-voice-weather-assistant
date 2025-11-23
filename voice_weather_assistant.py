import speech_recognition as sr
import requests
import subprocess
from datetime import datetime, timedelta, time as dtime

# ==================
# CONFIG
# ==================

API_KEY = "1651b8315a7c33a5b6d901fc050504a5"  # Your OpenWeatherMap API KEY
DEFAULT_COUNTRY = ""  # You can change this or set to "" to not force a country
UNITS = "metric"  # "metric" for Celsius, "imperial" for Fahrenheit
LANG = "en"  # "en" for English

# Microphone device index (you may need to adjust if you have multiple devices)
MIC_INDEX = 0  # None = default mic.

# ==================
# SPEECH RECOGNITION
# ==================

def listen_once(timeout=10, phrase_time_limit=10):
    """Listen once from the microphone and return recognized text (lowercased)."""
    r = sr.Recognizer()
    with sr.Microphone(device_index=MIC_INDEX) as source:
        print("\n[1] Adjusting for ambient noise...")
        r.adjust_for_ambient_noise(source, duration=0.5)
        
        print("[2] Say your weather query (e.g. 'What's the weather in Seoul tomorrow?')")
        try:
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            print("[!] No speech detected within 10 seconds.")
            return None
        
        print("[3] Got audio, sending to Google for recognition...")
        try:
            text = r.recognize_google(audio, language="en-US")
            print("[4] You said:", text)
            return text.lower()
        except sr.UnknownValueError:
            print("[!] Google Speech Recognition could not understand audio.")
        except sr.RequestError as e:
            print(f"[!] Could not request results from Google STT: {e}")
        return None
    
# ==================
# NATURAL LANGUAGE UNDERSTANDING (CITY + TIME)
# ==================

DAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
    }

TIME_WORDS = {
    "today", "tomorrow", "tonight", "now", "right", "right now", "this",
    "morning", "afternoon", "evening", "night",
    "day", "after",
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
    }

def interpret_day(text, now=None):
    """Return a date object based on words like 'today', 'tomorrow', 'monday', etc."""
    if now is None:
        now = datetime.now()
    t = text.lower()
    
    # Relative expressions
    if "day after tomorrow" in t:
        return (now + timedelta(days=2)).date()
    if "tomorrow" in t:
        return (now + timedelta(days=1)).date()
    if "today" in t or "right now" in t or "now" in t:
        return now.date()
    
    # Days during the week
    for day, idx in DAYS.items():
        if day in t:
            today_idx = now.weekday()
            offset = (idx - today_idx) % 7
            return (now + timedelta(days=offset)).date()
    
    # Default: assume today
    return now.date()

def interpret_part_of_day(text):
    """Return an hour (int) representing time-of-day based on words like 'morning', 'evening'."""
    t = text.lower()
    if "morning" in t:
        return 9  # 09:00
    if "afternoon" in t:
        return 15  # 15:00
    if "evening" in t or "tonight" in t:
        return 18  # 18:00
    if "night" in t:
        return 21  # 21:00
    # Default: mid-day
    return 12

def extract_city(text):
    """
    Try to extract city name from the recognized text.
    Simple heuristic:
    - If 'in' is present, take words after 'in' and remove time-related words at the end.
    - Otherwise, aassume words other than TIME_WORDS refer to a city
    """
    
    t = text.lower()
    
    # If user says "quit" or "exit", do not treat the command as city
    if "quit" in t or "exit" in t:
        return None
    
    if " in " in t:
        after_in = t.split(" in ", 1)[1]
        words = after_in.split()
    else:
        words = t.split()
    
    # Remove trailing time words (today, tomorrow, monday, morning, etc.)
    cleaned = []
    for w in words:
        if w not in TIME_WORDS:
            cleaned.append(w)
    
    if not cleaned:
        return None
    
    # For now, assume city name is remaining words joined
    city = " ".join(cleaned)
    # Capitalize each word: "new york" -> "New York"
    city = " ".join(part.capitalize() for part in city.split())
    return city

# ==================
# WEATHER API HELPERS
# ==================

def get_current_weather(city):
    """Call the current weather API for a given city name."""
    q = city if not DEFAULT_COUNTRY else f"{city},{DEFAULT_COUNTRY}"
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": q,
        "units": UNITS,
        "lang": LANG,
        "appid": API_KEY,
        }
    print(f"[API] Requesting current weather for {q}...")
    resp = requests.get(url, params=params, timeout=8)
    data = resp.json()
    if str(data.get("cod")) != "200":
        print("[!] API error:", data.get("message"))
        return None
    return data

def get_forecast(city):
    """Call the 5-day/3-hour forecast API for a given city name."""
    q = city if not DEFAULT_COUNTRY else f"{city},{DEFAULT_COUNTRY}"
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": q,
        "units": UNITS,
        "lang": LANG,
        "appid": API_KEY,
        }
    print(f"[API] Requesting forecast for {q}...")
    resp = requests.get(url, params=params, timeout=8)
    data = resp.json()
    if str(data.get("cod")) != "200":
        print("[!] Forecast API error:", data.get("message"))
        return None
    return data

"""def get_forecast(city):
    url = "https://api.openweathermap.org/data/2.5/forecast"
    q = city
    
    params = {
        "q": q,
        "units": UNITS,
        "lang": LANG,
        "appid": API_KEY,
        }
    
    print("[DEBUG] Forecast city:", city)
    print("[DEBUG] Forecast q param:", q)
    print("[DEBUG] Forecast params:", params)
    
    try:
        resp = requests.get(url, params=params, timeout=5)
    except requests.exceptions.RequestException as e:
        print("[!] Network error in forecast:", e)
        return None

    print("[DEBUG] HTTP status:", resp.status_code)
    print("[DEBUG] Raw forecast response:", resp.text[:400])
    
    try:
        data = resp.json()
    except ValueError:
        print("[!] Could not parse forecast JSON")
        return None
    
    print("[DEBUG] Parsed forecast JSON:", data)
    
    if str(data.get("cod")) != "200":
        print("[!] Forecast API error:", data.get("message"), "(cod:", data.get("cod"), ")")
        return None
    
    return data"""

def pick_best_forecast_entry(data, target_dt):
    """Pick the forecast entry whose dt_txt is closest to target_dt."""
    best = None
    best_diff = None
    for entry in data.get("list", []):
        entry_dt = datetime.strptime(entry["dt_txt"], "%Y-%m-%d %H:%M:%S")
        diff = abs((entry_dt - target_dt).total_seconds())
        if (best is None) or (diff < best_diff):
            best = entry
            best_diff = diff
    return best

# ==================
# TEXT-TO-SPEECH WITH ESPEAK
# ==================

def speak(text):
    """Speak the given text aloud using espeak."""
    print("[TTS]", text)
    try:
        subprocess.run(["espeak", text], check=False)
    except FileNotFoundError:
        print("[!] espeak not found. Make sure it is installed: sudo apt install espeak")

# ==================
# MAIN LOGIC
# ==================

def build_weather_sentence(city, temp, humidity, desc, when_str):
    """Build a natural sentence for TTS."""
    if when_str == "now":
        return f"The weather in {city} is {desc}, with {temp:.1f} degrees and {humidity} percent humidity."
    else:
        return f"The weather in {city} {when_str} will be {desc}, with {temp:.1f} degrees and {humidity} percent humidity."
    
def main():	
    if API_KEY == "YOUR_API_KEY_HERE":
        print("[!] Please set your OpenWeatherMap API key in the script before running.")
        return
    
    print("=== Voice Weather Assistant ===")
    print("Say something like:")
    print(" - 'What's the weather in Daegu now?'")
    print(" - 'What's the weather in Seoul tomorrow morning?'")
    print(" - 'What will the weather be in Incheon on Friday?'")
    print(" - 'Tonight Seoul'")
    
    text = listen_once()
    if not text:
        speak("Sorry, I did not catch that.")
        return
    
    city = extract_city(text)
    if not city:
        speak("Sorry, I could not detect a city name.")
        return
    
    print("[INFO] Detected city:", city)
    
    now = datetime.now()
    target_date = interpret_day(text, now=now)
    target_hour = interpret_part_of_day(text)
    target_dt = datetime.combine(target_date, dtime(hour=target_hour))
    
    print("[INFO] Target datetime:", target_dt)
    
    today = now.date()
    is_future = target_date > today
    
    # Decide whether to use current weather or forecast
    use_current = (not is_future)
    
    if use_current:
        data = get_current_weather(city)
        if not data:
            speak("Sorry, I could not retrieve the current weather.")
            return
        main = data["main"]
        weather = data["weather"][0]
        temp = main["temp"]
        humidity = main["humidity"]
        desc = weather["description"]
        sentence = build_weather_sentence(city, temp, humidity, desc, "now")
        speak(sentence)
    else:
        data = get_forecast(city)
        if not data:
            speak("Sorry, I could not retrieve the weather forcast.")
            return
        entry = pick_best_forecast_entry(data, target_dt)
        if not entry:
            speak("Sorry, I could not find a suitable forecast time.")
            return
        main = entry["main"]
        weather = entry["weather"][0]
        temp = main["temp"]
        humidity = main["humidity"]
        desc = weather["description"]
        
        #Build a simple human-readable "when" string
        if target_date == today + timedelta(days=1):
            when_str = "tomorrow"
        elif target_date == today + timedelta(days=2):
            when_str = "the day after tomorrow"
        else:
            when_str = "on" + target_date.strftime("%A")  # e.g., "on Friday"
        
        sentence = build_weather_sentence(city, temp, humidity, desc, when_str)
        speak(sentence)

if __name__ == "__main__":
    main()