import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import ReviewScreen from './ReviewScreen';

describe('ReviewScreen', () => {
  it('shows one review card for each extracted product', () => {
    render(<ReviewScreen products={[
      { name: 'Red Cotton Kurta', price: 499, description: '', category: 'Fashion' },
      { name: 'Classic Blue Jeans', price: 899, description: '', category: 'Fashion' },
      { name: 'Masala Namkeen', price: 120, description: '', category: 'Groceries' },
    ]} onChange={vi.fn()} onSave={vi.fn()} busy={false} />);
    expect(screen.getAllByRole('button', { name: 'Remove' })).toHaveLength(3);
    expect(screen.getByDisplayValue('Red Cotton Kurta')).toBeTruthy();
    expect(screen.getByDisplayValue('Classic Blue Jeans')).toBeTruthy();
    expect(screen.getByDisplayValue('Masala Namkeen')).toBeTruthy();
  });

  it('edits and adds product rows before saving', () => {
    const onChange = vi.fn();
    render(<ReviewScreen products={[{ name: 'Tea', price: 20, description: '', category: 'Groceries' }]} onChange={onChange} onSave={vi.fn()} busy={false} />);
    fireEvent.change(screen.getByDisplayValue('Tea'), { target: { value: 'Masala Tea' } });
    fireEvent.click(screen.getByRole('button', { name: /add row/i }));
    expect(onChange).toHaveBeenCalledTimes(2);
  });
});
