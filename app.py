import streamlit as st
import pandas as pd
import speech_recognition as sr
import pyttsx3
import re
from deep_translator import GoogleTranslator

# --------------------------
# Title
# --------------------------
st.title("🌍 Multilingual Civic Services Copilot")

# --------------------------
# Load Data
# --------------------------
data = pd.read_csv("schemes.csv")

# --------------------------
# Language Selection 🌍 (for display only)
# --------------------------
language = st.selectbox(
    "🌍 Select Language",
    ["English", "Hindi", "Kannada", "Tamil", "Telugu"]
)

lang_code = {
    "English": "en",
    "Hindi": "hi",
    "Kannada": "kn",
    "Tamil": "ta",
    "Telugu": "te"
}

# --------------------------
# State Selection 🗺️
# --------------------------
states = data["State"].unique()
selected_state = st.selectbox("🗺️ Select State", states)
filtered_data = data[data["State"] == selected_state]

# --------------------------
# Eligibility Checker 📋
# --------------------------
st.subheader("📋 Eligibility Checker")

age = st.number_input("Enter Age", min_value=1, max_value=100)
income = st.number_input("Enter Annual Income")

if st.button("Check Eligibility"):
    if age < 25 and income < 300000:
        st.success("✅ Eligible for Student Schemes")
    elif income < 200000:
        st.success("✅ Eligible for Support Schemes")
    else:
        st.warning("⚠️ Limited eligibility")

# --------------------------
# Translation 🌍 (display only)
# --------------------------
def translate_text(text, dest):
    try:
        if dest == "en":
            return text
        return GoogleTranslator(source='auto', target=dest).translate(text)
    except:
        return text

# --------------------------
# PII Protection 🔒
# --------------------------
def remove_pii(text):
    text = re.sub(r'\d{12}', '[Aadhaar Hidden]', text)
    text = re.sub(r'\d{10}', '[Phone Hidden]', text)
    return text

# --------------------------
# Voice Input 🎤
# --------------------------
def speech_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening...")
        audio = r.listen(source)
    try:
        return r.recognize_google(audio)
    except:
        return "Could not understand"

# --------------------------
# Voice Output 🔊 (ENGLISH ONLY)
# --------------------------
def speak_text(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1.0)
    engine.say(text)
    engine.runAndWait()

# --------------------------
# MULTI SEARCH 🔍
# --------------------------
def search_schemes(query):
    query = query.lower()
    results = []

    for _, row in filtered_data.iterrows():
        if any(word in row["Scheme"].lower() for word in query.split()) \
           or query in row["Benefits"].lower() \
           or query in row["Eligibility"].lower():
            results.append(row)

    return results

# --------------------------
# Input
# --------------------------
prompt = st.text_input("💬 Ask about Government Scheme")

if st.button("🎤 Speak"):
    user_input = speech_to_text()
    st.write("You said:", user_input)
else:
    user_input = prompt

# --------------------------
# MAIN LOGIC
# --------------------------
if user_input:

    clean_input = remove_pii(user_input)
    english_query = translate_text(clean_input, "en")

    results = search_schemes(english_query)

    if results:

        st.subheader("📋 Matching Schemes")

        speech_output = ""

        for result in results[:3]:  # limit for demo

            # Display (translated)
            scheme_name = translate_text(result["Scheme"], lang_code[language])
            eligibility = translate_text(result["Eligibility"], lang_code[language])
            benefits = translate_text(result["Benefits"], lang_code[language])
            state = translate_text(result["State"], lang_code[language])

            st.markdown(f"## 📌 {scheme_name}")

            st.write("### 🧾 Eligibility")
            st.write(eligibility)

            docs = result["Documents"].split(";")
            st.write("### 📄 Required Documents")

            for i, doc in enumerate(docs, start=1):
                translated_doc = translate_text(doc, lang_code[language])
                st.write(f"📌 Step {i}: {translated_doc}")

            st.write("### 🎁 Benefits")
            st.write(benefits)

            st.write("### 📍 State")
            st.write(state)

            st.write("---")

            # --------------------------
            # SPEECH (ENGLISH ONLY FULL OUTPUT)
            # --------------------------
            speech_output += f"Scheme {result['Scheme']}. "
            speech_output += f"Eligibility: {result['Eligibility']}. "

            speech_output += "Required documents are: "
            for doc in docs:
                speech_output += f"{doc}, "

            speech_output += f"Benefits: {result['Benefits']}. "
            speech_output += "Next scheme. "

        # 🔊 Speak full output
        speak_text(speech_output)

    else:
        st.error("No matching schemes found")