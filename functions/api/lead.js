// Collective enquiry endpoint, a Cloudflare Pages Function.
//
// Receives the /contact enquiry form, validates it, and records one lead in
// the one lead store by calling public.ingest_collective_lead() over the
// Supabase REST API with the publishable key, which PostgREST runs as the
// anon role. That function is SECURITY DEFINER,
// hard-codes the Collective client, honours the honeypot and calls
// public.ingest_lead, which writes hyperpipe.leads. The anon role may execute
// the wrapper and nothing else: it cannot execute ingest_lead and it cannot
// read any lead. No service-role key exists in this project.
//
// This is the Cloudflare twin of the Stratosphere website's api/lead.js, with
// the same wrapper shape, the same honeypot field and the same 503 rule: when
// the two environment values are unset the endpoint says it is not connected
// rather than accepting a lead it cannot record.
//
// Environment (Cloudflare Pages project settings, never in the repo):
//   SUPABASE_URL              the project URL
//   SUPABASE_PUBLISHABLE_KEY  the project's publishable key (sb_publishable_).
//   The legacy JWT anon key was disabled on the project on 2 Sep 2026, so the
//   key goes in the apikey header only, never as a bearer token.
//
// No dependencies. The Workers runtime provides fetch, Request and Response.

const RPC = 'ingest_collective_lead';
const LEAD_SOURCE = 'website';
const LEAD_CAMPAIGN = 'COLL-SITE-CONTACT';
const FALLBACK = 'Please email david@wearecollective.com.au.';

const LIMITS = {
  name: 120,
  email: 200,
  phone: 40,
  message: 4000,
  url: 500,
  utmValue: 200,
  company: 160,
  context: 400
};

// The v5 contact form's structured fields. They travel under one "enquiry" key, so
// ingest_lead keeps them in raw_payload and leaves product_interest_code alone.
const ENQUIRY_KEYS = [
  'interest', 'business_model', 'developer_business', 'developer_ambition', 'developer_pipeline'
];

const TRACKING_KEYS = [
  'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
  'gclid', 'fbclid'
];

// Naive per-isolate throttle. Cloudflare may run many isolates, so this is a
// speed bump against a single noisy client, not a guarantee.
const WINDOW_MS = 10 * 60 * 1000;
const MAX_PER_WINDOW = 5;
const seen = new Map();

function throttled(ip) {
  if (!ip) return false;
  const now = Date.now();
  const hits = (seen.get(ip) || []).filter(function (t) { return now - t < WINDOW_MS; });
  hits.push(now);
  seen.set(ip, hits);
  if (seen.size > 5000) seen.clear();
  return hits.length > MAX_PER_WINDOW;
}

// Strip C0 and C1 control characters, keeping newline, carriage return and tab.
const CONTROL_CHARS = /[\u0000-\u0008\u000B-\u000C\u000E-\u001F\u007F-\u009F]/g;

function clean(value, max) {
  if (typeof value !== 'string') return '';
  return value.replace(CONTROL_CHARS, '').trim().slice(0, max);
}

function looksLikeEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(value);
}

function looksLikePhone(value) {
  const digits = value.replace(/\D/g, '');
  return digits.length >= 6 && digits.length <= 20 && /^[0-9+()\-.\s]+$/.test(value);
}

function json(status, body) {
  return new Response(JSON.stringify(body), {
    status: status,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Cache-Control': 'no-store',
      'X-Robots-Tag': 'noindex'
    }
  });
}

// hyperpipe.v_cvr matches a lead to a page by the path of landing_page_url, so
// the host comes from the request and the path from the form.
function pageUrl(request, page) {
  const origin = new URL(request.url).origin;
  let path = clean(page, LIMITS.url);
  if (!path) return origin + '/';
  if (/^https?:\/\//i.test(path)) {
    try { path = new URL(path).pathname; } catch (e) { path = '/'; }
  }
  if (path.charAt(0) !== '/') path = '/' + path;
  return (origin + path).slice(0, LIMITS.url);
}

// A referrer is kept only when it names another host: a same-site referrer is
// the site's own navigation, not where the visitor came from.
function referrerUrl(request, given) {
  const value = clean(given, LIMITS.url);
  if (!value) return '';
  try {
    if (new URL(value).host === new URL(request.url).host) return '';
  } catch (e) {
    return '';
  }
  return value;
}

// The wrapper returns the new lead's uuid, or null when the honeypot was
// filled. PostgREST hands a scalar return back as the whole response body.
async function ingestLead(url, key, payload) {
  const endpoint = url.replace(/\/+$/, '') + '/rest/v1/rpc/' + RPC;
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'apikey': key,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ p_payload: payload })
  });

  if (!response.ok) {
    const detail = await response.text();
    console.error('lead: Supabase ingest failed', response.status, detail.slice(0, 500));
    return { ok: false, id: null };
  }

  const text = (await response.text()).trim();
  let id = null;
  if (text && text !== 'null') {
    try {
      const parsed = JSON.parse(text);
      if (typeof parsed === 'string') id = parsed;
    } catch (e) {
      id = null;
    }
  }
  return { ok: true, id: id };
}

