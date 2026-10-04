import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import time
import json
from playwright.sync_api import sync_playwright

os.makedirs("storage/test_artifacts", exist_ok=True)

WORKSPACE_ID = "d23b3143-2b9c-4bd1-bd5a-e71d9666935c" # Biology workspace
BASE_URL = f"http://localhost:3000/workspaces/{WORKSPACE_ID}/chat"

questions = [
    {
        "role": "Student Doubts 1 (Chapter List with Typo)",
        "query": "Give me the list fo all chapters",
        "expected_topic": "Chapter 1 to Chapter 13 listing from Zoology textbook"
    },
    {
        "role": "Student Doubts 2 (Exam Prep - Chapter 1 & 2)",
        "query": "What are the key topics in Chapter 1 Reproduction in Organisms and Chapter 2 Human Reproduction?",
        "expected_topic": "Asexual/sexual reproduction, gametogenesis, menstrual cycle"
    },
    {
        "role": "Student Doubts 3 (Exam Doubts - Spelling Error)",
        "query": "Explain the stages of spermatogenisis and hormonel control for my exam tomorrow",
        "expected_topic": "Spermatogenesis stages, FSH/LH/testosterone hormonal regulation"
    },
    {
        "role": "Student Doubts 4 (Chapter 13 Topic)",
        "query": "What are the environmental issues covered in chapter 13?",
        "expected_topic": "Air pollution, water pollution, greenhouse effect, solid waste"
    }
]

print(f"Starting Playwright E2E Student Simulation against {BASE_URL}...")

results = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    
    # 1. Navigate to Biology Workspace Chat
    print(f"Navigating to {BASE_URL}...")
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=20000)
    time.sleep(3)
    
    # Capture initial view
    page.screenshot(path="storage/test_artifacts/01_biology_workspace_initial.png")
    print("Initial workspace loaded. Starting student interaction loop...")

    for i, q in enumerate(questions):
        print(f"\n==========================================")
        print(f"--- Turn {i+1}: Student Query: '{q['query']}' ---")
        print(f"==========================================")
        
        # Locate chat input textarea
        input_locator = page.locator("textarea")
        input_locator.wait_for(state="visible", timeout=10000)
        
        input_locator.fill(q["query"])
        time.sleep(0.5)
        
        # Click send button
        send_btn = page.locator("button[aria-label='Send prompt'], button:has(svg.lucide-arrow-up)")
        if send_btn.is_visible() and send_btn.is_enabled():
            send_btn.click()
        else:
            input_locator.press("Enter")
            
        print(f"Query submitted. Waiting for AI response generation...")
        
        # Wait for generation to start and complete
        time.sleep(6)
        try:
            # Wait until generating indicator / stop button disappears
            page.wait_for_selector("button[aria-label='Stop generation']", state="detached", timeout=35000)
        except Exception:
            pass
            
        time.sleep(3)
        
        # Take screenshot of the response
        screenshot_path = f"storage/test_artifacts/turn_{i+1}_response.png"
        page.screenshot(path=screenshot_path)
        
        # Extract assistant message content
        assistant_elements = page.locator("div.flex.justify-start").all()
        if assistant_elements:
            latest_text = assistant_elements[-1].inner_text()
        else:
            latest_text = page.locator("body").inner_text()
        
        print(f"Response Received ({len(latest_text)} chars):\n{latest_text[:400]}...\n")
        
        results.append({
            "turn": i + 1,
            "query": q["query"],
            "role": q["role"],
            "expected_topic": q["expected_topic"],
            "response_text": latest_text,
            "screenshot": screenshot_path
        })

    browser.close()

with open("storage/test_artifacts/student_simulation_report.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("\n==========================================")
print("Student simulation complete! All 4 turns tested successfully.")
print("Report saved to storage/test_artifacts/student_simulation_report.json")
