# Raspberry Pi Voice-Based Weather Assistant  
*A real-time voice-controlled weather system using Speech Recognition, NLP, and TTS*

This project is a **voice-driven weather assistant** built on **Raspberry Pi 5**.  
It listens to a user’s spoken query, extracts the **city** and **date/time target**, retrieves weather data from the **OpenWeatherMap API**, and responds using **text-to-speech**.

It demonstrates hands-on integration of:

- Speech Recognition (ASR)
- Lightweight Natural Language Processing (NLP)
- API data retrieval (JSON)
- Embedded system audio output (TTS)
- Real-time event-driven programming
- Raspberry Pi hardware/software ecosystem

---

## Demo Video
- Video link: https://youtube.com/shorts/rAMmzgMXIbo
---

## Project Structure

```text
voice_weather_assistant/
├── voice_weather_assistant.py     # Main program: ASR → NLP → Weather API → TTS
├── requirements.txt               # Python dependencies
└── README.md                      # Project documentation
```
## Features
- Voice-controlled interaction using Google Speech Recognition
- Rule-based NLP to interpret:
  - "today"
  - "tomorrow"
  - "day after tomorrow"
  -  weekdays ("Monday~Sunday")
  - "morning," "afternoon," "evening," "tonight"
- City extraction from voice queries
- Real-time weather (temperature, humidity, description)
- Weather forecast up to 5 days (3-hour intervals)
- Audio response using eSpeak TTS
- Clear error handling and fallback logic

## Supported Voice Query Formats
- "What's the weather in New York now?"
- "Weather in Seoul tomorrow morning."
- "Weather in Paris day after tomorrow." (no 'the' before 'day')
- "What will the weather be in Tokyo Friday night?" (no 'on' before 'Friday')
* The assistant uses lightweight rule-based parsing.
  Sentences not following certain rules will not be recognized, such as:
  - "I want to know Seoul's weather today."
  
    → If there is no 'in' right before a city name, only words in TIME_WORDS (Python set), apart from the city name, can be allowed in the sentence, for the city to be properly recognized.
  - "Is it cold in Tokyo?"

    → Full conversational sentences may not be fully recognized.

## Prerequisites
### Hardware Requirements
To run this project, you will need:

- Raspberry Pi 4 or 5 (recommended)
- USB microphone
- Bluetooth speaker (connected to Raspberry Pi)
- Stable internet connection (for API calls & Google STT)

### System Packages (must be installed before pip packages)
On Raspberry Pi OS:
```text
sudo apt update
sudo apt install portaudio19-dev flac espeak -y
```
- portaudio19-dev: Needed so PyAudio (installed via pip) can compile correctly
- flac: Required by SpeechRecognition for handling FLAC audio
- espeak: Text-to-Speech engine for audio response
 
**You also need a personal API key from OpenWeatherMap: https://openweathermap.org/**

## Install Python Dependencies
  ```text
  pip install -r requirements.txt
  ```

## How to Run
```text
python3 voice_weather_assistant.py
```
The assistant will:
1. Listen for your spoken query
2. Recognize your speech
3. Extract city + date/time
4. Fetch weather data via API
5. Respond using TTS

## How It Works (Architecture)
```text
Microphone → SpeechRecognition → NLP Parser → Weather API → Formatter → TTS (eSpeak)
```

## Weather Data
Uses OpenWeatherMap APIs:
- Current weather → https://api.openweathermap.org/data/2.5/weather
- 5-day forecast → https://api.openweathermap.org/data/2.5/forecast

## NLP Components
- City extraction
- Date/time interpretation
- Weekday → date offset conversion
- 3-hour forecast matching

## Future Improvements
- Offline speech recognition (Vosk)
- Better NLP using spaCy or regex
- Wake-word activation
- Multi-language support
- Add GUI via Flask
