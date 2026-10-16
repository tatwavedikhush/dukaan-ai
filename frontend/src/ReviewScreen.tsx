import type { FormEvent } from 'react';

export type ReviewProduct = {
  name: string;
  price: number | string;
  description: string;
  category: string;
  stock?: number;
  currency?: string;
  variants?: string[];
  image_url?: string;
};

type Props = {
  products: ReviewProduct[];
  onChange: (products: ReviewProduct[]) => void;
  onSave: (event?: FormEvent) => void;
  busy: boolean;
};

export default function ReviewScreen({ products, onChange, onSave, busy }: Props) {
  const update = (index: number, key: keyof ReviewProduct, value: string) =>
    onChange(products.map((product, itemIndex) => itemIndex === index ? { ...product, [key]: value } : product));
  return <section aria-label="Review products">
    <div className="section-title"><h2>Review products</h2><button className="outline" type="button" onClick={() => onChange([...products, { name: '', price: '', description: '', category: '', stock: 0, currency: 'INR', variants: [] }])}>＋ Add row</button></div>
    {products.map((product, index) => <div className="card product-edit" key={index}>
      <button className="remove" type="button" onClick={() => onChange(products.filter((_, itemIndex) => itemIndex !== index))}>Remove</button>
      {(['name', 'price', 'category'] as const).map((key) => <label key={key}>{key}<input value={product[key]} onChange={(event) => update(index, key, event.target.value)} /></label>)}
      <label>Description<textarea value={product.description} onChange={(event) => update(index, 'description', event.target.value)} /></label>
    </div>)}
    <button type="button" onClick={() => onSave()} disabled={busy}>Save products</button>
  </section>;
}
