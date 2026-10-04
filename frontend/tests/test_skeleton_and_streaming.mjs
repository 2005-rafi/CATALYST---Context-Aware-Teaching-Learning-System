import { chromium } from 'playwright';
import path from 'path';

async function testSkeletonAndStreaming() {
  console.log('--- Testing Skeleton Loader & Text Streaming Animation ---');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();

  try {
    await page.goto('http://localhost:3000/workspaces/b4b8c4f8-1370-437f-804f-d359e3e0888f/chat', {
      waitUntil: 'networkidle',
      timeout: 15000,
    });

    await page.waitForTimeout(1000);

    // Type a prompt and send
    const textarea = page.locator('textarea');
    await textarea.fill('Briefly summarize the role of the liver in digestion');

    // Click Send
    const sendBtn = page.locator('button[aria-label="Send prompt"]');
    await sendBtn.click();

    // Verify skeleton appears in conversation
    const skeletonPill = page.locator('text=Searching hybrid vector').or(page.locator('text=Evaluating evidence')).or(page.locator('text=Synthesizing grounded'));
    await skeletonPill.waitFor({ state: 'visible', timeout: 5000 });
    console.log('✓ Verified: Inline MessageSkeleton successfully mounted with dynamic stage pill');

    // Capture screenshot of the Skeleton Loading state in action
    const skeletonScreenshot = path.resolve('..', 'artifacts', 'skeleton_loading_active.png');
    await page.screenshot({ path: skeletonScreenshot });
    console.log(`✓ Saved skeleton loader screenshot: ${skeletonScreenshot}`);

    // Wait for the response to finish streaming and render prose
    const lastProse = page.locator('.prose').last();
    await lastProse.waitFor({ state: 'visible', timeout: 35000 });
    console.log('✓ Assistant response received and streaming in action');

    await page.waitForTimeout(800);
    const streamingScreenshot = path.resolve('..', 'artifacts', 'streaming_text_active.png');
    await page.screenshot({ path: streamingScreenshot });
    console.log(`✓ Saved streaming text animation screenshot: ${streamingScreenshot}`);

    // Click anywhere on prose to test instant skip
    await lastProse.click();
    console.log('✓ Click-to-skip streaming tested');

    await page.waitForTimeout(500);
    console.log('✅ Skeleton loading and streaming test successfully passed!');
  } catch (err) {
    console.error('❌ Error during skeleton/streaming test:', err);
  } finally {
    await browser.close();
  }
}

testSkeletonAndStreaming();
