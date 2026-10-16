const modal = document.querySelector('#modal');
document.querySelector('#open-form').addEventListener('click', () => { modal.hidden = false; document.querySelector('input').focus(); });
document.querySelector('#close-form').addEventListener('click', () => { modal.hidden = true; });
document.querySelector('#product-form').addEventListener('submit', (event) => {
  event.preventDefault();
  const data = new FormData(event.target); const name = data.get('name'); const price = data.get('price');
  const row = document.createElement('div'); row.className = 'product';
  row.innerHTML = `<span class="product-icon peach">✦</span><div><strong>${name}</strong><small>SKU: NEW · ₹${price}</small></div><span class="status good">In stock</span><b>0</b><span class="dots">···</span>`;
  document.querySelector('#product-list').prepend(row); event.target.reset(); modal.hidden = true;
});
