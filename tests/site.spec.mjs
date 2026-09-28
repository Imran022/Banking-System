import {test,expect} from '@playwright/test';
const SITE_URL=process.env.CAPITOL_LEDGER_URL||'/';

test('feed opens member and ticker detail and keeps preview routing in-app',async({page})=>{
  await page.goto(SITE_URL);
  await expect(page.locator('#main h1')).toHaveText('Trading activity');
  const person=page.locator('#main .row .person').first();
  const personName=(await person.locator('.pname').innerText()).trim();
  await person.click();
  await expect(page.locator('#main h1')).toHaveText(personName);
  await expect(page).toHaveURL(/#member\//);
  await page.locator('.nav[data-view="feed"]').click();
  const tickerLink=page.locator('#main .row .ticker').first();
  const ticker=(await tickerLink.innerText()).trim();
  await tickerLink.click();
  await expect(page.locator('#main h1')).toHaveText(`${ticker} transactions`);
  await expect(page).toHaveURL(new RegExp(`#ticker/${ticker}$`));
  await expect(page.locator('#main .row').first()).toBeVisible();
});

test('politician directory search and filters open a working profile',async({page})=>{
  await page.goto(SITE_URL);
  await page.locator('.nav[data-view="politicians"]').click();
  await expect(page.locator('#main h1')).toHaveText('Politicians');
  const party=page.locator('#main select[data-filter="party"]');
  await party.selectOption('Democrat');
  const first=page.locator('#main .member').first();
  await expect(first.locator('.pill')).toHaveText('Democrat');
  const name=(await first.locator('.pname').innerText()).trim();
  await first.click();
  await expect(page.locator('#main h1')).toHaveText(name);
  await expect(page.locator('#main')).toContainText('Transaction history');
});

test('feed chamber, party, and action filters narrow trades',async({page})=>{
  await page.goto(SITE_URL);
  await page.locator('#main select[data-filter="chamber"]').selectOption('House');
  await page.locator('#main select[data-filter="party"]').selectOption('Republican');
  await page.locator('#main select[data-filter="direction"]').selectOption('buy');
  const rows=page.locator('#main .row');
  await expect(rows.first()).toBeVisible();
  const count=await rows.count();
  for(let i=0;i<count;i++){
    await expect(rows.nth(i).locator('.person .pmeta')).toContainText('House');
    await expect(rows.nth(i).locator('.person .pmeta')).toContainText('Republican');
    await expect(rows.nth(i).locator('.direction')).toContainText('Buy');
  }
});

test('search remains usable and ticker form opens the requested symbol',async({page})=>{
  await page.goto(SITE_URL);
  const ticker=(await page.locator('#main .row .ticker').first().innerText()).trim();
  await page.locator('#globalSearch').fill(ticker);
  await page.locator('#searchGo').click();
  await expect(page.locator('#main .row').first().locator('.ticker')).toHaveText(ticker);
  await page.locator('.nav[data-view="ticker"]').click();
  await page.locator('#tickerForm input[name="ticker"]').fill(ticker);
  await page.locator('#tickerForm button').click();
  await expect(page.locator('#main h1')).toHaveText(`${ticker} transactions`);
});

test('pagination advances the visible feed page',async({page})=>{
  await page.goto(SITE_URL);
  const first=await page.locator('#main .row').first().innerText();
  await page.locator('#main .pager button').last().click();
  await expect(page.locator('#main .pager')).toContainText('Page 2');
  await expect(page.locator('#main .row').first()).not.toContainText(first.slice(0,35));
});

test('member filters and pagination stay on the profile',async({page})=>{
  await page.goto(SITE_URL);
  await page.locator('#main .row .person').first().click();
  await expect(page.locator('#main')).toContainText('Transaction history');
  const tradeSearch=page.locator('#main #localSearch');
  await tradeSearch.fill('THIS_SHOULD_NOT_MATCH');
  await expect(page.locator('#main')).toContainText('No disclosures match');
  await expect(page).toHaveURL(/#member\//);
});
