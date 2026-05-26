(function () {
  const input = document.querySelector('[data-search]');
  if (!input) return;
  const cards = Array.from(document.querySelectorAll('[data-card]'));
  input.addEventListener('input', function () {
    const q = input.value.trim().toLowerCase();
    for (const card of cards) {
      const text = card.textContent.toLowerCase();
      card.style.display = !q || text.includes(q) ? '' : 'none';
    }
  });
})();
