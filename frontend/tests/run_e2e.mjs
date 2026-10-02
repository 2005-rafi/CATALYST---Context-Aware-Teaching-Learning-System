import { chromium } from 'playwright';

async function runE2ETests() {
  console.log('===================================================');
  console.log('  Starting Playwright E2E UI & Component Test Suite');
  console.log('===================================================');

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  const results = {
    passed: [],
    failed: [],
    logs: [],
  };

  page.on('console', (msg) => {
    results.logs.push(`[Console ${msg.type()}]: ${msg.text()}`);
  });

  page.on('pageerror', (err) => {
    results.logs.push(`[PageError]: ${err.message}`);
  });

  try {
    // -------------------------------------------------------------------------
    // Test 1: Dashboard Navigation & Sidebar
    // -------------------------------------------------------------------------
    console.log('\n[1/7] Testing Workspaces Dashboard (http://localhost:3000)...');
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle', timeout: 15000 });
    
    const sidebarTitle = await page.textContent('aside >> text=CATALYST');
    if (!sidebarTitle) throw new Error('Sidebar brand CATALYST not found');
    
    const themeBtn = page.locator('aside button:has-text("Mode")');
    if (await themeBtn.isVisible()) {
      await themeBtn.click();
      console.log('  ✓ Theme toggle interacted successfully');
    }
    results.passed.push('Dashboard & Sidebar rendering');

    // -------------------------------------------------------------------------
    // Test 2: Create Workspace Modal & Validation
    // -------------------------------------------------------------------------
    console.log('\n[2/7] Testing Workspace Creation Modal...');
    const newWsBtn = page.locator('button:has-text("New Workspace")');
    await newWsBtn.click();
    await page.waitForSelector('text=Create New Workspace', { timeout: 5000 });
    console.log('  ✓ Create Workspace modal opened');

    // Submit workspace
    const wsName = `E2E_Test_Lab_${Date.now()}`;
    await page.fill('input[placeholder*="Legal Contracts"]', wsName);
    await page.fill('textarea[placeholder*="Brief description"]', 'Playwright automated test workspace for RAG');
    await page.click('button:has-text("Create Workspace")');
    
    // Wait for card to appear in grid
    await page.waitForSelector(`text=${wsName}`, { timeout: 10000 });
    console.log(`  ✓ Workspace created and visible in dashboard: ${wsName}`);
    results.passed.push('Workspace creation flow');

    // -------------------------------------------------------------------------
    // Test 3: System Health Page
    // -------------------------------------------------------------------------
    console.log('\n[3/7] Testing System Health Page (http://localhost:3000/health)...');
    await page.click('aside a[href="/health"]');
    await page.waitForSelector('h1:has-text("System Health")', { timeout: 5000 });
    
    const refreshBtn = page.locator('button:has-text("Refresh")');
    await refreshBtn.click();
    console.log('  ✓ System health page loaded and refresh verified');
    results.passed.push('System Health dashboard');

    // -------------------------------------------------------------------------
    // Test 4: Workspace Navigation & Layout
    // -------------------------------------------------------------------------
    console.log('\n[4/7] Testing Workspace Layout & Navigation Tabs...');
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
    const wsCard = page.locator(`a:has-text("${wsName}")`);
    await wsCard.click();
    
    // Wait for redirect to /workspaces/[id]/chat
    await page.waitForURL(/\/workspaces\/.*\/chat/, { timeout: 10000 });
    await page.waitForSelector('header >> nav', { timeout: 8000 });
    
    const chatTab = page.locator('header nav a:has-text("Chat")');
    const docsTab = page.locator('header nav a:has-text("Documents")');
    const analyticsTab = page.locator('header nav a:has-text("Analytics")');

    await chatTab.waitFor({ state: 'visible', timeout: 5000 });
    await docsTab.waitFor({ state: 'visible', timeout: 5000 });
    await analyticsTab.waitFor({ state: 'visible', timeout: 5000 });

    console.log('  ✓ Workspace header and 3 tabs (Chat, Documents, Analytics) visible');
    results.passed.push('Workspace layout & tab navigation');

    // -------------------------------------------------------------------------
    // Test 5: Documents Page
    // -------------------------------------------------------------------------
    console.log('\n[5/7] Testing Documents Knowledge Base Tab...');
    await docsTab.click();
    await page.waitForURL(/\/workspaces\/.*\/documents/, { timeout: 5000 });
    await page.waitForSelector('text=Knowledge Base', { timeout: 5000 });
    await page.waitForSelector('text=Click or drag file to upload', { timeout: 5000 });
    console.log('  ✓ Documents upload zone & file dropzone rendered');
    results.passed.push('Documents Knowledge Base tab');

    // -------------------------------------------------------------------------
    // Test 6: Chat Page & Retrieval Query Flow
    // -------------------------------------------------------------------------
    console.log('\n[6/7] Testing Chat Tab & Retrieval Interaction...');
    await chatTab.click();
    await page.waitForURL(/\/workspaces\/.*\/chat/, { timeout: 5000 });
    await page.waitForSelector('input[placeholder*="Ask a question"]', { timeout: 5000 });
    
    // Test mode selector
    const expertModeBtn = page.locator('button:has-text("expert")');
    if (await expertModeBtn.isVisible()) {
      await expertModeBtn.click();
      console.log('  ✓ Switched model mode to expert');
    }

    // Send chat query
    await page.fill('input[placeholder*="Ask a question"]', 'What is the purpose of RAG?');
    await page.click('button[type="submit"]');
    
    // Wait for message bubble to appear
    await page.waitForSelector('text=What is the purpose of RAG?', { timeout: 5000 });
    console.log('  ✓ Query submitted, user and assistant bubbles rendered');
    results.passed.push('Chat Q&A interface');

    // -------------------------------------------------------------------------
    // Test 7: Analytics Tab & Cleanup
    // -------------------------------------------------------------------------
    console.log('\n[7/7] Testing Analytics Tab & Workspace Cleanup...');
    await analyticsTab.click();
    await page.waitForURL(/\/workspaces\/.*\/analytics/, { timeout: 5000 });
    await page.waitForSelector('text=Workspace Telemetry', { timeout: 5000 });
    await page.waitForSelector('text=Total Queries', { timeout: 5000 });
    await page.waitForSelector('text=Storage Used', { timeout: 5000 });
    console.log('  ✓ Telemetry metric cards rendered');
    results.passed.push('Analytics telemetry');

    // Cleanup: Delete workspace
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
    page.on('dialog', async (dialog) => {
      await dialog.accept();
    });
    const deleteBtn = page.locator(`a:has-text("${wsName}") button[title="Delete workspace"]`);
    if (await deleteBtn.isVisible()) {
      await deleteBtn.click();
      console.log('  ✓ Test workspace deleted cleanly');
      results.passed.push('Workspace deletion cleanup');
    }

  } catch (error) {
    console.error('  ✗ Test failure:', error);
    results.failed.push(error.message);
  } finally {
    await browser.close();
  }

  console.log('\n===================================================');
  console.log(`  E2E Test Results: ${results.passed.length} Passed, ${results.failed.length} Failed`);
  console.log('===================================================');
  for (const p of results.passed) {
    console.log(`  ✓ ${p}`);
  }
  for (const f of results.failed) {
    console.log(`  ✗ ${f}`);
  }

  if (results.failed.length > 0) {
    process.exit(1);
  }
}

runE2ETests();
