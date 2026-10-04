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

def test_visual_rag_figure_card_and_lightbox():
    print("\n--- Starting Playwright Visual RAG E2E Test ---")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        # Step 1: Open chat page for Visual RAG test lab workspace
        chat_url = f"{FRONTEND_URL}/workspaces/{WORKSPACE_ID}/chat"
        print(f"1. Navigating to: {chat_url}")
        page.goto(chat_url, wait_until="networkidle")
        page.wait_for_timeout(1000)

        # Step 2: Send query requesting cell structure diagram
        chat_input = page.locator("textarea[placeholder*='Ask a question'], input[placeholder*='Ask a question']").first
        expect(chat_input).to_be_visible()
        
        query = "Show and explain the human reproductive system diagram"
        print(f"2. Typing query: '{query}'")
        chat_input.fill(query)
        send_btn = page.locator("button[aria-label='Send prompt']").first
        if send_btn.is_visible():
            send_btn.click()
        else:
            chat_input.press("Enter")

        # Step 3: Wait for assistant response with figure gallery
        print("3. Waiting for AI response and figure rendering...")
        # Give LLM up to 45 seconds to synthesize and return
        figure_section = page.locator("text=Referenced Figures & Diagrams").first
        figure_section.wait_for(state="visible", timeout=45000)
        print("   Found 'Referenced Figures & Diagrams' header!")

        # Step 4: Verify FigureCard rendering
        figure_cards = page.locator("[role='button'][aria-label*='View figure']")
        card_count = figure_cards.count()
        print(f"4. Rendered FigureCards count: {card_count}")
        assert card_count > 0, "Expected at least 1 FigureCard to be rendered in chat response"

        first_card = figure_cards.first
        expect(first_card).to_be_visible()

        # Check badge and page reference
        badge_text = first_card.locator("[data-testid='figure-type-badge']").text_content() or ""
        print(f"   Badge: {badge_text}")
        assert "Diagram" in badge_text or "Figure" in badge_text

        # Verify image inside card has loaded
        img = first_card.locator("img").first
        expect(img).to_be_visible()
        is_natural_width = page.evaluate("(img) => img.naturalWidth > 0", img.element_handle())
        print(f"   Thumbnail image naturalWidth > 0: {is_natural_width}")
        assert is_natural_width, "Figure thumbnail failed to load image content"

        # Step 5: Click card to trigger Lightbox Modal
        print("5. Clicking FigureCard to open Lightbox Modal...")
        first_card.click()
        page.wait_for_timeout(600)

        # Verify Lightbox Modal opened
        lightbox = page.locator("div.fixed.inset-0").first
        expect(lightbox).to_be_visible()
        print("   Lightbox overlay is visible!")

        # Verify lightbox image and caption
        lightbox_img = lightbox.locator("img").first
        expect(lightbox_img).to_be_visible()
        lightbox_img_loaded = page.evaluate("(img) => img.naturalWidth > 0", lightbox_img.element_handle())
        print(f"   Lightbox full-res image loaded: {lightbox_img_loaded}")
        assert lightbox_img_loaded, "Lightbox image failed to render"

        # Step 6: Close Lightbox
        close_btn = lightbox.locator("button[aria-label='Close lightbox'], button:has-text('✕'), button").first
        print("6. Closing lightbox modal...")
        close_btn.click()
        page.wait_for_timeout(400)
        expect(lightbox).not_to_be_visible()
        print("   Lightbox closed successfully!")

        # Take screenshot for QA artifact
        os.makedirs(r"storage\screenshots", exist_ok=True)
        screenshot_path = os.path.abspath(r"storage\screenshots\visual_rag_playwright_success.png")
        page.screenshot(path=screenshot_path)
        print(f"7. Captured full verification screenshot: {screenshot_path}")

        browser.close()
        print("\n>>> PLAYWRIGHT E2E TESTS PASSED WITH 100% SUCCESS! <<<")

if __name__ == "__main__":
    test_visual_rag_figure_card_and_lightbox()
