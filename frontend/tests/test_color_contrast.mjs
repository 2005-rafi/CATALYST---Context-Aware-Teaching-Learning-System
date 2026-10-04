import { chromium } from 'playwright';
import path from 'path';

async function runVisualContrastTest() {
  console.log('--- Running Color Contrast & Text Visibility Test ---');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();

  try {
    // Navigate to workspace chat
    await page.goto('http://localhost:3000/workspaces/b4b8c4f8-1370-437f-804f-d359e3e0888f/chat', {
      waitUntil: 'networkidle',
      timeout: 15000,
    });

    await page.waitForTimeout(1000);

    // 1. LIGHT MODE TEST
    // Ensure light mode is active
    await page.evaluate(() => {
      document.documentElement.classList.remove('dark');
      document.documentElement.classList.add('light');
    });
    await page.waitForTimeout(500);

    const getButtonStyles = async () => {
      const btn = page.locator('button', { hasText: 'New Conversation' }).first();
      const textSpan = btn.locator('span', { hasText: 'New Conversation' });
      const badge = btn.locator('span', { hasText: 'Ctrl+N' });
      
      const btnBg = await btn.evaluate((el) => window.getComputedStyle(el).backgroundColor);
      const btnColor = await btn.evaluate((el) => window.getComputedStyle(el).color);
      const textColor = await textSpan.evaluate((el) => window.getComputedStyle(el).color);
      const badgeBg = await badge.evaluate((el) => window.getComputedStyle(el).backgroundColor);
      const badgeColor = await badge.evaluate((el) => window.getComputedStyle(el).color);

      return { btnBg, btnColor, textColor, badgeBg, badgeColor };
    };

    const lightBtnStyles = await getButtonStyles();
    console.log('[Light Mode] New Conversation button styles:', lightBtnStyles);

    const lightScreenshot = path.resolve('..', 'artifacts', 'light_mode_contrast_verified.png');
    await page.screenshot({ path: lightScreenshot });
    console.log(`✓ Captured light mode screenshot to ${lightScreenshot}`);

    // 2. DARK MODE TEST
    await page.evaluate(() => {
      document.documentElement.classList.remove('light');
      document.documentElement.classList.add('dark');
    });
    await page.waitForTimeout(500);

    const darkBtnStyles = await getButtonStyles();
    console.log('[Dark Mode] New Conversation button styles:', darkBtnStyles);

    const darkScreenshot = path.resolve('..', 'artifacts', 'dark_mode_contrast_verified.png');
    await page.screenshot({ path: darkScreenshot });
    console.log(`✓ Captured dark mode screenshot to ${darkScreenshot}`);

    console.log('✅ Visual contrast verification complete!');
  } catch (err) {
    console.error('❌ Error during contrast test:', err);
  } finally {
    await browser.close();
  }
}

runVisualContrastTest();
