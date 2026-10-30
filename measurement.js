'use strict';

// Prepared event contract only. No Google, Meta or other external tag is loaded.
// Activation requires an agreed tag/consent configuration at the production host.
(() => {
  const config = window.CollectiveSite || {};
  const permittedEvents = new Set(['cta_click', 'enquiry_start', 'email_draft_prepared', 'generate_lead']);
  const permittedValues = {
    form_id: new Set(['contact_enquiry']),
    enquiry_type: new Set(['growth', 'developer', 'ecommerce', 'project', 'advisory']),
    cta_id: new Set(['contact_email', 'email_draft_open', 'contact', 'ecommerce_partnership', 'developer_partnership']),
    destination_type: new Set(['email', 'internal'])
  };
  let analyticsConsent = false;
  function record(name, values = {}) {
    if (!config.measurementEnabled || !analyticsConsent || config.environment !== 'production' ||
      window.location.origin !== config.productionOrigin || !permittedEvents.has(name)) return;
    const event = { event: name };
    for (const [key, allowed] of Object.entries(permittedValues)) {
      if (allowed.has(values[key])) event[key] = values[key];
    }
    (window.dataLayer = window.dataLayer || []).push(event);
  }
  window.CollectiveMeasurement = Object.freeze({
    record,
    setAnalyticsConsent(granted) { analyticsConsent = granted === true; }
  });
  document.addEventListener('click', event => {
    const link = event.target.closest('a');
    if (!link) return;
    let ctaId = link.dataset.cta;
    const href = link.getAttribute('href') || '';
    if (!ctaId && /^\/contact(?:[/?#]|$)/.test(href)) {
      ctaId = href.includes('enquiry=developer') ? 'developer_partnership' : href.includes('enquiry=partnership') ? 'ecommerce_partnership' : 'contact';
    }
    if (!ctaId && href.startsWith('mailto:')) ctaId = 'contact_email';
    if (ctaId) record('cta_click', { cta_id: ctaId, destination_type: href.startsWith('mailto:') ? 'email' : 'internal' });
  });
})();
