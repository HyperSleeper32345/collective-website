'use strict';

// Measurement (C-SITE-V5-2). One GTM container (site-config.js gtmContainerId) carries
// GA4 G-GTJXEGTF0G and the Meta pixel. It loads only at the production origin, or on
// this Pages project's preview host (leadTestHost), where it loads the container's
// preview environment. Consent stays as before: analytics granted, every advertising
// signal denied and ads data redacted. Only the four events below, with only the
// allowlisted values, reach the data layer: no personal field and no mailto URL.
(() => {
  const config = window.CollectiveSite || {};
  const permittedEvents = new Set(['cta_click', 'enquiry_start', 'email_draft_prepared', 'generate_lead']);
  const permittedValues = {
    form_id: new Set(['contact_enquiry']),
    enquiry_type: new Set(['growth', 'developer', 'ecommerce', 'project', 'advisory']),
    cta_id: new Set(['contact_email', 'email_draft_open', 'contact', 'ecommerce_partnership', 'developer_partnership']),
    destination_type: new Set(['email', 'internal'])
  };
  const location = window.location || {};
  const host = location.hostname || '';
  const testHost = typeof config.leadTestHost === 'string' && config.leadTestHost !== '' &&
    location.protocol === 'https:' && (host === config.leadTestHost || host.endsWith('.' + config.leadTestHost));
  const active = config.measurementEnabled === true && config.environment === 'production' &&
    (location.origin === config.productionOrigin || testHost);
  let analyticsConsent = active && config.analyticsConsent === 'granted';
  function record(name, values = {}) {
    if (!active || !analyticsConsent || !permittedEvents.has(name)) return;
    const event = { event: name };
    for (const [key, allowed] of Object.entries(permittedValues)) {
      if (allowed.has(values[key])) event[key] = values[key];
    }
    (window.dataLayer = window.dataLayer || []).push(event);
  }
  window.CollectiveMeasurement = Object.freeze({
    record,
    setAnalyticsConsent(granted) { analyticsConsent = active && granted === true; }
  });
  if (active && /^GTM-[A-Z0-9]+$/.test(config.gtmContainerId || '')) {
    const dataLayer = window.dataLayer = window.dataLayer || [];
    function gtag() { dataLayer.push(arguments); }
    // Consent defaults precede the container, so every tag reads them on its first fire.
    gtag('consent', 'default', {
      ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied',
      analytics_storage: analyticsConsent ? 'granted' : 'denied'
    });
    gtag('set', 'ads_data_redaction', true);
    dataLayer.push({ 'gtm.start': Date.now(), event: 'gtm.js' });
    let src = 'https://www.googletagmanager.com/gtm.js?id=' + encodeURIComponent(config.gtmContainerId);
    const environment = config.gtmTestEnvironment;
    if (testHost && environment && environment.auth && environment.preview) {
      src += '&gtm_auth=' + encodeURIComponent(environment.auth) + '&gtm_preview=' + encodeURIComponent(environment.preview) + '&gtm_cookies_win=x';
    }
    const tag = document.createElement('script');
    tag.async = true;
    tag.src = src;
    document.head.appendChild(tag);
  }
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
