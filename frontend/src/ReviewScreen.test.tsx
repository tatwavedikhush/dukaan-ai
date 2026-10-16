import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import ReviewScreen from './ReviewScreen';

describe('ReviewScreen', () => {
  it('edits and adds product rows before saving', () => {
    const onChange = vi.fn();
    render(<ReviewScreen products={[{ name: 'Tea', price: 20, description: '', category: 'Groceries' }]} onChange={onChange} onSave={vi.fn()} busy={false} />);
    fireEvent.change(screen.getByDisplayValue('Tea'), { target: { value: 'Masala Tea' } });
    fireEvent.click(screen.getByRole('button', { name: /add row/i }));
    expect(onChange).toHaveBeenCalledTimes(2);
  });
});
