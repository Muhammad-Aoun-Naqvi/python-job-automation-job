import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# 1. Load Secrets
load_dotenv(override=True)

EMAIL_ADDRESS = os.getenv("BOT_EMAIL")
EMAIL_PASSWORD = os.getenv("BOT_PASSWORD")

st.set_page_config(page_title="Job Hunter Bot", page_icon="🤖")


# --- FUNCTIONS ---
def scrape_jobs(keyword):
    url = "https://realpython.github.io/fake-jobs/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    results = []
    
    for card in soup.find_all("div", class_="card-content"):
        title = card.find("h2", class_="title").text.strip()
        company = card.find("h3", class_="company").text.strip()
        location = card.find("p", class_="location").text.strip()
        link = card.find("a", string="Apply")["href"]
        
        if keyword.lower() in title.lower():
            results.append({
                "Title": title, 
                "Company": company, 
                "Location": location,
                "Link": link
            })
    return results

def send_email(to_email, job_data):
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        st.error("❌ Email credentials not found in .env file!")
        return

    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = f"🔥 New {len(job_data)} Jobs Found!"

    body = f"Here are the top jobs I found for you:\n\n"
    for job in job_data:
        body += f"{job['Title']} at {job['Company']} ({job['Location']})\nLink: {job['Link']}\n\n"

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        st.success(f"✅ Email sent successfully to {to_email}!")
    except Exception as e:
        st.error(f"❌ Email Failed: {e}")

# --- MAIN APP LOGIC ---
st.title("🤖 AI Job Hunter")
st.markdown("---")

st.sidebar.header("⚙️ Configuration")
user_keyword = st.sidebar.text_input("Job Keyword", "Python")
user_email = st.sidebar.text_input("Send Alerts To:", EMAIL_ADDRESS)

# 2. INITIALIZE SESSION STATE (The Memory)
if 'found_jobs' not in st.session_state:
    st.session_state['found_jobs'] = []

# 3. BUTTON 1: SCRAPE
if st.button("Start Scraping"):
    with st.spinner("🕷️ Crawling the web..."):
        # Save results to session_state, NOT a local variable
        st.session_state['found_jobs'] = scrape_jobs(user_keyword)

# 4. DISPLAY RESULTS (Always show if data exists in memory)
if st.session_state['found_jobs']:
    st.success(f"Found {len(st.session_state['found_jobs'])} jobs for '{user_keyword}'")
    
    # Show Table
    df = pd.DataFrame(st.session_state['found_jobs'])
    st.dataframe(df)
    
    # 5. BUTTON 2: EMAIL (Now it works because data persists!)
    if st.button("📧 Email Me These Jobs"):
        send_email(user_email, st.session_state['found_jobs'])