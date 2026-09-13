import asyncio, json, re
from pathlib import Path
from playwright.async_api import async_playwright

EAASthi = "https://bbmpeaasthi.karnataka.gov.in/CitzLogin.aspx"
TAX = "https://bbmptax.karnataka.gov.in/"

PROPERTY = {
    "epid": "?",
    "flat": "?",
    "ward": "?",
    "owners": ["?", "?"],
    "old_property_ref": "?",
    "khata_ref": "?",
    "survey_no": "?",
    "certificate_ref": "?",
}

OUT, SHOTS = Path("results"), Path("screenshots")
OUT.mkdir(exist_ok=True); SHOTS.mkdir(exist_ok=True)

async def capture(page, name):
    await page.screenshot(path=str(SHOTS / f"{name}.png"), full_page=True)
    text = await page.locator("body").inner_text()
    (OUT / f"{name}.txt").write_text(text[:30000], encoding="utf-8")
    print(f"Saved {name}")

async def pause(reason):
    print("\n" + "="*70)
    print("HUMAN ACTION REQUIRED")
    print(reason)
    print("Complete the CAPTCHA/OTP/manual navigation in the visible browser,")
    print("then press ENTER here.")
    print("="*70)
    await asyncio.to_thread(input)

async def click_text(page, text):
    loc = page.get_by_text(text, exact=False)
    for i in range(await loc.count()):
        try:
            if await loc.nth(i).is_visible():
                await loc.nth(i).click()
                await page.wait_for_timeout(1500)
                return True
        except Exception:
            pass
    return False

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page(viewport={"width":1440,"height":1000}, locale="en-IN")

        # 1. e-Aasthi
        print("Opening e-Aasthi...")
        await page.goto(EAASthi, wait_until="domcontentloaded", timeout=60000)
        await capture(page, "01_eaasthi_home")

        clicked = await click_text(page, "Search your eKhata with SAS Property Tax")
        if not clicked:
            for label in ["Search your eKhata", "Search eKhata", "Property Search", "ಸ್ವತ್ತುಗಳನ್ನು ಹುಡುಕು"]:
                if await click_text(page, label):
                    clicked = True; break

        if not clicked:
            await pause("Open the public e-Aasthi property/eKhata search page.")

        await capture(page, "02_eaasthi_search")

        # Find an ePID/SAS/property-like visible input.
        inputs = page.locator("input")
        target = None
        for i in range(await inputs.count()):
            el = inputs.nth(i)
            try:
                if not await el.is_visible(): continue
                blob = " ".join(str(await el.get_attribute(x) or "") for x in
                                ["name","id","placeholder"]).lower()
                typ = await el.get_attribute("type")
                if typ in ["submit","button","hidden"]: continue
                if any(k in blob for k in ["epid","sas","property"]):
                    target = el; break
            except Exception: pass

        if target:
            await target.fill(PROPERTY["epid"])
            for label in ["Search","SEARCH","View","Submit"]:
                b = page.get_by_role("button", name=re.compile(label, re.I))
                if await b.count():
                    try:
                        await b.first.click(); break
                    except Exception: pass
        else:
            await pause(f"Enter ePID {PROPERTY['epid']} in the search form and submit.")

        await page.wait_for_timeout(2000)
        await capture(page, "03_eaasthi_epid_result")

        # 2. BBMP property tax portal
        print("Opening Property Tax portal...")
        await page.goto(TAX, wait_until="domcontentloaded", timeout=60000)
        await capture(page, "04_tax_home")
        await pause(
            "For the tax-portal diagnostic, enter the known ePID 4400376209 "
            "and an owner fragment such as VIK if the fields are visible. "
            "Do not try to bypass any CAPTCHA."
        )
        await capture(page, "05_tax_result")

        (OUT/"SUMMARY.json").write_text(json.dumps({
            "property": PROPERTY,
            "next_step": "Inspect 03_eaasthi_epid_result.txt/png for SAS Base Application No. or Old Property No."
        }, indent=2), encoding="utf-8")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
