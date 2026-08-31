(function () {
  function createIcon(path) {
    return '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">' + path + '</svg>';
  }

  function mountDock() {
    if (document.querySelector('.social-dock')) return;

    const quoteTarget = document.querySelector('#quote') ? '#quote' : '../index.html#quote';
    const dock = document.createElement('nav');
    dock.className = 'social-dock';
    dock.setAttribute('aria-label', 'דרכי קשר');
    dock.innerHTML = [
      '<a href="https://wa.me/97226206070" target="_blank" rel="noopener" aria-label="שליחת הודעה ב-WhatsApp">' +
        createIcon('<circle cx="12" cy="12" r="8.5"></circle><path d="m8.5 15.5 1.1-2.2a4.9 4.9 0 1 1 1.7 1.7l-2.8.8Z"></path><path d="M9.8 9.3c.2-.4.5-.4.8-.3l.7.5c.2.2.2.4.1.6l-.3.5c.4.7.9 1.2 1.6 1.6l.5-.3c.2-.1.4-.1.6.1l.5.7c.1.3.1.6-.3.8-1 .4-2.3-.4-3.2-1.2s-1.7-2.1-1-3Z"></path>') +
      '</a>',
      '<a href="mailto:info@mitkaplim.co.il" aria-label="שליחת אימייל">' +
        createIcon('<rect x="3.5" y="5.5" width="17" height="13" rx="1.5"></rect><path d="m4.5 7 7.5 5.5L19.5 7"></path>') +
      '</a>',
      '<a href="' + quoteTarget + '" aria-label="פתיחת טופס הצעת מחיר">' +
        createIcon('<path d="M5 5.5h14v10H9l-4 3v-13Z"></path><path d="M8 9h8M8 12h5"></path>') +
      '</a>'
    ].join('');
    document.body.append(dock);
  }

  const style = document.createElement('style');
  style.textContent = [
    '.social-dock{position:fixed;left:18px;bottom:18px;z-index:20;display:flex;flex-direction:column;gap:10px}',
    '.social-dock a{width:52px;height:52px;display:grid;place-items:center;border:1px solid var(--line,rgba(255,255,255,.2));border-radius:50%;background:var(--bg,#0b0c0d);color:var(--ink,#f0f0ed);transition:background .2s ease,border-color .2s ease,color .2s ease,transform .2s ease}',
    '.social-dock svg{width:24px;height:24px;fill:none;stroke:currentColor;stroke-linecap:round;stroke-linejoin:round;stroke-width:1.7}',
    '.social-dock a:hover,.social-dock a:focus-visible{background:var(--lime,var(--gold,#c58a45));border-color:var(--lime,var(--gold,#c58a45));color:#111;transform:translateY(-2px)}',
    '@media(max-width:600px){.social-dock{left:12px;bottom:12px;gap:8px}.social-dock a{width:46px;height:46px}.social-dock svg{width:21px;height:21px}}'
  ].join('');
  document.head.append(style);

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mountDock, { once: true });
  } else {
    mountDock();
  }
})();
