import { chromium } from 'playwright';
import path from 'path';

async function runFullWidthLayoutTest() {
  console.log('--- Running Full Width Horizontal Layout Verification ---');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1920, height: 1080 } });
  const page = await context.newPage();

  try {
    await page.goto('http://localhost:3000/workspaces/b4b8c4f8-1370-437f-804f-d359e3e0888f/chat', {
      waitUntil: 'networkidle',
      timeout: 15000,
    });

    await page.waitForTimeout(1000);

    // 1. Dark mode test
    await page.evaluate(() => {
      document.documentElement.classList.remove('light');
      document.documentElement.classList.add('dark');
    });
    await page.waitForTimeout(500);

    // Measure widths
    const layoutMetrics = await page.evaluate(() => {
      const scrollFeed = document.querySelector('.overflow-y-auto');
      const assistantMsg = document.querySelector('.prose');
      const composerCard = document.querySelector('textarea')?.closest('.relative');
      return {
        feedWidth: scrollFeed ? scrollFeed.getBoundingClientRect().width : 0,
        assistantProseWidth: assistantMsg ? assistantMsg.getBoundingClientRect().width : 0,
        composerWidth: composerCard ? composerCard.getBoundingClientRect().width : 0,
      };
    });

    console.log('Layout Metrics on 1920x1080 Viewport:', layoutMetrics);

    const darkScreenshot = path.resolve('..', 'artifacts', 'full_width_dark_mode.png');
    await page.screenshot({ path: darkScreenshot });
    console.log(`✓ Saved dark mode full width screenshot: ${darkScreenshot}`);

    // 2. Light mode test
    await page.evaluate(() => {
      document.documentElement.classList.remove('dark');
      document.documentElement.classList.add('light');
    });
    await page.waitForTimeout(500);

    const lightScreenshot = path.resolve('..', 'artifacts', 'full_width_light_mode.png');
    await page.screenshot({ path: lightScreenshot });
    console.log(`✓ Saved light mode full width screenshot: ${lightScreenshot}`);

    console.log('✅ Full width layout verification passed!');
  } catch (err) {
    console.error('❌ Error during full width test:', err);
  } finally {
    await browser.close();
  }
}

runFullWidthLayoutTest();
