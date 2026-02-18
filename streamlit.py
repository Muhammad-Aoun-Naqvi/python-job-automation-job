import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ==========================================
# ⚙️ CONFIGURATION (EDIT THIS PART)
# ==========================================
URL = "https://realpython.github.io/fake-jobs/"
CSV_FILE = "my_python_jobs.csv"

# 🔒 SECURITY WARNING: Never share this file with your real password inside!
EMAIL_ADDRESS = "my.python.bot.2026@gmail.com"       # <--- Put your email here
EMAIL_PASSWORD = "rigl bbbk xqzp jybn"       # <--- Put your Google App Password here
RECEIVER_EMAIL ="my.python.bot.2026@gmail.com"      # Send to yourself

# ==========================================
# 📧 EMAIL FUNCTION
# ==========================================
def send_job_alert(new_jobs_list):
    print(f"📧 Sending email for {len(new_jobs_list)} new jobs...")
    
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = f"🔔 Alert: Found {len(new_jobs_list)} New Python Jobs!"

    # Format the email body
    body = "🚀 I found these new jobs for you:\n\n"
    for job in new_jobs_list:
        body += f"🔹 {job['Job Title']} at {job['Company']}\n"
        body += f"   📍 {job['Location']}\n"
        body += "-" * 20 + "\n"
    
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

# ==========================================
# 🧠 MAIN LOGIC (THE BRAIN)
# ==========================================

print("--- Starting Job Bot ---")

# 1. LOAD HISTORY (The "De-Duplicator")
old_ids = []
if os.path.exists(CSV_FILE):
    try:
        df_old = pd.read_csv(CSV_FILE)
        # Create unique IDs from existing data to compare later
        # ID format: "Title_Company" (e.g., "Python Dev_Systems")
        old_ids = (df_old["Job Title"] + "_" + df_old["Company"]).tolist()
        print(f"📂 Loaded history: {len(old_ids)} jobs already in database.")
    except Exception as e:
        print("⚠️ Found CSV but couldn't read it. Starting fresh.")

# 2. SCRAPE THE WEBSITE
print("🕷️  Scraping website...")
try:
    response = requests.get(URL)
    soup = BeautifulSoup(response.content, "html.parser")
    cards = soup.find_all("div", class_="card-content")
except Exception as e:
    print(f"❌ Critical Error: Could not connect to website. {e}")
    cards = []

# 3. FILTER & CHECK FOR NEW JOBS
new_jobs_found = []

for card in cards:
    # Extract Data
    title = card.find("h2", class_="title").text.strip()
    company = card.find("h3", class_="company").text.strip()
    location = card.find("p", class_="location").text.strip()
    
    # Create the Fingerprint ID
    job_id = title + "_" + company
    
    # LOGIC GATE 1: Is it a Python job?
    if "python" in title.lower():
        
        # LOGIC GATE 2: Is it a NEW job? (Not in old_ids)
        if job_id not in old_ids:
            print(f"🆕 Found NEW Job: {title}")
            
            # Add to our "New" list
            new_jobs_found.append({
                "Job Title": title,
                "Company": company,
                "Location": location
            })
            
            # Add to "Old" list so we don't pick it up again if there are duplicates on the page itself
            old_ids.append(job_id)

# 4. FINAL ACTIONS
if new_jobs_found:
    # A. Send the Email
    send_job_alert(new_jobs_found)
    
    # B. Save to CSV (Append Mode)
    # mode='a' means append (add to bottom), header=False (don't write column names again)
    df_new = pd.DataFrame(new_jobs_found)
    
    if os.path.exists(CSV_FILE):
        df_new.to_csv(CSV_FILE, mode='a', header=False, index=False)
    else:
        # If file doesn't exist, we write it with headers
        df_new.to_csv(CSV_FILE, index=False)
        
    print(f"💾 Saved {len(new_jobs_found)} new jobs to {CSV_FILE}")

else:
    print("😴 No new jobs found since last run.")