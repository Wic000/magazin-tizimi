/**
 * Magazin tizimi - Frontend (O'zbek)
 * Multi-user, responsive UI
 */
const API_BASE = window.location.origin + '/api';

// State
let token = localStorage.getItem('token');
let user = JSON.parse(localStorage.getItem('user') || '{}');
let products = [];
let cart = [];

// Init
document.addEventListener('DOMContentLoaded', () => {
  if (token && user.username) {
    showMain();
    loadProducts();
  } else {
    showLogin();
  }
  bindEvents();
});

function bindEvents() {
  document.getElementById('loginForm')?.addEventListener('submit', handleLogin);
  document.getElementById('logoutBtn')?.addEventListener('click', handleLogout);
  document.getElementById('menuBtn')?.addEventListener('click', () =>
    document.getElementById('sidebar').classList.toggle('open'));
  document.querySelectorAll('.nav-btn[data-page]').forEach(btn =>
    btn.addEventListener('click', () => switchPage(btn.dataset.page)));
  document.getElementById('addProductBtn')?.addEventListener('click', openProductModal);
  document.getElementById('productForm')?.addEventListener('submit', saveProduct);
  document.getElementById('productModalCancel')?.addEventListener('click', closeProductModal);
  document.getElementById('sellBtn')?.addEventListener('click', sellCart);
  document.getElementById('productSearch')?.addEventListener('input', debounce(loadProducts, 300));
  document.getElementById('showArchived')?.addEventListener('change', loadProducts);
  document.getElementById('sotuvSearch')?.addEventListener('input', debounce(filterProductsForSale, 300));
  document.getElementById('reportLoadBtn')?.addEventListener('click', loadReport);
  document.getElementById('reportFrom')?.addEventListener('change', loadReport);
  document.getElementById('reportTo')?.addEventListener('change', loadReport);
}

async function handleLogin(e) {
  e.preventDefault();
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value;
  if (!username || !password) {
    alert('Foydalanuvchi nomi va parol kiriting');
    return;
  }
  try {
    const res = await fetch(API_BASE + '/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Kirish xatosi');
    token = data.access_token;
    user = data.user;
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
    showMain();
    loadProducts();
  } catch (err) {
    alert(err.message || 'Tarmoq xatosi. Qayta urinib ko\'ring.');
  }
}

function handleLogout() {
  token = null;
  user = {};
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  showLogin();
}

function showLogin() {
  document.getElementById('loginPage').classList.remove('hidden');
  document.getElementById('mainPage').classList.add('hidden');
}

function showMain() {
  document.getElementById('loginPage').classList.add('hidden');
  document.getElementById('mainPage').classList.remove('hidden');
  document.getElementById('userName').textContent = user.full_name || user.username;
  loadProducts();
  loadOmborStats();
  loadReport();
}

function switchPage(page) {
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-btn[data-page]').forEach(b => b.classList.remove('active'));
  document.getElementById(page + 'Section')?.classList.add('active');
  document.querySelector(`.nav-btn[data-page="${page}"]`)?.classList.add('active');
  document.getElementById('sidebar')?.classList.remove('open');
  if (page === 'sotuv') {
    loadProductsForSale();
  } else if (page === 'ombor') {
    loadOmborStats();
    loadOmborProducts();
  } else if (page === 'hisobot') {
    loadReport();
  } else if (page === 'mahsulot') {
    loadProducts();
  }
}

async function api(url, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: 'Bearer ' + token }),
    ...options.headers
  };
  const res = await fetch(API_BASE + url, { ...options, headers });
  if (res.status === 401) {
    alert('Sessiya tugadi. Qayta kiring.');
    handleLogout();
    throw new Error('Unauthorized');
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Server xatosi');
  }
  return res.json().catch(() => ({}));
}

async function loadProducts() {
  const search = document.getElementById('productSearch')?.value || '';
  const activeOnly = !document.getElementById('showArchived')?.checked;
  try {
    products = await api(
      `/products?active_only=${activeOnly}&search=${encodeURIComponent(search)}`
    );
    renderProductTable();
  } catch (err) {
    alert(err.message);
  }
}

async function loadProductsForSale() {
  const search = document.getElementById('sotuvSearch')?.value || '';
  try {
    products = await api(`/products?active_only=true&search=${encodeURIComponent(search)}`);
    renderProductListForSale();
  } catch (err) {
    alert(err.message);
  }
}

function filterProductsForSale() {
  loadProductsForSale();
}

