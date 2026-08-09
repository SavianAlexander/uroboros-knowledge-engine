const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', error => console.log('PAGE ERROR:', error.message));
  page.on('requestfailed', request =>
    console.log('REQUEST FAILED:', request.url(), request.failure().errorText)
  );

  console.log("Navigating to http://127.0.0.1:8085 ...");
  await page.goto('http://127.0.0.1:8085', { waitUntil: 'networkidle0' });
  
  console.log("Done checking.");
  await browser.close();
})();
