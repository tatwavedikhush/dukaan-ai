import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import App from './App';

describe('manage catalogue', () => {
  it('loads bundled sample photos and text from the Try it button', async () => {
    const blob = new Blob(['sample'], { type: 'image/png' });
    vi.stubGlobal('fetch', vi.fn((url: string) => {
      if (url.includes('/samples/')) return Promise.resolve(new Response(blob));
      return Promise.resolve(new Response(JSON.stringify({ slug: 'demo' }), { status: 200 }));
    }));
    window.history.pushState({}, '', '/shop/demo/manage');
    render(<App />);
    fireEvent.click(screen.getByRole('button', { name: /try it with sample photos/i }));
    await waitFor(() => expect(screen.getByDisplayValue(/Handmade lavender soap/)).toBeTruthy());
    expect(screen.getAllByAltText(/Product preview/)).toHaveLength(3);
    vi.unstubAllGlobals();
  });
});