function renderProductTable() {
  const isAdmin = user.role === 'admin';
  const html = `
    <table>
      <thead>
        <tr>
          <th>Nomi</th>
          <th>Narx</th>
          <th>Miqdor</th>
          <th>Holat</th>
          ${isAdmin ? '<th>Amallar</th>' : ''}
        </tr>
      </thead>
      <tbody>
        ${products.map(p => `
          <tr>
            <td>${escapeHtml(p.name)}</td>
            <td>${formatNumber(p.price)} so'm</td>
            <td>${p.quantity} ${p.unit}</td>
            <td>${p.is_active ? 'Faol' : 'Arxiv'}</td>
            ${isAdmin ? `
              <td>
                <button class="action-btn edit" onclick="editProduct(${p.id})">Tahrirlash</button>
                ${p.is_active ?
                  `<button class="action-btn archive" onclick="archiveProduct(${p.id})">Arxivlash</button>` :
                  `<button class="action-btn edit" onclick="restoreProduct(${p.id})">Qayta qo'shish</button>`
                }
              </td>
            ` : ''}
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;
  document.getElementById('productTable').innerHTML = products.length ? html : '<p>Mahsulot yo\'q</p>';
}

function renderProductListForSale() {
  const list = document.getElementById('sotuvProductList');
  list.innerHTML = products.map(p => `
    <div class="product-item" onclick="addToCart(${p.id})">
      <span>${escapeHtml(p.name)}</span>
      <span class="price">${formatNumber(p.price)} so'm · ${p.quantity} dona</span>
    </div>
  `).join('') || '<p>Mahsulot topilmadi</p>';
}

function addToCart(productId) {
  const p = products.find(x => x.id === productId);
  if (!p || p.quantity <= 0) return;
  const existing = cart.find(x => x.product_id === productId);
  if (existing) {
    if (existing.quantity >= p.quantity) return;
    existing.quantity++;
  } else {
    cart.push({
      product_id: p.id,
      product_name: p.name,
      price: p.price,
      cost_price: p.cost_price || 0,
      quantity: 1
    });
  }
  updateCartDisplay();
}

function removeFromCart(productId) {
  cart = cart.filter(x => x.product_id !== productId);
  updateCartDisplay();
}

function changeCartQty(productId, delta) {
  const item = cart.find(x => x.product_id === productId);
  if (!item) return;
  const p = products.find(x => x.id === productId);
  item.quantity = Math.max(0, Math.min(p?.quantity || 999, item.quantity + delta));
  if (item.quantity <= 0) cart = cart.filter(x => x.product_id !== productId);
  updateCartDisplay();
}

function updateCartDisplay() {
  const container = document.getElementById('cartItems');
  const total = cart.reduce((s, i) => s + i.price * i.quantity, 0);
  const profit = cart.reduce((s, i) => s + (i.price - i.cost_price) * i.quantity, 0);
  container.innerHTML = cart.map(i => `
    <div class="cart-item">
      <span>${escapeHtml(i.product_name)} × ${i.quantity}</span>
      <span>
        <button class="action-btn edit" onclick="changeCartQty(${i.product_id}, -1)">−</button>
        <button class="action-btn edit" onclick="changeCartQty(${i.product_id}, 1)">+</button>
        <button class="action-btn archive" onclick="removeFromCart(${i.product_id})">×</button>
        ${formatNumber(i.price * i.quantity)} so'm
      </span>
    </div>
  `).join('') || '<p>Bo\'sh</p>';
  document.getElementById('cartTotal').textContent = formatNumber(total);
  document.getElementById('cartProfit').textContent = formatNumber(profit);
  document.getElementById('sellBtn').disabled = cart.length === 0;
}

async function sellCart() {
  if (cart.length === 0) return;
  const items = cart.map(i => ({ product_id: i.product_id, quantity: i.quantity }));
  try {
    await api('/sales', { method: 'POST', body: JSON.stringify({ items }) });
    cart = [];
    updateCartDisplay();
    loadProductsForSale();
    loadProducts();
    loadOmborStats();
    loadReport();
    alert('Sotuv muvaffaqiyatli amalga oshirildi!');
  } catch (err) {
    alert(err.message);
  }
}

async function loadOmborStats() {
  try {
    const s = await api('/reports/summary');
    document.getElementById('statProducts').textContent = s.total_products;
    document.getElementById('statQuantity').textContent = s.total_quantity;
    document.getElementById('statSold').textContent = s.total_sold;
    document.getElementById('statProfit').textContent = formatNumber(s.total_profit);
    document.getElementById('statTodayProfit').textContent = formatNumber(s.today_profit);
  } catch (err) {
    console.error(err);
  }
}

async function loadOmborProducts() {
  try {
    const list = await api('/products?active_only=false');
    const container = document.getElementById('omborProductList');
    container.innerHTML = list.map(p => `
      <div class="product-item">
        <div>
          <strong>${escapeHtml(p.name)}</strong>
          <p>${formatNumber(p.price)} so'm · ${p.quantity} ${p.unit} · ${p.is_active ? 'Faol' : 'Arxiv'}</p>
        </div>
      </div>
    `).join('') || '<p>Mahsulot yo\'q</p>';
  } catch (err) {
    alert(err.message);
  }
}

async function loadReport() {
  const from = document.getElementById('reportFrom')?.value || new Date().toISOString().slice(0, 10);
  const to = document.getElementById('reportTo')?.value || new Date().toISOString().slice(0, 10);
  try {
    const summary = await api('/reports/summary');
    document.getElementById('reportTodayProfit').textContent = formatNumber(summary.today_profit);
    const top = await api(`/reports/top-products?from_date=${from}&to_date=${to}&limit=20`);
    const table = document.getElementById('topProducts');
    table.innerHTML = top.length ? `
      <table>
        <thead><tr><th>Mahsulot</th><th>Miqdor</th><th>Summa</th><th>Foyda</th></tr></thead>
        <tbody>
          ${top.map(t => `
            <tr>
              <td>${escapeHtml(t.product_name)}</td>
              <td>${t.quantity}</td>
              <td>${formatNumber(t.amount)} so'm</td>
              <td>${formatNumber(t.profit)} so'm</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    ` : '<p>Ma\'lumot yo\'q</p>';
  } catch (err) {
    alert(err.message);
  }
}

function openProductModal(id) {
  document.getElementById('productModalTitle').textContent = id ? 'Mahsulotni tahrirlash' : 'Mahsulot qo\'shish';
  document.getElementById('productId').value = id || '';
  if (id) {
    const p = products.find(x => x.id === id);
    if (p) {
      document.getElementById('productName').value = p.name;
      document.getElementById('productPrice').value = p.price;
      document.getElementById('productCostPrice').value = p.cost_price || 0;
      document.getElementById('productQuantity').value = p.quantity;
      document.getElementById('productUnit').value = p.unit || 'dona';
    }
  } else {
    document.getElementById('productForm').reset();
    document.getElementById('productQuantity').value = 0;
    document.getElementById('productCostPrice').value = 0;
    document.getElementById('productUnit').value = 'dona';
  }
  document.getElementById('productModal').classList.remove('hidden');
}

function closeProductModal() {
  document.getElementById('productModal').classList.add('hidden');
}

async function saveProduct(e) {
  e.preventDefault();
  const id = document.getElementById('productId').value;
  const data = {
    name: document.getElementById('productName').value.trim(),
    price: parseFloat(document.getElementById('productPrice').value) || 0,
    cost_price: parseFloat(document.getElementById('productCostPrice').value) || 0,
    quantity: parseInt(document.getElementById('productQuantity').value) || 0,
    unit: document.getElementById('productUnit').value.trim() || 'dona'
  };
  try {
    if (id) {
      await api(`/products/${id}`, { method: 'PATCH', body: JSON.stringify(data) });
    } else {
      await api('/products', { method: 'POST', body: JSON.stringify(data) });
    }
    closeProductModal();
    loadProducts();
    loadProductsForSale();
    loadOmborStats();
  } catch (err) {
    alert(err.message);
  }
}

function editProduct(id) {
  openProductModal(id);
}

async function archiveProduct(id) {
  if (!confirm('Mahsulotni arxivlashni xohlaysizmi?')) return;
  try {
    await api(`/products/${id}/archive`, { method: 'POST' });
    loadProducts();
  } catch (err) {
    alert(err.message);
  }
}

async function restoreProduct(id) {
  try {
    await api(`/products/${id}/restore`, { method: 'POST' });
    loadProducts();
  } catch (err) {
    alert(err.message);
  }
}

function formatNumber(n) {
  return new Intl.NumberFormat('uz-UZ').format(n);
}

function escapeHtml(s) {
  if (!s) return '';
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}

function debounce(fn, ms) {
  let t;
  return (...args) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), ms);
  };
}
