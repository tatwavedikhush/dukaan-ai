import { render, screen, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import App from './App';

describe('manage catalogue', () => {
  it('offers the bundled sample-photo flow', () => {
    window.history.pushState({}, '', '/shop/demo/manage');
    render(<App />);
    expect(screen.getByRole('button', { name: /try it with sample photos/i })).toBeTruthy();
  });
});

describe('public catalogue ordering', () => {
  it('shows WhatsApp ordering for variants, plain products, and stock states', async () => {
    vi.stubGlobal('fetch', vi.fn(() => Promise.resolve(new Response(JSON.stringify({
      name: 'Test Shop', whatsapp_number: '918696754461', products: [
        { id: 1, name: 'Kurta', price: 499, stock: 4, category: 'Fashion', variants: ['S', 'M'], image_url: '/uploads/kurta.png' },
        { id: 2, name: 'Tea', price: 120, stock: 2, category: 'Groceries' },
        { id: 3, name: 'Sold Out', price: 50, stock: 0, category: 'Other' },
      ],
    }), { status: 200 }))));
    window.history.pushState({}, '', '/shop/test-shop');
    render(<App />);
    await waitFor(() => expect(screen.getByRole('heading', { name: 'Test Shop' })).toBeTruthy());
    expect(screen.getByRole('link', { name: /chat on whatsapp/i }).getAttribute('href')).toContain('wa.me/918696754461');
    const orders = screen.getAllByRole('link', { name: /order on whatsapp/i });
    expect(orders).toHaveLength(2);
    expect(orders[0].getAttribute('href')).toContain(encodeURIComponent('Kurta (S)'));
    expect(orders[1].getAttribute('href')).toContain(encodeURIComponent('Tea'));
    expect((screen.getByRole('button', { name: 'Out of stock' }) as HTMLButtonElement).disabled).toBe(true);
    vi.unstubAllGlobals();
  });
});
