import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

const outDir = path.resolve(process.cwd(), 'docs/ux_journey');
if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
}

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function run() {
    console.log('Starting UX Journey Capture...');
    const browser = await chromium.launch({ headless: true });
    
    const context = await browser.newContext({
        viewport: { width: 1440, height: 900 },
        deviceScaleFactor: 2, // High resolution
    });

    const page = await context.newPage();
    
    // Fail on console errors
    page.on('pageerror', (err) => {
        console.error(`Visual capture blocked: console exception found - ${err.message}`);
        process.exit(1);
    });

    console.log('Navigating to http://localhost:3000 ...');
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });

    // Wait for fonts to load
    await page.evaluate(() => document.fonts.ready);
    await delay(1000);

    // Helper to capture a view
    const captureView = async (buttonId, filename) => {
        console.log(`Capturing: ${buttonId}`);
        // Click the sidebar button that contains the data-tab ID
        await page.locator(`button[data-tab="${buttonId}"]`).click();
        await delay(1000); // wait for transitions
        await page.screenshot({ path: path.join(outDir, filename), fullPage: true });
    };

    // 1. Dashboard View
    await captureView('dashboard', '01_dashboard.png');

    // 2. Workspace View
    await captureView('workspace', '02_workspace.png');

    // 3. Explorer / Search View
    await captureView('search', '03_search.png');

    // 4. Ingestion View
    await captureView('ingestion', '04_ingestion.png');

    // 5. Graph View
    await captureView('graph', '05_graph.png');

    // 6. AI Chat View
    await captureView('chat', '06_chat.png');

    // 7. Processes / Config View
    await captureView('config', '07_config.png');

    // 8. System Settings View
    await captureView('settings', '08_settings.png');

    // 9. Command Palette Modal
    console.log('Capturing: Command Palette');
    // Open Command Palette
    await page.locator('[data-testid="command-palette-btn"]').click();
    await delay(500);
    await page.screenshot({ path: path.join(outDir, '09_command_palette.png'), fullPage: true });
    // Close Command Palette (Escape key)
    await page.keyboard.press('Escape');
    await delay(500);

    console.log('Successfully captured all views!');
    await browser.close();
}

run().catch(err => {
    console.error('Capture failed:', err);
    process.exit(1);
});
