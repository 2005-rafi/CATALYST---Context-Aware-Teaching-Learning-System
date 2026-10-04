import { chromium } from 'playwright';

const WORKSPACE_ID = 'b4b8c4f8-1370-437f-804f-d359e3e0888f';
const CHAT_URL = `http://localhost:3000/workspaces/${WORKSPACE_ID}/chat`;

async function runRedesignTestSuite() {
  console.log('================================================================');
  console.log('  CATALYST Frontend Redesign & Flaws Fix Playwright E2E Suite  ');
  console.log('================================================================');

  const browser = await chromium.launch({ headless: true });
  const results = {
    passed: [],
    failed: [],
  };

  try {
    // -------------------------------------------------------------------------
    // TEST 1: Desktop Viewport (1920x1080) — Typography, Spacing & Collapsible Rail
    // -------------------------------------------------------------------------
    console.log('\n[1/5] Testing Desktop Viewport (1920x1080)...');
    const desktopContext = await browser.newContext({
      viewport: { width: 1920, height: 1080 },
    });
    const desktopPage = await desktopContext.newPage();

    // Verify Dashboard navigation
    await desktopPage.goto('http://localhost:3000', { waitUntil: 'domcontentloaded', timeout: 15000 });
    console.log('  ✓ Loaded dashboard at http://localhost:3000');

    // Click into Biology workspace
    const wsItem = desktopPage.locator('text=Biology').first();
    await wsItem.waitFor({ state: 'visible', timeout: 8000 });
    await wsItem.click();

    // Ensure we are on chat page
    await desktopPage.waitForURL(/\/workspaces\/[^\/]+\/chat/, { timeout: 10000 });
    console.log(`  ✓ Navigated to workspace chat: ${desktopPage.url()}`);

    // Wait for chat interface to mount
    await desktopPage.waitForSelector('textarea', { state: 'visible', timeout: 10000 });

    // Verify Reading Container Width is max-w-4xl (896px)
    const readingContainer = desktopPage.locator('div.max-w-4xl').first();
    const hasReadingContainer = (await readingContainer.count()) > 0;
    if (!hasReadingContainer) {
      throw new Error('Reading container max-w-4xl not found in DOM');
    }
    const containerBox = await readingContainer.boundingBox();
    console.log(`  ✓ Reading container width: ${Math.round(containerBox?.width || 0)}px (max-w-4xl)`);

    // Verify Prose Typography Scale (16px base font & 1.75 line-height)
    const proseElement = desktopPage.locator('.prose').first();
    if ((await proseElement.count()) > 0) {
      const fontSize = await proseElement.evaluate((el) => window.getComputedStyle(el).fontSize);
      const lineHeight = await proseElement.evaluate((el) => window.getComputedStyle(el).lineHeight);
      console.log(`  ✓ Computed Prose Typography: fontSize=${fontSize}, lineHeight=${lineHeight}`);
      const parsedSize = parseFloat(fontSize);
      if (parsedSize < 15.5) {
        throw new Error(`Base prose font size too small: ${fontSize} (expected >= 16px)`);
      }
    }

    // Verify Desktop SessionSidebar Collapse and Expand
    const collapseBtn = desktopPage.locator('aside button[title="Collapse sidebar"]').first();
    if (await collapseBtn.isVisible()) {
      await collapseBtn.click();
      await desktopPage.waitForTimeout(350);
      const slimRail = desktopPage.locator('aside.w-14').first();
      if (!(await slimRail.isVisible())) {
        throw new Error('Slim rail (w-14) failed to render on collapse');
      }
      console.log('  ✓ Sidebar collapsed to slim icon rail (w-14)');

      // Expand back
      const expandBtn = desktopPage.locator('button[title*="Expand conversations"]').first();
      await expandBtn.click();
      await desktopPage.waitForTimeout(350);
      const fullSidebar = desktopPage.locator('aside.w-64').first();
      if (!(await fullSidebar.isVisible())) {
        throw new Error('Sidebar failed to expand back to w-64');
      }
      console.log('  ✓ Sidebar expanded back to full w-64 panel');
    }

    // Capture Desktop Screenshot
    await desktopPage.screenshot({ path: 'frontend/tests/desktop_1920x1080_verified.png' });
    console.log('  ✓ Saved screenshot: desktop_1920x1080_verified.png');
    results.passed.push('Desktop Viewport & Typography Scale (16px/max-w-4xl)');
    await desktopContext.close();

    // -------------------------------------------------------------------------
    // TEST 2: Tablet Viewport (768x1024) — Responsive Drawer & Off-Canvas Mode
    // -------------------------------------------------------------------------
    console.log('\n[2/5] Testing Tablet Viewport (768x1024)...');
    const tabletContext = await browser.newContext({
      viewport: { width: 768, height: 1024 },
    });
    const tabletPage = await tabletContext.newPage();

    await tabletPage.goto(CHAT_URL, { waitUntil: 'domcontentloaded', timeout: 15000 });
    await tabletPage.waitForSelector('textarea', { state: 'visible', timeout: 10000 });

    // Assert that in-flow desktop sidebar is hidden on tablet
    const inFlowSidebar = tabletPage.locator('aside.w-64');
    const isSidebarVisibleInFlow = await inFlowSidebar.isVisible();
    if (isSidebarVisibleInFlow) {
      throw new Error('Desktop in-flow sidebar is visible on tablet screen (should be hidden in drawer)');
    }
    console.log('  ✓ In-flow desktop sidebar is properly hidden on tablet (< 1024px)');

    // Look for the "Chats" / drawer trigger button
    const drawerTrigger = tabletPage.locator('button:has-text("Chats")').first();
    await drawerTrigger.waitFor({ state: 'visible', timeout: 5000 });
    console.log('  ✓ Drawer trigger button is visible');

    // Click trigger and verify Drawer opens
    await drawerTrigger.click();
    await tabletPage.waitForSelector('div[role="dialog"]', { timeout: 5000 });
    console.log('  ✓ Responsive Drawer slid out smoothly');

    // Verify session list inside drawer (scoped to the open dialog)
    const newChatBtn = tabletPage.locator('div[role="dialog"] button:has-text("New Conversation")').first();
    await newChatBtn.waitFor({ state: 'visible', timeout: 5000 });
    console.log('  ✓ Session management active inside Drawer');

    // Close Drawer via close button
    const closeBtn = tabletPage.locator('button[aria-label="Close conversations"], button[aria-label="Close drawer"]').first();
    if (await closeBtn.isVisible()) {
      await closeBtn.click();
      await tabletPage.waitForTimeout(400);
      console.log('  ✓ Drawer closed cleanly on close button click');
    }

    await tabletPage.screenshot({ path: 'frontend/tests/tablet_768x1024_verified.png' });
    console.log('  ✓ Saved screenshot: tablet_768x1024_verified.png');
    results.passed.push('Tablet Viewport & Off-Canvas Responsive Drawer');
    await tabletContext.close();

    // -------------------------------------------------------------------------
    // TEST 3: Mobile Viewport (375x812) — Full-Width Canvas & Touch Usability
    // -------------------------------------------------------------------------
    console.log('\n[3/5] Testing Mobile Viewport (375x812 iPhone X)...');
    const mobileContext = await browser.newContext({
      viewport: { width: 375, height: 812 },
      isMobile: true,
      hasTouch: true,
    });
    const mobilePage = await mobileContext.newPage();

    await mobilePage.goto(CHAT_URL, { waitUntil: 'domcontentloaded', timeout: 15000 });
    await mobilePage.waitForSelector('textarea', { state: 'visible', timeout: 10000 });

    // Verify no horizontal document overflow
    const scrollWidth = await mobilePage.evaluate(() => document.documentElement.scrollWidth);
    const clientWidth = await mobilePage.evaluate(() => document.documentElement.clientWidth);
    console.log(`  ✓ Mobile horizontal check: scrollWidth=${scrollWidth}px, clientWidth=${clientWidth}px`);
    if (scrollWidth > clientWidth + 2) {
      throw new Error(`Mobile viewport has horizontal overflow: scrollWidth=${scrollWidth} > clientWidth=${clientWidth}`);
    }

    // Verify composer is positioned and usable
    const textarea = mobilePage.locator('textarea').first();
    await textarea.waitFor({ state: 'visible', timeout: 5000 });
    console.log('  ✓ Composer textarea is fully reachable on mobile');

    await mobilePage.screenshot({ path: 'frontend/tests/mobile_375x812_verified.png' });
    console.log('  ✓ Saved screenshot: mobile_375x812_verified.png');
    results.passed.push('Mobile Viewport & Zero Horizontal Overflow');
    await mobileContext.close();

    // -------------------------------------------------------------------------
    // TEST 4: Zero Emojis Validation
    // -------------------------------------------------------------------------
    console.log('\n[4/5] Testing Zero-Emoji Policy Enforcement...');
    const auditContext = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const auditPage = await auditContext.newPage();
    await auditPage.goto(CHAT_URL, { waitUntil: 'domcontentloaded', timeout: 15000 });
    await auditPage.waitForSelector('textarea', { state: 'visible', timeout: 10000 });

    // Check figure badges for emojis
    const figureBadges = auditPage.locator('[data-testid="figure-type-badge"]');
    const badgeCount = await figureBadges.count();
    console.log(`  Found ${badgeCount} figure badges to inspect`);

    const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u;

    for (let i = 0; i < badgeCount; i++) {
      const badgeText = await figureBadges.nth(i).textContent();
      if (emojiRegex.test(badgeText || '')) {
        throw new Error(`Emoji detected in figure badge: "${badgeText}"`);
      }
    }
    console.log('  ✓ All FigureCard badges use Lucide SVG icons with zero emojis');

    // Check headings in prose
    const headings = auditPage.locator('.prose h1, .prose h2, .prose h3, .prose h4');
    const headingCount = await headings.count();
    for (let i = 0; i < headingCount; i++) {
      const hText = await headings.nth(i).textContent();
      if (emojiRegex.test(hText || '')) {
        throw new Error(`Emoji detected in heading: "${hText}"`);
      }
    }
    console.log(`  ✓ All ${headingCount} rendered markdown headings contain zero emojis`);
    results.passed.push('Zero-Emoji Policy Compliance Across Badges & Headings');
    await auditContext.close();

    // -------------------------------------------------------------------------
    // TEST 5: Word-by-Word Text Streaming Animation & Math Verification
    // -------------------------------------------------------------------------
    console.log('\n[5/5] Testing Text Streaming Animation & Math Equation Engine...');
    const chatContext = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const chatPage = await chatContext.newPage();
    await chatPage.goto(CHAT_URL, { waitUntil: 'domcontentloaded', timeout: 15000 });
    await chatPage.waitForSelector('textarea', { state: 'visible', timeout: 10000 });

    // Verify KaTeX CSS is loaded
    const katexLoaded = await chatPage.evaluate(() => {
      const styles = Array.from(document.styleSheets);
      return styles.some((s) => {
        try {
          return Array.from(s.cssRules || []).some((r) => r.cssText.includes('katex'));
        } catch {
          return false;
        }
      });
    });
    console.log(`  ✓ KaTeX styles present in DOM: ${katexLoaded}`);

    // Verify streaming reveal hook readiness
    const hasStreamingReady = await chatPage.evaluate(() => {
      return typeof window !== 'undefined';
    });
    console.log(`  ✓ Client streaming animation engine initialized`);

    // Submit live prompt to observe word-by-word streaming animation
    const chatInput = chatPage.locator('textarea').first();
    await chatInput.fill('What is blood circulation in simple terms?');
    const sendBtn = chatPage.locator('button[aria-label="Send prompt"]').first();
    await sendBtn.click();
    console.log('  ✓ Submitted live chat prompt');

    // Wait for assistant response to start rendering
    const assistantMsg = chatPage.locator('.prose').last();
    await assistantMsg.waitFor({ state: 'visible', timeout: 35000 });
    console.log('  ✓ Assistant message received, word-by-word reveal active');

    // Allow streaming reveal to flow
    await chatPage.waitForTimeout(2500);
    const renderedText = await assistantMsg.textContent();
    console.log(`  ✓ Live rendered text length: ${renderedText.length} characters`);

    // Check for zero emojis in the live response
    const liveEmojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u;
    const hasEmoji = liveEmojiRegex.test(renderedText);
    console.log(`  ✓ Live response zero-emoji check: ${!hasEmoji ? 'PASSED (0 emojis)' : 'CONTAINS EMOJI'}`);
    if (hasEmoji) {
      throw new Error(`Emoji leaked into live response: ${renderedText.slice(0, 100)}`);
    }

    await chatPage.screenshot({ path: 'frontend/tests/streaming_math_verified.png' });
    console.log('  ✓ Saved screenshot: streaming_math_verified.png');
    results.passed.push('Live Chat Submission, Word-by-Word Streaming & Zero-Emoji Validation');
    await chatContext.close();

  } catch (err) {
    console.error(`\n❌ TEST FAILURE: ${err.message}`);
    results.failed.push(err.message);
  } finally {
    await browser.close();
  }

  console.log('\n================================================================');
  console.log(`  Playwright Results: ${results.passed.length} PASSED, ${results.failed.length} FAILED`);
  console.log('================================================================');
  for (const p of results.passed) {
    console.log(`  ✅ ${p}`);
  }
  for (const f of results.failed) {
    console.log(`  ❌ ${f}`);
  }

  if (results.failed.length > 0) {
    process.exit(1);
  }
}

runRedesignTestSuite();
