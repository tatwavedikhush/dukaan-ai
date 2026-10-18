import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import App from './App';

describe('manage catalogue', () => {
  it('offers the bundled sample-photo flow', () => {
    window.history.pushState({}, '', '/shop/demo/manage');
    render(<App />);
    expect(screen.getByRole('button', { name: /try it with sample photos/i })).toBeTruthy();
  });
});
