import { chromium } from 'playwright';
import path from 'path';
import fs from 'fs';

const OUT_DIR = path.resolve('docs', 'ux_journey');
if (!fs.existsSync(OUT_DIR)) {
  fs.mkdirSync(OUT_DIR, { recursive: true });
}

async function capture() {
  console.log('Starting UX Journey Capture...');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1200 },
    colorScheme: 'dark',
  });
  const page = await context.newPage();

  // Make sure dev server is running
  const url = 'http://localhost:8000';
  console.log(`Navigating to ${url}...`);
  try {
    await page.goto(url, { waitUntil: 'networkidle' });
  } catch(e) {
    console.error('Failed to connect to dev server. Is the Uroboros backend running on port 8000? Start it with: python main.py');
    await browser.close();
    process.exit(1);
  }

  const views = [
    { label: 'Dashboard', file: '01_dashboard_view.png' },
    { label: 'Workspace', file: '02_workspace_view.png' },
    { label: 'Explorer', file: '03_explorer_view.png' },
    { label: 'Ingestion', file: '04_ingestion_view.png' },
    { label: 'Graph', file: '05_graph_view.png' },
    { label: 'AI Chat', file: '06_chat_view.png' },
    { label: 'Processes', file: '07_config_view.png' },
    { label: 'System', file: '08_settings_view.png' }
  ];

  for (const view of views) {
    console.log(`Capturing ${view.label}...`);
    // Click the sidebar navigation item
    await page.locator(`nav button:has-text("${view.label}")`).click();
    
    // For Graph view, wait longer for 3D engine to render
    if (view.label === 'Graph') {
      await page.waitForTimeout(3000);
    } else {
      await page.waitForTimeout(1500); // Give React more time to fetch DB data
    }
    
    // Wait for fonts to load
    await page.evaluate(() => document.fonts.ready);
    
    await page.screenshot({ path: path.join(OUT_DIR, view.file), fullPage: true });
  }

  // Capture Command Palette
  console.log('Capturing Command Palette...');
  await page.keyboard.press('Control+K');
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(OUT_DIR, '09_command_palette.png'), fullPage: true });
  await page.keyboard.press('Escape');
  await page.waitForTimeout(500);
  
  // Capture Light Mode
  console.log('Capturing Light Mode System Settings...');
  await page.locator(`nav button:has-text("System")`).click();
  await page.waitForTimeout(1000);
  // Click theme toggle in settings
  await page.locator('button:has-text("Toggle between dark and light appearance")').click({ force: true }).catch(async () => {
      await page.evaluate(() => {
          const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerHTML.includes('lucide-sun') || b.innerHTML.includes('lucide-moon'));
          if (btn) btn.click();
      });
  });
  await page.waitForTimeout(500);
  await page.screenshot({ path: path.join(OUT_DIR, '10_light_mode.png'), fullPage: true });

  await browser.close();
  console.log('Done!');
}

capture().catch(console.error);
