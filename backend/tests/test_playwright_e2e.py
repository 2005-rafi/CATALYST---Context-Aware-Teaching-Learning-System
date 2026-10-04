import re
import pytest
import time
from playwright.sync_api import sync_playwright, expect

FRONTEND_URL = "http://localhost:3000"

def test_frontend_loads_and_theme_toggle():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(FRONTEND_URL, wait_until="networkidle")
        
        # Verify Workspaces heading
        expect(page.get_by_role("heading", name="Workspaces")).to_be_visible()
        
        # Verify theme toggle button
        theme_btn = page.locator("button:has-text('Theme'), button:has-text('Light'), button:has-text('Dark')").first
        if theme_btn.is_visible():
            theme_btn.click()
            page.wait_for_timeout(300)
            theme_btn.click()
            
        browser.close()

def test_mode_selector_and_simple_mode_chat():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(FRONTEND_URL, wait_until="networkidle")
        
        # Navigate to Biology workspace
        bio_heading = page.get_by_role("heading", name=re.compile(r"Biology")).first
        expect(bio_heading).to_be_visible()
        bio_heading.click()
        
        page.wait_for_url("**/workspaces/**/chat", timeout=8000)
        
        # Verify mode buttons exist: Simple, Medium, Expert
        simple_btn = page.get_by_role("button", name="Simple")
        medium_btn = page.get_by_role("button", name="Medium")
        expert_btn = page.get_by_role("button", name="Expert")
        
        expect(simple_btn).to_be_visible()
        expect(medium_btn).to_be_visible()
        expect(expert_btn).to_be_visible()
        
        # 1. Click Simple mode (previously caused 422 error!)
        simple_btn.click()
        page.wait_for_timeout(500)
        
        # Type and send query in Simple mode with typos
        chat_input = page.locator("textarea[placeholder*='Ask a question'], input[placeholder*='Ask a question']").first
        expect(chat_input).to_be_visible()
        
        test_query = "Explain mitosis and cell divisoin briefly"
        chat_input.fill(test_query)
        chat_input.press("Enter")
        
        # Wait for response message to appear (no 422 error popup)
        page.wait_for_timeout(7000)
        
        page_text = page.content()
        assert "String should match pattern" not in page_text
        assert "422" not in page_text
        
        browser.close()

def test_in_domain_spelling_mistakes_retrieval_and_answer():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(FRONTEND_URL, wait_until="networkidle")
        
        # Open Biology workspace
        page.get_by_role("heading", name=re.compile(r"Biology")).first.click()
        page.wait_for_url("**/workspaces/**/chat", timeout=8000)
        
        # Select Medium mode
        page.get_by_role("button", name="Medium").click()
        page.wait_for_timeout(500)
        
        chat_input = page.locator("textarea[placeholder*='Ask a question'], input[placeholder*='Ask a question']").first
        expect(chat_input).to_be_visible()
        
        # In-domain query with severe typos: 'preventaion', 'pollutoin'
        test_query = "List all environmental issues and the preventaion to them?"
        chat_input.fill(test_query)
        send_btn = page.locator("button[aria-label='Send prompt']").first
        if send_btn.is_visible():
            send_btn.click()
        else:
            chat_input.press("Enter")
        
        # Wait for pedagogical response
        page.locator(".prose").last.wait_for(state="visible", timeout=30000)
        
        # Verify answer rendered with pedagogical structure or pollution keywords
        page_text = page.content()
        assert "Pollution" in page_text or "Environmental" in page_text or "Core Concept" in page_text or "oil spills" in page_text.lower()
        
        browser.close()

def test_out_of_domain_physics_query_handling():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(FRONTEND_URL, wait_until="networkidle")
        
        # Open Biology workspace
        page.get_by_role("heading", name=re.compile(r"Biology")).first.click()
        page.wait_for_url("**/workspaces/**/chat", timeout=8000)
        
        # Select Medium mode
        page.get_by_role("button", name="Medium").click()
        page.wait_for_timeout(500)
        
        chat_input = page.locator("textarea[placeholder*='Ask a question'], input[placeholder*='Ask a question']").first
        expect(chat_input).to_be_visible()
        
        # Out-of-domain Physics query with typo ('motin' -> motion, 'Newtn' -> Newton)
        physics_query = "What is Newtn second law of motin?"
        chat_input.fill(physics_query)
        send_btn = page.locator("button[aria-label='Send prompt']").first
        if send_btn.is_visible():
            send_btn.click()
        else:
            chat_input.press("Enter")
        
        # Wait for model generated physics explanation without crashing
        page.locator(".prose").last.wait_for(state="visible", timeout=30000)
        
        page_text = page.content()
        assert "Newton" in page_text or "Force" in page_text or "acceleration" in page_text or "motion" in page_text
        assert "String should match pattern" not in page_text
        assert "Internal Server Error" not in page_text
        
        browser.close()
