import { chromium } from 'playwright';
import path from 'path';

async function testAnalyticsDashboard() {
  console.log('--- Running End-to-End Analytics Dashboard Verification ---');
  const browser = await chromium.launch({ headless: true });
  
  try {
    // 1. TEST DESKTOP ULTRA-WIDE (1920x1080) in Dark Mode
    console.log('[1/4] Testing Desktop Ultra-wide (1920x1080)...');
    const contextDesktop = await browser.newContext({ viewport: { width: 1920, height: 1080 } });
    const page = await contextDesktop.newPage();

    await page.goto('http://localhost:3000/workspaces/b4b8c4f8-1370-437f-804f-d359e3e0888f/analytics', {
      waitUntil: 'networkidle',
      timeout: 15000,
    });

    await page.waitForTimeout(1000);

    // Ensure Dark Mode
    await page.evaluate(() => {
      document.documentElement.classList.remove('light');
      document.documentElement.classList.add('dark');
    });
    await page.waitForTimeout(500);

    // Verify presence of all cards
    await page.waitForSelector('text=Query & Conversational Velocity', { timeout: 10000 });
    await page.waitForSelector('text=Cognitive Mastery & Memory Profile', { timeout: 10000 });
    await page.waitForSelector('text=Document Corpus & Visual Ingestion', { timeout: 10000 });
    await page.waitForSelector('text=Inference Distribution & Telemetry', { timeout: 10000 });

    console.log('✓ All analytics cards loaded successfully on desktop');

    // Hover over an activity bar to trigger tooltip
    const activityBar = page.locator('.group').last();
    if (await activityBar.isVisible()) {
      await activityBar.hover();
      await page.waitForTimeout(400);
      console.log('✓ Activity bar hover tooltip triggered');
    }

    const darkDesktopScreenshot = path.resolve('..', 'artifacts', 'analytics_dashboard_desktop_dark.png');
    await page.screenshot({ path: darkDesktopScreenshot, fullPage: true });
    console.log(`✓ Saved desktop dark mode screenshot: ${darkDesktopScreenshot}`);

    // 2. TEST DESKTOP LIGHT MODE (1440x900)
    console.log('[2/4] Testing Desktop Light Mode (1440x900)...');
    const contextLight = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const pageLight = await contextLight.newPage();

    await pageLight.goto('http://localhost:3000/workspaces/b4b8c4f8-1370-437f-804f-d359e3e0888f/analytics', {
      waitUntil: 'networkidle',
      timeout: 15000,
    });

    await pageLight.evaluate(() => {
      document.documentElement.classList.remove('dark');
      document.documentElement.classList.add('light');
    });
    await pageLight.waitForTimeout(500);

    // Test timeframe toggle
    const btn7Days = pageLight.locator('button:has-text("7 Days")');
    await btn7Days.click();
    await pageLight.waitForTimeout(500);
    console.log('✓ Clicked 7 Days filter');

    const lightScreenshot = path.resolve('..', 'artifacts', 'analytics_dashboard_desktop_light.png');
    await pageLight.screenshot({ path: lightScreenshot, fullPage: true });
    console.log(`✓ Saved desktop light mode screenshot: ${lightScreenshot}`);

    // 3. TEST TABLET VIEWPORT (768x1024)
    console.log('[3/4] Testing Tablet Viewport (768x1024)...');
    const contextTablet = await browser.newContext({ viewport: { width: 768, height: 1024 } });
    const pageTablet = await contextTablet.newPage();

    await pageTablet.goto('http://localhost:3000/workspaces/b4b8c4f8-1370-437f-804f-d359e3e0888f/analytics', {
      waitUntil: 'networkidle',
      timeout: 15000,
    });
    await pageTablet.waitForTimeout(500);

    const tabletScreenshot = path.resolve('..', 'artifacts', 'analytics_dashboard_tablet.png');
    await pageTablet.screenshot({ path: tabletScreenshot, fullPage: true });
    console.log(`✓ Saved tablet screenshot: ${tabletScreenshot}`);

    // 4. TEST MOBILE VIEWPORT (375x667)
    console.log('[4/4] Testing Mobile Viewport (375x667)...');
    const contextMobile = await browser.newContext({ viewport: { width: 375, height: 667 } });
    const pageMobile = await contextMobile.newPage();

    await pageMobile.goto('http://localhost:3000/workspaces/b4b8c4f8-1370-437f-804f-d359e3e0888f/analytics', {
      waitUntil: 'networkidle',
      timeout: 15000,
    });
    await pageMobile.waitForTimeout(500);

    const mobileScreenshot = path.resolve('..', 'artifacts', 'analytics_dashboard_mobile.png');
    await pageMobile.screenshot({ path: mobileScreenshot, fullPage: true });
    console.log(`✓ Saved mobile screenshot: ${mobileScreenshot}`);

    console.log('✅ End-to-End Analytics Dashboard Verification successfully completed!');
  } catch (err) {
    console.error('❌ Error during analytics dashboard test:', err);
  } finally {
    await browser.close();
  }
}

testAnalyticsDashboard();
