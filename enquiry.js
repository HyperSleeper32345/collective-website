'use strict';

(() => {
  const form = document.querySelector('#enquiry-form');
  if (!form) return;
  const fields = form.elements;
  const founding = document.querySelector('#founding-context');
  const developer = document.querySelector('#developer-context');
  const model = document.querySelector('#business-model-context');
  const ready = document.querySelector('#enquiry-ready');
  const received = document.querySelector('#enquiry-received');
  const draft = document.querySelector('#enquiry-draft');
  const open = document.querySelector('#open-email-draft');
  const status = document.querySelector('#copy-status');
  const error = document.querySelector('#enquiry-error');
  const fallback = document.querySelector('#email-fallback');
  const submit = form.querySelector('button[type="submit"]');
  const config = window.CollectiveSite || {};
  // A production artifact viewed on a preview hostname must never create LIVE leads.
  // The one exception is this Pages project's own preview host (leadTestHost), where
  // only an enquiry whose name starts with TEST is sent; any other name prepares the
  // email draft, so a preview never records a real prospect.
  const host = window.location.hostname;
  const testHost = typeof config.leadTestHost === 'string' && config.leadTestHost !== '' &&
    window.location.protocol === 'https:' &&
    (host === config.leadTestHost || host.endsWith('.' + config.leadTestHost));
  const apiMode = config.enquiryMode === 'api' && config.environment === 'production' &&
    (window.location.origin === config.productionOrigin || testHost);
  let sending = false;
  let started = false;
  const interestIds = {
    'A growth conversation': 'growth', 'Developer founding partnership': 'developer',
    'Ecommerce founding partnership': 'ecommerce', 'A defined project': 'project',
    'Advisory and commercial direction': 'advisory'
  };
  function track(name) {
    window.CollectiveMeasurement?.record(name, { form_id: 'contact_enquiry', enquiry_type: interestIds[fields.interest.value] || 'growth' });
  }
  function updateInterest() {
    const ecommerceSelected = fields.interest.value === 'Ecommerce founding partnership';
    const developerSelected = fields.interest.value === 'Developer founding partnership';
    founding.hidden = !ecommerceSelected;
    fields.investment.required = ecommerceSelected;
    fields.investment.disabled = !ecommerceSelected;
    if (!ecommerceSelected) fields.investment.checked = false;
    developer.hidden = !developerSelected;
    developer.disabled = !developerSelected;
    fields.developer_business.required = developerSelected;
    model.hidden = ecommerceSelected || developerSelected;
    fields.business_model.disabled = model.hidden;
  }
  const enquiry = new URLSearchParams(window.location.search).get('enquiry');
  if (enquiry === 'partnership') fields.interest.value = 'Ecommerce founding partnership';
  if (enquiry === 'developer') fields.interest.value = 'Developer founding partnership';
  updateInterest();
  fields.interest.addEventListener('change', updateInterest);
  if (apiMode) {
    form.querySelector('[data-submit-label]').textContent = 'Send my enquiry';
    form.querySelector('[data-submit-note]').textContent = 'Your enquiry goes directly to Collective.';
    document.querySelector('[data-enquiry-explainer]').textContent = 'Use the prompts to send David some context. He will review the enquiry and respond about the next step.';
  }
  form.addEventListener('input', event => {
    if (event.target.setCustomValidity) event.target.setCustomValidity('');
    if (!started) { started = true; track('enquiry_start'); }
  });
  function valid() {
    for (const input of form.querySelectorAll('input, textarea, select')) {
      if (input.disabled || input.closest('fieldset[disabled]')) continue;
      if ((input.type === 'text' || input.tagName === 'TEXTAREA') && input.required) {
        input.setCustomValidity(input.value.trim() ? '' : 'Please complete this field.');
        if (input.name === 'message' && input.value.trim().length < 10) input.setCustomValidity('Please add a little more context.');
      }
      if (!input.reportValidity()) return false;
    }
    return true;
  }
  function enquiryDetails() {
    const lines = ['Enquiry: ' + fields.interest.value, 'Business: ' + fields.business.value.trim()];
    if (fields.website.value.trim()) lines.push('Website: ' + fields.website.value.trim());
    if (!model.hidden && fields.business_model.value) lines.push('Business model: ' + fields.business_model.value);
    if (!developer.hidden) {
      lines.push('', 'Development business and markets:', fields.developer_business.value.trim());
      if (fields.developer_ambition.value.trim()) lines.push('', 'Brand ambition:', fields.developer_ambition.value.trim());
      if (fields.developer_pipeline.value.trim()) lines.push('', 'Pipeline, timing and relationship:', fields.developer_pipeline.value.trim());
    }
    lines.push('', 'What I’d like to change:', fields.message.value.trim());
    if (!founding.hidden) lines.push('', 'I understand the founding ecommerce partnership is AUD $10,000 per month + GST for agreed scope, with implementation, advertising and agreed third-party costs additional.');
    return lines.join('\n');
  }
  // The structured enquiry fields, recorded in the lead's raw payload by /api/lead.
  function enquiryContext() {
    const context = { interest: fields.interest.value };
    if (!model.hidden && fields.business_model.value) context.business_model = fields.business_model.value;
    if (!developer.hidden) {
      for (const name of ['developer_business', 'developer_ambition', 'developer_pipeline']) {
        if (fields[name].value.trim()) context[name] = fields[name].value.trim();
      }
    }
    if (!founding.hidden) context.investment_acknowledged = fields.investment.checked;
    return context;
  }
  function prepareDraft() {
    if (!valid()) return;
    const body = ['Hi David,', '', 'Name: ' + fields.name.value.trim(), 'Email: ' + fields.email.value.trim(), '', enquiryDetails(), '', 'Thanks,', fields.name.value.trim()].join('\n');
    draft.value = body;
    open.href = 'mailto:david@wearecollective.com.au?subject=' + encodeURIComponent('Collective enquiry: ' + fields.business.value.trim()) + '&body=' + encodeURIComponent(body);
    form.hidden = true;
    ready.hidden = false;
    status.textContent = '';
    track('email_draft_prepared');
    ready.focus();
  }
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (sending || !valid()) return;
    if (!apiMode || (testHost && !/^test/i.test(fields.name.value.trim()))) { prepareDraft(); return; }
    sending = true;
    submit.disabled = true;
    form.setAttribute('aria-busy', 'true');
    submit.querySelector('[data-submit-label]').textContent = 'Sending…';
    error.hidden = true;
    fallback.hidden = true;
    try {
      const { submitLead } = await import('/lead-client.mjs');
      const attribution = window.CollectiveAttribution?.read() || {};
      await submitLead({
        name: fields.name.value.trim(), email: fields.email.value.trim(),
        message: enquiryDetails(), company_website: fields.company_website.value,
        page: '/contact',
        business: fields.business.value.trim(), website: fields.website.value.trim(),
        enquiry: enquiryContext(),
        referrer: attribution.referrer || '', entry_page: attribution.entry_page || '',
        tracking: attribution.tracking || {}
      });
      track('generate_lead');
      form.reset();
      form.hidden = true;
      received.hidden = false;
      received.focus();
    } catch (problem) {
      error.textContent = problem.message || 'We could not confirm receipt. Please email David directly.';
      error.hidden = false;
      fallback.hidden = false;
    } finally {
      sending = false;
      submit.disabled = false;
      form.removeAttribute('aria-busy');
      submit.querySelector('[data-submit-label]').textContent = 'Send my enquiry';
    }
  });
  fallback.addEventListener('click', prepareDraft);
  document.querySelector('#edit-enquiry').addEventListener('click', () => {
    ready.hidden = true;
    form.hidden = false;
    fields.message.focus();
  });
  document.querySelector('#copy-enquiry').addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(draft.value);
      status.textContent = 'Enquiry copied. Paste it into your email to David.';
    } catch {
      draft.focus(); draft.select();
      status.textContent = 'Select and copy the enquiry above, then paste it into your email.';
    }
  });
  window.addEventListener('pagehide', () => {
    form.reset(); draft.value = ''; open.href = 'mailto:david@wearecollective.com.au';
    ready.hidden = true; received.hidden = true; form.hidden = false; status.textContent = '';
    error.hidden = true; fallback.hidden = true; updateInterest();
  });
  submit.disabled = false;
})();
