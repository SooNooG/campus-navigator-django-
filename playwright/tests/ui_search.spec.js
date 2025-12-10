const { test, expect } = require('@playwright/test');

test('Поиск работает и отображает результаты', async ({ page }) => {
    await page.goto('http://127.0.0.1:8000/search?q=101');

    await expect(page.locator('h2')).toContainText('Результаты поиска');
    await expect(page.locator('body')).toContainText('101');
});
