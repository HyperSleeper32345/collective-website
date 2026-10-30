// Fixed identity previews for the working copy. The red-bracket wordmark is the default.
(() => {
  const options = {
    plain: { label: 'Secondary / Plain wordmark', asset: 'collective-secondary' },
    framed: { label: 'Primary / Red brackets', asset: 'collective-primary' },
    compact: { label: 'Compact / Framed initial', asset: 'collective-compact' }
  };
  const requested = new URLSearchParams(window.location.search).get('lockup');
  const key = Object.hasOwn(options, requested) ? requested : 'framed';
  const selected = options[key];
  document.querySelectorAll('[data-brand-lockup]').forEach(element => {
    element.className = 'identity-lockup identity-lockup--' + key;
    const image = document.createElement('img');
    image.className = 'identity-artwork';
    image.alt = '';
    const tone = element.dataset.brandTone === 'reverse' ? '-reverse' : '';
    image.src = '/assets/identity/' + selected.asset + tone + '.svg';
    element.replaceChildren(image);
  });
  document.querySelectorAll('[data-study-label]').forEach(element => { element.textContent = selected.label; });
})();
