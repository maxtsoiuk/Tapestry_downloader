# Tapestry Downloader

This script downloads all photos and videos from a Tapestry observation journal.

## Requirements

- Python 3.9+
- Google Chrome
- pip packages: selenium, webdriver-manager

## Installation

1. Clone repository:
   ```bash
   git clone https://github.com/maxtsoiuk/tapestry-downloader.git
   cd tapestry-downloader
2. Install dependencies:
   ```bash
   pip install -r requirements.txt

## Usage

Edit Tapestry.py and set:

EMAIL

PASSWORD

BASE_URL

DOWNLOAD_FOLDER

Run the script:

```bash
python Tapestry.py

## Notes

The script uses Selenium and automatically downloads the correct ChromeDriver version.

The downloaded media files will be saved in the folder specified in DOWNLOAD_FOLDER.
