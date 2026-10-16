import { describe, expect, it } from 'vitest';
import { formatPrice, whatsappLink } from './App';

describe('catalogue utilities', () => {
  it('formats Indian prices', () => expect(formatPrice(12500)).toBe('₹12,500'));
  it('creates an encoded WhatsApp order link', () => {
    expect(whatsappLink('+91 98765 43210', 'Brownie', 125)).toBe('https://wa.me/919876543210?text=Hi%2C%20I\'d%20like%20to%20order%3A%20Brownie%20(%E2%82%B9125)');
  });
});
