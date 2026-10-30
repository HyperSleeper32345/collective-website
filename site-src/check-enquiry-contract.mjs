// Check the failure modes that could otherwise lose or falsely count an enquiry.
// All responses are local fixtures; this script never contacts the real endpoint.
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import vm from 'node:vm';
import { submitLead, isRecordedLead } from '../lead-client.mjs';

const uuid = '123e4567-e89b-42d3-a456-426614174000';
const payload = { name: 'Local Review', email: 'review@example.com', message: 'Developer founding partnership\nBusiness and pipeline context.', page: '/contact', company_website: '', business: 'Local Review Pty Ltd', website: 'https://example.com', enquiry: { interest: 'Developer founding partnership', developer_business: 'Townhouses, Brisbane' }, referrer: 'https://www.google.com/', entry_page: '/insights/pipeline-velocity', tracking: { utm_source: 'google', gclid: 'abc' } };
let submitted;
const result = await submitLead(payload, { fetcher: async (url, options) => {
  assert.equal(url, '/api/lead');
  assert.equal(options.method, 'POST');
  assert.equal(options.credentials, 'same-origin');
  submitted = JSON.parse(options.body);
  return new Response(JSON.stringify({ ok: true, id: uuid }), { status: 200 });
}});
assert.deepEqual(submitted, payload);
assert.deepEqual(result, { recorded: true });
for (const body of [{ok:true}, {ok:true,id:null}, {ok:true,id:'not-a-record'}, {ok:false,id:uuid}]) {
  assert.equal(isRecordedLead({ok:true},body),false);
  await assert.rejects(submitLead(payload,{fetcher:async()=>new Response(JSON.stringify(body),{status:200})}), /could not confirm/);
}
await assert.rejects(submitLead(payload,{fetcher:async()=>new Response('unavailable',{status:503})}),/could not confirm/);
await assert.rejects(submitLead(payload,{fetcher:async()=>new Response('{}',{status:429})}),/wait a little/);
await assert.rejects(submitLead(payload,{fetcher:async()=>{throw new TypeError('offline');}}),/could not confirm/);
await assert.rejects(submitLead({...payload,message:'x'.repeat(4001)}),/shorten/);

const code=await readFile(new URL('../measurement.js',import.meta.url),'utf8');
function measurement({environment='production',origin='https://wearecollective.com.au',enabled=true}={}) {
  const window={CollectiveSite:{environment,productionOrigin:'https://wearecollective.com.au',measurementEnabled:enabled},location:{origin}};
  vm.runInNewContext(code,{window,document:{addEventListener(){}}});
  return window;
}
let m=measurement();
m.CollectiveMeasurement.record('generate_lead',{form_id:'contact_enquiry'});
assert.equal(m.dataLayer,undefined,'Consent is required before queuing analytics.');
m.CollectiveMeasurement.setAnalyticsConsent(true);
m.CollectiveMeasurement.record('generate_lead',{form_id:'contact_enquiry',enquiry_type:'developer',email:'private@example.com',message:'Private message',link_url:'mailto:private@example.com?body=private',id:uuid});
assert.equal(JSON.stringify(m.dataLayer),JSON.stringify([{event:'generate_lead',form_id:'contact_enquiry',enquiry_type:'developer'}]));
m.CollectiveMeasurement.record('unknown_event',{form_id:'contact_enquiry'});
assert.equal(m.dataLayer.length,1);
for (const settings of [{environment:'review'},{origin:'https://collective-bracket-study.stratosphere-9776.chatgpt.site'},{enabled:false}]) {
  m=measurement(settings);m.CollectiveMeasurement.setAnalyticsConsent(true);m.CollectiveMeasurement.record('generate_lead',{form_id:'contact_enquiry'});
  assert.equal(m.dataLayer,undefined,'Preview and disabled measurement remain inert.');
}
// The Pages Function maps the v5 fields additively (C-SITE-V5): business to company,
// website and the enquiry context into the payload ingest_lead keeps as raw_payload.
const { onRequestPost } = await import('../functions/api/lead.js');
let rpc;
const realFetch = globalThis.fetch;
globalThis.fetch = async (url, options) => { rpc = { url, body: JSON.parse(options.body) }; return new Response(JSON.stringify(uuid), { status: 200 }); };
function post(body) {
  return onRequestPost({ env: { SUPABASE_URL: 'https://project.example', SUPABASE_PUBLISHABLE_KEY: 'sb_publishable_fixture' },
    request: new Request('https://wearecollective.com.au/api/lead', { method: 'POST', headers: { 'Content-Type': 'application/json', 'CF-Connecting-IP': String(Math.random()) }, body: JSON.stringify(body) }) });
}
let reply = await post({ ...payload, enquiry: { ...payload.enquiry, interest: 'x'.repeat(500), unknown: 'dropped' }, tracking: { ...payload.tracking, email: 'private@example.com' } });
assert.equal(reply.status, 200);
assert.deepEqual(await reply.json(), { ok: true, id: uuid });
assert.match(rpc.url, /\/rest\/v1\/rpc\/ingest_collective_lead$/);
const sent = rpc.body.p_payload;
assert.equal(sent.company, 'Local Review Pty Ltd');
assert.equal(sent.website, 'https://example.com');
assert.deepEqual(Object.keys(sent.enquiry).sort(), ['developer_business', 'interest']);
assert.equal(sent.enquiry.interest.length, 400);
assert.equal(sent.interest, undefined, 'interest stays out of product_interest_code');
assert.equal(sent.landing_page_url, 'https://wearecollective.com.au/contact');
assert.equal(sent.referrer_url, 'https://www.google.com/');
assert.equal(sent.entry_page, '/insights/pipeline-velocity');
assert.equal(sent.utm_source, 'google');
assert.equal(sent.gclid, 'abc');
assert.equal(sent.email, 'review@example.com');
assert.equal(JSON.stringify(sent).includes('private@example.com'), false, 'tracking keeps only the allowlist');
rpc = undefined;
reply = await post({ ...payload, company_website: 'https://bot.example' });
assert.deepEqual(await reply.json(), { ok: true });
assert.equal(rpc, undefined, 'the honeypot writes nothing');
globalThis.fetch = realFetch;

console.log('Passed: receipt-based lead success, preserved payload, spam/missing-ID/server/network failures, message limit, consent/host guards, analytics field allowlist, and /api/lead field mapping (company, website, enquiry context, attribution, honeypot). No external requests.');
