const { test, expect } = require('@playwright/test');

test('Карта отображается и элементы управления видны', async ({ page }) => {
    await page.goto('http://127.0.0.1:8000/');

    await expect(page.locator('#map')).toBeVisible();
    await expect(page.locator('#routeFrom')).toBeVisible();
    await expect(page.locator('#routeTo')).toBeVisible();
    await expect(page.locator('#buildRouteBtn')).toBeVisible();
});
test('Селекты маршрута заполняются списком POI', async ({ page }) => {
    await page.goto('http://127.0.0.1:8000/');

    await page.waitForTimeout(1500); // ждём загрузку fetch()

    const fromOptions = await page.locator('#routeFrom option').count();
    expect(fromOptions).toBeGreaterThan(1);
});

test('Избранное скрыто для неавторизованных пользователей', async ({ page }) => {
    await page.goto('http://127.0.0.1:8000/');
    await expect(page.locator('#favoritesList')).not.toBeVisible();
});

