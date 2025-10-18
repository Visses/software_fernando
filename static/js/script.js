// Sidebar toggle active state
document.querySelectorAll('.menu-item').forEach(item => {
  item.addEventListener('click', () => {
    document.querySelectorAll('.menu-item').forEach(i => i.classList.remove('active'));
    item.classList.add('active');
  });
});

// Custom select
const stock = document.getElementById('stockSelect');
stock.addEventListener('click', (e) => {
  stock.classList.toggle('open');
});
stock.querySelectorAll('.option').forEach(opt => {
  opt.addEventListener('click', (e) => {
    e.stopPropagation();
    stock.querySelector('.select-label').textContent = opt.textContent;
    stock.classList.remove('open');
  });
});

// Fechar select ao clicar fora
document.addEventListener('click', (e) => {
  if (!stock.contains(e.target)) stock.classList.remove('open');
});

// Hamburger para mobile
const btn = document.getElementById('btnHamburger');
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('overlay');

btn.addEventListener('click', () => {
  sidebar.classList.toggle('hidden');
  overlay.classList.toggle('show');
});
overlay.addEventListener('click', () => {
  sidebar.classList.add('hidden');
  overlay.classList.remove('show');
});

// Resetar ao voltar pro desktop
window.addEventListener('resize', () => {
  if (window.innerWidth > 900) {
    sidebar.classList.remove('hidden');
    overlay.classList.remove('show');
  }
});

// ESC fecha sidebar e select
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    sidebar.classList.add('hidden');
    overlay.classList.remove('show');
    stock.classList.remove('open');
  }
});



