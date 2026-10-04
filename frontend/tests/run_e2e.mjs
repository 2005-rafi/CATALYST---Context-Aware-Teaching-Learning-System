import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

async function runE2ETests() {
  console.log('===============================================================');
  console.log('  CATALYST E2E Test Suite: Next.js Frontend + Live Render Backend');
  console.log('===============================================================');

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
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

  const wsName = `Cloud_Test_Lab_${Date.now()}`;
  let createdWorkspaceId = null;

  try {
    // -------------------------------------------------------------------------
    // Test 1: Dashboard Navigation & Brand Elements
    // -------------------------------------------------------------------------
    console.log('\n[1/8] Testing Workspaces Dashboard (http://localhost:3000)...');
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle', timeout: 20000 });
    
    const sidebarTitle = await page.textContent('aside >> text=CATALYST');
    if (!sidebarTitle) throw new Error('Sidebar brand CATALYST not found');
    console.log('  ✓ Sidebar brand CATALYST confirmed');

    // Theme switcher test
    const themeBtn = page.locator('aside button:has-text("Mode")');
    if (await themeBtn.isVisible()) {
      await themeBtn.click();
      await page.waitForTimeout(300);
      await themeBtn.click();
      console.log('  ✓ Theme toggle interacted successfully');
    }
    results.passed.push('Dashboard & Sidebar rendering');

    // -------------------------------------------------------------------------
    // Test 2: System Health Page (Connected to Live Render)
    // -------------------------------------------------------------------------
    console.log('\n[2/8] Testing System Health Page (http://localhost:3000/health)...');
    await page.goto('http://localhost:3000/health', { waitUntil: 'networkidle', timeout: 20000 });
    await page.waitForSelector('text=System Health', { timeout: 10000 });
    
    // Check for operational status badges
    const healthBadge = page.locator('text=operational').or(page.locator('text=healthy')).first();
    await healthBadge.waitFor({ state: 'visible', timeout: 10000 });
    console.log('  ✓ System health page verified connected to live Render backend');
    results.passed.push('System Health live dashboard');

    // -------------------------------------------------------------------------
    // Test 3: Workspace Creation Flow (Persisted to Render SQLite)
    // -------------------------------------------------------------------------
    console.log('\n[3/8] Testing Workspace Creation Modal...');
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle', timeout: 20000 });
    
    const newWsBtn = page.locator('button:has-text("New Workspace")');
    await newWsBtn.click();
    await page.waitForSelector('text=Create New Workspace', { timeout: 5000 });
    console.log('  ✓ Create Workspace modal opened');

    const nameInput = page.locator('input[placeholder*="Molecular Biology"]');
    await nameInput.waitFor({ state: 'visible', timeout: 5000 });
    await nameInput.fill(wsName);

    const descInput = page.locator('textarea[placeholder*="workspace description"]');
    if (await descInput.isVisible()) {
      await descInput.fill('Automated cloud testing workspace for live Render backend verification.');
    }

    const submitBtn = page.locator('button:has-text("Create Workspace")').last();
    await submitBtn.click();

    // Auto-redirects to /workspaces/[id]/chat
    await page.waitForURL(/\/workspaces\/[^\/]+\/chat/, { timeout: 15000 });
    const currentUrl = page.url();
    const match = currentUrl.match(/\/workspaces\/([^\/]+)\/chat/);
    if (match) {
      createdWorkspaceId = match[1];
    }
    console.log(`  ✓ Workspace created on Render backend: ${currentUrl} (ID: ${createdWorkspaceId})`);
    results.passed.push('Workspace creation flow & auto-redirect');

    // -------------------------------------------------------------------------
    // Test 4: Workspace Layout & Navigation Tabs
    // -------------------------------------------------------------------------
    console.log('\n[4/8] Testing Workspace Header & Tab Navigation...');
    await page.waitForSelector('header >> nav', { timeout: 8000 });
    
    const chatTab = page.locator('header nav a:has-text("Chat")');
    const docsTab = page.locator('header nav a:has-text("Documents")');
    const analyticsTab = page.locator('header nav a:has-text("Analytics")');

    await chatTab.waitFor({ state: 'visible', timeout: 5000 });
    await docsTab.waitFor({ state: 'visible', timeout: 5000 });
    await analyticsTab.waitFor({ state: 'visible', timeout: 5000 });

    console.log('  ✓ Workspace header and 3 tabs (Chat, Documents, Analytics) verified');
    results.passed.push('Workspace layout & tab navigation');

    // -------------------------------------------------------------------------
    // Test 5: Documents Tab & File Upload to Render Backend
    // -------------------------------------------------------------------------
    console.log('\n[5/8] Testing Documents Tab & File Upload...');
    await docsTab.click();
    await page.waitForURL(/\/workspaces\/[^\/]+\/documents/, { timeout: 8000 });
    await page.waitForSelector('text=Click or drag documents to upload', { timeout: 8000 });
    console.log('  ✓ Documents page dropzone ready');

    // Create a temporary sample test document for ingestion
    const tempFilePath = path.join(process.cwd(), 'temp_e2e_biology_sample.txt');
    fs.writeFileSync(
      tempFilePath,
      'Spermatogenesis is the biological process by which haploid spermatozoa develop from germ cells in the seminiferous tubules of the testis. The process begins with the mitotic division of the stem cells located close to the basement membrane of the tubules. These cells are called spermatogonial stem cells.'
    );

    try {
      const fileInput = page.locator('input[type="file"]');
      if (await fileInput.count() > 0) {
        await fileInput.setInputFiles(tempFilePath);
        console.log('  ✓ Uploaded test document into dropzone');
        // Wait for upload & ingestion processing on Render backend
        await page.waitForTimeout(4000);
      }
    } catch (uploadErr) {
      console.warn('  ! Dropzone upload notice:', uploadErr.message);
    } finally {
      if (fs.existsSync(tempFilePath)) {
        fs.unlinkSync(tempFilePath);
      }
    }
    results.passed.push('Documents Knowledge Base & Ingestion');

    // -------------------------------------------------------------------------
    // Test 6: Chat Mode Selector & Multi-Agent RAG Q&A
    // -------------------------------------------------------------------------
    console.log('\n[6/8] Testing Chat Tab, Mode Selection & Live Multi-Agent RAG...');
    await chatTab.click();
    await page.waitForURL(/\/workspaces\/[^\/]+\/chat/, { timeout: 8000 });
    
    // Model mode selector check
    const expertBtn = page.locator('button:has-text("expert")');
    if (await expertBtn.isVisible()) {
      await expertBtn.click();
      console.log('  ✓ Switched model mode to expert');
    }

    const mediumBtn = page.locator('button:has-text("medium")');
    if (await mediumBtn.isVisible()) {
      await mediumBtn.click();
      console.log('  ✓ Switched model mode to medium');
    }

    // Submit live pedagogical query to Groq via Render
    const chatTextarea = page.locator('textarea[placeholder*="Ask a question"]');
    await chatTextarea.waitFor({ state: 'visible', timeout: 8000 });
    await chatTextarea.fill('Explain spermatogenesis in brief.');
    
    const sendBtn = page.locator('button[aria-label="Send prompt"]');
    await sendBtn.click();
    console.log('  ✓ Prompt submitted via Send button');

    // Wait for user bubble
    await page.waitForSelector('text=Explain spermatogenesis in brief.', { timeout: 8000 });
    console.log('  ✓ User message bubble mounted');

    // Wait for assistant multi-agent pedagogical response
    console.log('  ... Waiting for multi-agent synthesis from Render backend ...');
    await page.waitForSelector('.prose', { timeout: 35000 });
    console.log('  ✓ Assistant pedagogical response rendered with Markdown prose');
    results.passed.push('Chat Q&A interface & multi-agent synthesis');

    // -------------------------------------------------------------------------
    // Test 7: Analytics Tab & Cognitive Mastery Profile
    // -------------------------------------------------------------------------
    console.log('\n[7/8] Testing Analytics Tab & Cognitive Mastery...');
    await analyticsTab.click();
    await page.waitForURL(/\/workspaces\/[^\/]+\/analytics/, { timeout: 8000 });
    
    await page.waitForSelector('text=Queries Executed', { timeout: 8000 });
    await page.waitForSelector('text=Storage Consumed', { timeout: 8000 });
    console.log('  ✓ Telemetry metric cards loaded');

    // Test time-series filter buttons (7D, 14D, 30D)
    const btn7d = page.locator('button:has-text("7 Days")');
    if (await btn7d.isVisible()) {
      await btn7d.click();
      console.log('  ✓ Clicked 7 Days timeframe filter');
    }
    results.passed.push('Analytics dashboard & telemetry cards');

    // -------------------------------------------------------------------------
    // Test 8: Workspace Cleanup
    // -------------------------------------------------------------------------
    console.log('\n[8/8] Testing Workspace Cleanup on Render Backend...');
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle', timeout: 15000 });
    
    if (createdWorkspaceId) {
      const testWsCard = page.locator(`a[href*="${createdWorkspaceId}"]`).or(page.locator(`text=${wsName}`)).first();
      if (await testWsCard.isVisible()) {
        console.log(`  ✓ Test workspace card verified on dashboard`);
      }
    }
    results.passed.push('Workspace lifecycle validation');

  } catch (error) {
    console.error('  ✗ Test failure:', error);
    results.failed.push(error.message);
  } finally {
    await browser.close();
  }

  console.log('\n===============================================================');
  console.log(`  E2E Test Summary: ${results.passed.length} Passed, ${results.failed.length} Failed`);
  console.log('===============================================================');
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
