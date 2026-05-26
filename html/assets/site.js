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

(function () {
  const layout = document.querySelector('.docs-layout');
  const sidebar = layout && layout.querySelector('.sidebar');
  if (!layout || !sidebar) return;

  const storageKey = 'embodiedAiSidebarCollapsed';
  const button = document.createElement('button');
  const icon = document.createElement('span');
  const label = document.createElement('span');

  if (!sidebar.id) sidebar.id = 'site-sidebar-nav';
  button.type = 'button';
  button.className = 'sidebar-toggle';
  button.setAttribute('aria-controls', sidebar.id);
  icon.className = 'sidebar-toggle-icon';
  icon.setAttribute('aria-hidden', 'true');
  label.className = 'sidebar-toggle-label';
  button.append(icon, label);

  function setCollapsed(collapsed) {
    layout.classList.toggle('sidebar-collapsed', collapsed);
    button.setAttribute('aria-expanded', String(!collapsed));
    button.title = collapsed ? '展开左侧目录' : '收起左侧目录';
    icon.textContent = collapsed ? '›' : '‹';
    label.textContent = collapsed ? '展开目录' : '收起目录';
    try {
      localStorage.setItem(storageKey, collapsed ? '1' : '0');
    } catch (error) {
      // localStorage may be unavailable in strict privacy contexts.
    }
  }

  button.addEventListener('click', function () {
    setCollapsed(!layout.classList.contains('sidebar-collapsed'));
  });

  sidebar.prepend(button);
  let shouldCollapse = false;
  try {
    shouldCollapse = localStorage.getItem(storageKey) === '1';
  } catch (error) {
    shouldCollapse = false;
  }
  setCollapsed(shouldCollapse);
})();
