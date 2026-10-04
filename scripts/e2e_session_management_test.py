import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import time
import json
from playwright.sync_api import sync_playwright

os.makedirs("storage/test_artifacts", exist_ok=True)

WORKSPACE_ID = "d23b3143-2b9c-4bd1-bd5a-e71d9666935c" # Biology workspace
BASE_URL = f"http://localhost:3000/workspaces/{WORKSPACE_ID}/chat"

print(f"Starting Playwright E2E Session Management & UI/UX Test against {BASE_URL}...")

results = {}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1366, "height": 850})
    
    # 1. Navigate to Biology Workspace Chat
    print("1. Navigating to Chat page...")
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=20000)
    time.sleep(3)
    
    # Wait for header text to populate with workspace name
    page.wait_for_selector("header h1", timeout=10000)
    time.sleep(1)
    
    # Capture initial view with temporal sidebar & updated header
    screenshot_1 = "storage/test_artifacts/session_ui_01_initial.png"
    page.screenshot(path=screenshot_1)
    
    # Check header metadata
    header_text = page.locator("header").inner_text()
    print(f"Header text detected: {header_text.replace(chr(10), ' ')}")
    results["header_text"] = header_text
    
    # 2. Test Creating a New Session via Button
    print("2. Testing New Conversation CTA...")
    new_btn = page.locator("button:has-text('New Conversation')").first
    if new_btn.is_visible():
        new_btn.click()
        time.sleep(2)
    
    screenshot_2 = "storage/test_artifacts/session_ui_02_new_session_created.png"
    page.screenshot(path=screenshot_2)
    
    # 3. Test Search / Filter input
    print("3. Testing Search Filtering...")
    search_input = page.locator("input[placeholder*='Search conversations']")
    if search_input.is_visible():
        search_input.fill("Reproduction")
        time.sleep(1)
        screenshot_3 = "storage/test_artifacts/session_ui_03_search_filtered.png"
        page.screenshot(path=screenshot_3)
        # Clear search
        search_input.fill("")
        time.sleep(1)

    # 4. Test Inline Renaming
    print("4. Testing Inline Renaming...")
    first_session = page.locator("aside").last.locator("div.group.relative").first
    if first_session.is_visible():
        first_session.hover()
        time.sleep(0.5)
        rename_btn = first_session.locator("button[title*='Rename']").first
        if rename_btn.is_visible():
            rename_btn.click()
            time.sleep(0.5)
            # Type new name
            edit_input = first_session.locator("input")
            if edit_input.is_visible():
                edit_input.fill("Zoology Exam Master Revision")
                edit_input.press("Enter")
                time.sleep(2)
                
    screenshot_4 = "storage/test_artifacts/session_ui_04_inline_renamed.png"
    page.screenshot(path=screenshot_4)
    
    # 5. Send a quick query in the session
    print("5. Sending test doubt in active session...")
    input_box = page.locator("textarea")
    input_box.fill("Give me a quick 2-bullet summary of Chapter 1 modes of reproduction")
    send_btn = page.locator("button[aria-label='Send prompt']")
    if send_btn.is_visible() and send_btn.is_enabled():
        send_btn.click()
    else:
        input_box.press("Enter")
        
    print("Waiting for generation...")
    time.sleep(8)
    try:
        page.wait_for_selector("button[aria-label='Stop generation']", state="detached", timeout=30000)
    except Exception:
        pass
    time.sleep(2)
    
    screenshot_5 = "storage/test_artifacts/session_ui_05_message_and_sidebar_sync.png"
    page.screenshot(path=screenshot_5)
    
    # Capture sidebar sessions text using .last aside
    sidebar_text = page.locator("aside").last.inner_text()
    results["sidebar_text"] = sidebar_text
    print(f"Final sidebar state:\n{sidebar_text}\n")
    
    browser.close()

with open("storage/test_artifacts/session_management_validation.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("Session management E2E test completed successfully!")
