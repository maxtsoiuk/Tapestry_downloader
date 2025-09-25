from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import urllib.request
from urllib.parse import urlparse, unquote
import re
from datetime import datetime

# === SETTINGS ===
EMAIL = "Email address"     # Your Tapestry email
PASSWORD = "Password"           # Your Tapestry password
BASE_URL = "https://tapestryjournal.com/s/wimbledon-high-school"
DOWNLOAD_FOLDER = r"C:\Users\xxx\"  # Folder to store downloads

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# === SANITIZE FILENAME ===
def sanitize_filename(url):
    path = urlparse(url).path  # removes query string
    filename = os.path.basename(path)
    filename = unquote(filename)
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)  # remove unsafe chars
    return filename

# === START DRIVER WITH AUTO ChromeDriver ===
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=service, options=options)

# === LOGIN ===
driver.get(BASE_URL)
time.sleep(2)
driver.find_element(By.NAME, "email").send_keys(EMAIL)
driver.find_element(By.NAME, "password").send_keys(PASSWORD)
driver.find_element(By.XPATH, "//button[contains(text(),'Log in')]").click()
time.sleep(5)

# === OPEN OBSERVATIONS PAGE ===
driver.get(BASE_URL + "/observations")
time.sleep(5)

# === SCROLL TO LOAD ALL OBSERVATIONS ===
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

time.sleep(2)

# === COLLECT ALL OBSERVATION LINKS ===
obs_links = []
for elem in driver.find_elements(By.XPATH, "//a[contains(@href,'/observation/')]"):
    link = elem.get_attribute("href")
    if link and link not in obs_links:
        obs_links.append(link)

print(f"Found {len(obs_links)} observations.")

# === VISIT EACH OBSERVATION AND DOWNLOAD MEDIA ===
for idx, obs_url in enumerate(obs_links, start=1):
    print(f"[{idx}/{len(obs_links)}] Opening {obs_url}")
    driver.get(obs_url)
    time.sleep(3)

    # Get observation title
    try:
        obs_title = driver.find_element(By.XPATH, "//h1").text.strip()
        obs_title = sanitize_filename(obs_title)
    except Exception:
        obs_title = f"observation_{idx}"

    # === ROBUST DATE EXTRACTION ===
    obs_date = "unknown_date"
    try:
        metadata_paragraphs = driver.find_elements(By.CSS_SELECTOR, "div.obs-metadata p")
        for p in metadata_paragraphs:
            text = p.text.strip()
            if "Authored by" in text and "added" in text:
                date_match = re.search(r"added\s+(\d{1,2}\s+\w+\s+\d{4})", text)
                if date_match:
                    obs_date_raw = date_match.group(1)
                    obs_date = datetime.strptime(obs_date_raw, "%d %b %Y").strftime("%Y-%m-%d")
                    break
    except Exception as e:
        print(f"Date extraction error: {e}")

    # Prefix for filenames
    prefix = f"{obs_date}_{obs_title}"

    # Download images
    images = driver.find_elements(By.XPATH, "//img[contains(@class,'obs-media')]")
    for img_idx, img in enumerate(images, start=1):
        src = img.get_attribute("src")
        if src:
            suffix = f"_{img_idx}" if len(images) > 1 else ""
            filename = f"{prefix}{suffix}{os.path.splitext(sanitize_filename(src))[1]}"
            filepath = os.path.join(DOWNLOAD_FOLDER, filename)
            print(f"Downloading image {src} → {filepath}")
            try:
                urllib.request.urlretrieve(src, filepath)
            except Exception as e:
                print(f"Failed to download image {src}: {e}")

    # Download videos
    videos = driver.find_elements(By.XPATH, "//video/source")
    for vid_idx, vid in enumerate(videos, start=1):
        src = vid.get_attribute("src")
        if src:
            suffix = f"_{vid_idx}" if len(videos) > 1 else ""
            filename = f"{prefix}{suffix}{os.path.splitext(sanitize_filename(src))[1]}"
            filepath = os.path.join(DOWNLOAD_FOLDER, filename)
            print(f"Downloading video {src} → {filepath}")
            try:
                urllib.request.urlretrieve(src, filepath)
            except Exception as e:
                print(f"Failed to download video {src}: {e}")

driver.quit()
print("All done!")
