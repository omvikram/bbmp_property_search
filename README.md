# BBMP Property Finder

Browser helper for the XYZ property.

Known data:
- ePID: ?
- Flat: ?
- Ward: ?
- Owners: ?
- Old property ref: ?
- Khata ref: ?
- Survey No.: ?
- Certificate ref: ?

## Run

Python 3.10+:

    python -m venv .venv
    # Windows: .venv\Scripts\activate
    # macOS/Linux: source .venv/bin/activate
    pip install -r requirements.txt
    python -m playwright install chromium
    python main.py

The browser is deliberately visible. If CAPTCHA or OTP appears, you complete it
manually. The script does not bypass access controls.

Results are saved under `results/` and screenshots under `screenshots/`.

Official portals:
https://bbmpeaasthi.karnataka.gov.in/
https://bbmptax.karnataka.gov.in/
