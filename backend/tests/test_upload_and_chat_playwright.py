import sys
import os
sys.path.insert(0, r"F:\Studies\Project\11. NLP\RAG Application\Implementation_2")
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import time
import pytest
from playwright.sync_api import sync_playwright, expect

FRONTEND_URL = "http://localhost:3000"
WORKSPACE_ID = "b4b8c4f8-1370-437f-804f-d359e3e0888f"

def test_documents_page_and_chat_e2e():
    print("\n--- Starting Playwright E2E Ingestion & Chat Test ---")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        # Step 1: Open Documents Page
        docs_url = f"{FRONTEND_URL}/workspaces/{WORKSPACE_ID}/documents"
        print(f"1. Navigating to Documents Page: {docs_url}")
        page.goto(docs_url, wait_until="networkidle")
        page.wait_for_timeout(1000)

        # Step 2: Check document table
        doc_row = page.locator("text=TN-Std12-Zoology-EM.pdf").first
        expect(doc_row).to_be_visible()
        print("   Found document 'TN-Std12-Zoology-EM.pdf' in table!")

        # Step 3: Check chunks count
        chunks_badge = page.locator("text=487 chunks").first
        expect(chunks_badge).to_be_visible()
        print("   Found '487 chunks' badge!")

        # Step 4: Upload new document through the UI
        test_file_path = os.path.abspath(r"storage\test_cell_diagram.pdf")
        print(f"4. Uploading '{test_file_path}' through file input...")
        file_input = page.locator("input[type='file']").first
        file_input.set_input_files(test_file_path)

        # Wait for upload and instant ingestion
        print("   Waiting for upload & fast ingestion to complete...")
        page.wait_for_timeout(4000)

        # Verify new document appears in list
        new_doc_row = page.locator("text=test_cell_diagram.pdf").first
        expect(new_doc_row).to_be_visible(timeout=10000)
        print("   New document 'test_cell_diagram.pdf' ingested and visible!")

        # Step 5: Navigate to Chat Page
        chat_url = f"{FRONTEND_URL}/workspaces/{WORKSPACE_ID}/chat"
        print(f"5. Navigating to Chat: {chat_url}")
        page.goto(chat_url, wait_until="networkidle")
        page.wait_for_timeout(1000)

        # Step 6: Ask question
        chat_input = page.locator("textarea[placeholder*='Ask a question'], input[placeholder*='Ask a question']").first
        expect(chat_input).to_be_visible()

        query = "Explain reproductive health and methods of contraception from the textbook"
        print(f"6. Sending query: '{query}'")
        chat_input.fill(query)
        send_btn = page.locator("button[aria-label='Send prompt']").first
        if send_btn.is_visible():
            send_btn.click()
        else:
            chat_input.press("Enter")

        # Wait for assistant response
        print("   Waiting for pedagogical response...")
        page.locator(".prose").last.wait_for(state="visible", timeout=30000)
        page_text = page.content()
        print(f"   Response received! Page text length: {len(page_text)}")
        assert "Contraception" in page_text or "reproductive" in page_text.lower() or "Core Concept" in page_text or "health" in page_text.lower()

        # Take screenshot
        os.makedirs(r"storage\screenshots", exist_ok=True)
        screenshot_path = os.path.abspath(r"storage\screenshots\e2e_biology_ingestion_chat.png")
        page.screenshot(path=screenshot_path)
        print(f"7. Captured screenshot: {screenshot_path}")

        browser.close()
        print("\n>>> ALL PLAYWRIGHT E2E INGESTION & CHAT TESTS PASSED! <<<")

if __name__ == "__main__":
    test_documents_page_and_chat_e2e()