export async function onRequestPost(context) {
  const request = context.request;
  const env = context.env || {};

  const url = env.SUPABASE_URL;
  const key = env.SUPABASE_PUBLISHABLE_KEY;
  if (!url || !key) {
    return json(503, { ok: false, error: 'The enquiry form is not connected yet. ' + FALLBACK });
  }

  const type = request.headers.get('Content-Type') || '';
  if (type.indexOf('application/json') === -1) {
    return json(415, { ok: false, error: 'The enquiry could not be read. ' + FALLBACK });
  }

  const raw = await request.text();
  if (raw.length > 64 * 1024) {
    return json(413, { ok: false, error: 'The enquiry is too long. ' + FALLBACK });
  }

  let body = null;
  try { body = JSON.parse(raw); } catch (e) { body = null; }
  if (!body || typeof body !== 'object' || Array.isArray(body)) {
    return json(400, { ok: false, error: 'The enquiry could not be read. ' + FALLBACK });
  }

  // A filled honeypot is answered exactly like a success and written nowhere,
  // so a bot learns nothing. The wrapper refuses it as well.
  if (clean(body.company_website, 200)) return json(200, { ok: true });

  if (throttled(request.headers.get('CF-Connecting-IP') || '')) {
    return json(429, { ok: false, error: 'Too many enquiries from this connection. Please try again shortly.' });
  }

  const name = clean(body.name, LIMITS.name);
  const email = clean(body.email, LIMITS.email);
  const phone = clean(body.phone, LIMITS.phone);
  const message = clean(body.message, LIMITS.message);

  const errors = {};
  if (!name) errors.name = 'Please enter your name.';
  if (!email || !looksLikeEmail(email)) errors.email = 'Please enter a valid email address.';
  if (phone && !looksLikePhone(phone)) errors.phone = 'Please check the phone number.';
  if (!message) errors.message = 'Please tell us a little about what you need.';
  if (Object.keys(errors).length) return json(422, { ok: false, errors: errors });

  const payload = {
    name: name,
    email: email,
    message: message,
    source: LEAD_SOURCE,
    form: 'contact-enquiry',
    landing_page_url: pageUrl(request, body.page),
    user_agent: clean(request.headers.get('User-Agent') || '', LIMITS.url),
    ip_country: clean((request.cf && request.cf.country) || '', 8)
  };
  if (phone) payload.phone = phone;

  // v5 form: the business name is the lead's company; the visitor's own website and
  // the enquiry context are recorded in raw_payload (ingest_lead stores the payload whole).
  const company = clean(body.business, LIMITS.company);
  if (company) payload.company = company;

  const website = clean(body.website, LIMITS.url);
  if (website) payload.website = website;

  const given = body.enquiry && typeof body.enquiry === 'object' && !Array.isArray(body.enquiry)
    ? body.enquiry : {};
  const enquiry = {};
  ENQUIRY_KEYS.forEach(function (k) {
    const value = clean(given[k], LIMITS.context);
    if (value) enquiry[k] = value;
  });
  if (typeof given.investment_acknowledged === 'boolean') {
    enquiry.investment_acknowledged = given.investment_acknowledged;
  }
  if (Object.keys(enquiry).length) payload.enquiry = enquiry;

  const referrer = referrerUrl(request, body.referrer);
  if (referrer) payload.referrer_url = referrer;

  const entry = clean(body.entry_page, LIMITS.url);
  if (entry) payload.entry_page = entry;

  const tracking = body.tracking && typeof body.tracking === 'object' && !Array.isArray(body.tracking)
    ? body.tracking : {};
  TRACKING_KEYS.forEach(function (k) {
    const value = clean(tracking[k], LIMITS.utmValue);
    if (value) payload[k] = value;
  });
  if (!payload.utm_campaign) payload.campaign = LEAD_CAMPAIGN;

  let result;
  try {
    result = await ingestLead(url, key, payload);
  } catch (e) {
    console.error('lead: Supabase ingest threw', String((e && e.message) || e));
    result = { ok: false, id: null };
  }

  if (!result.ok) {
    return json(502, { ok: false, error: 'The enquiry could not be recorded. ' + FALLBACK });
  }
  return json(200, { ok: true, id: result.id });
}

export async function onRequest() {
  return new Response('Method not allowed', {
    status: 405,
    headers: { 'Allow': 'POST', 'X-Robots-Tag': 'noindex' }
  });
}
