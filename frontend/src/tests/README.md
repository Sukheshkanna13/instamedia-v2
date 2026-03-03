# Frontend Testing Guide

## Overview

This directory contains all frontend tests organized by type:
- `unit/` - Component and function unit tests
- `integration/` - API integration tests
- `e2e/` - End-to-end user flow tests

## Setup

1. Install test dependencies:
```bash
cd frontend
npm install
```

2. Install Playwright browsers (for e2e tests):
```bash
npx playwright install
```

## Running Tests

### All unit/integration tests
```bash
npm test
```

### With UI
```bash
npm run test:ui
```

### With coverage
```bash
npm run test:coverage
```

### E2E tests
```bash
npm run test:e2e
```

### E2E tests with UI
```bash
npx playwright test --ui
```

## Test Structure

### Unit Test Example

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@/tests/utils/test-utils';
import MyComponent from '@/components/MyComponent';

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent title="Test" />);
    expect(screen.getByText('Test')).toBeInTheDocument();
  });
});
```

### E2E Test Example

```typescript
import { test, expect } from '@playwright/test';

test('user can upload brand asset', async ({ page }) => {
  await page.goto('/');
  await page.click('text=Brand Assets');
  await page.setInputFiles('input[type="file"]', 'test-logo.png');
  await page.click('button:has-text("Upload")');
  await expect(page.locator('.success-message')).toBeVisible();
});
```

## Best Practices

1. **Component Tests**: Test behavior, not implementation
2. **User Interactions**: Use user-event for realistic interactions
3. **Accessibility**: Include accessibility checks in tests
4. **Mocking**: Use MSW for API mocking
5. **Cleanup**: Tests should not affect each other
