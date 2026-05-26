import { expect, test } from '@playwright/test'

test('responds on the health check endpoint', async ({ page }) => {
    const response = await page.goto('/up')
    expect(response?.status()).toBe(200)
})