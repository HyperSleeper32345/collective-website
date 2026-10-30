'use strict';

// Site navigation. The native dialog provides keyboard focus containment.
(() => {
  const menu = document.querySelector('#site-menu');
  const toggle = document.querySelector('.menu-toggle');
  if (!menu || !toggle) return;
  toggle.addEventListener('click', () => {
    menu.showModal();
    toggle.setAttribute('aria-expanded', 'true');
    document.body.classList.add('dialog-open');
  });
  menu.querySelector('[data-close-menu]').addEventListener('click', () => menu.close());
  menu.querySelectorAll('a').forEach(link => link.addEventListener('click', () => menu.close()));
  menu.addEventListener('close', () => {
    toggle.setAttribute('aria-expanded', 'false');
    document.body.classList.remove('dialog-open');
    toggle.focus({ preventScroll: true });
  });
  window.addEventListener('resize', () => {
    if (window.innerWidth > 900 && menu.open) menu.close();
  });
})();

// A quiet reading indicator, shared by long pages and field notes.
(() => {
  const bar = document.querySelector('.reading-progress > span');
  if (!bar) return;
  let queued = false;
  const update = () => {
    const distance = document.documentElement.scrollHeight - window.innerHeight;
    bar.style.width = (distance > 0 ? Math.max(0, Math.min(100, window.scrollY / distance * 100)) : 0) + '%';
    queued = false;
  };
  window.addEventListener('scroll', () => {
    if (!queued) { queued = true; requestAnimationFrame(update); }
  }, { passive: true });
  window.addEventListener('resize', update);
  update();
})();

// Commercial questions are examples, not an automated diagnosis.
(() => {
if (!document.querySelector('#scenario-panel')) return;
const scenarios = {
  profit: [
    { question: 'What does each order leave after the costs of winning and fulfilling it?', examine: 'Product costs, discounts, fulfilment, payment fees, returns and acquisition cost.', work: 'Reprioritising products, offers and campaigns around contribution, with reporting that makes the trade-offs visible.' },
    { question: 'Are your best-selling products also the products worth scaling?', examine: 'Contribution by product, sales mix, stock availability and evidence of repeat purchase.', work: 'Connecting product priorities, merchandising and paid campaigns to the economics of the range.' },
    { question: 'Which costs are rising faster than the value they create?', examine: 'Marketing and service investment, operating costs, return rates and cash timing.', work: 'A clearer cost baseline and a focused plan for where investment should continue, change or stop.' }
  ],
  acquisition: [
    { question: 'What can the business afford to pay for its next customer?', examine: 'First-order contribution before acquisition, evidence of repeat purchase and cash timing.', work: 'Agreeing a commercially grounded acquisition target, then aligning campaigns and the purchase journey around it.' },
    { question: 'Where does qualified demand turn into a lost purchase?', examine: 'The ad promise, audience, landing page, product information, checkout friction and measurement quality.', work: 'Coordinated creative, targeting, landing-page and store improvements, prioritised around the constraint.' },
    { question: 'Is more spend bringing better customers, or just more orders?', examine: 'Customer cohorts, new-customer mix, returns and repeat purchase alongside the related costs.', work: 'Campaign and offer decisions informed by the customers the business can profitably serve.' }
  ],
  retention: [
    { question: 'What gives this customer a reason to come back?', examine: 'Purchase intervals, replenishment patterns, the product range and customer segments.', work: 'Relevant email journeys, campaigns and product priorities grounded in actual purchase behaviour.' },
    { question: 'What happens after the first order?', examine: 'The fulfilment experience, post-purchase communication, product use and customer-service feedback.', work: 'Connecting the post-purchase experience with timely, useful communication and an appropriate next offer.' },
    { question: 'Where is the repeat-purchase opportunity in your existing customers?', examine: 'Purchase cohorts, product combinations, engagement history and the quality of customer data.', work: 'A focused retention programme with meaningful segments and a way to measure its contribution.' }
  ]
};
let activeScenario = 'profit';
let questionIndex = 0;
const scenarioTabs = [...document.querySelectorAll('[data-scenario]')];
const scenarioPanel = document.querySelector('#scenario-panel');
function renderQuestion() {
  const item = scenarios[activeScenario][questionIndex];
  document.querySelector('#commercial-question').textContent = item.question;
  document.querySelector('#examine-copy').textContent = item.examine;
  document.querySelector('#work-copy').textContent = item.work;
  document.querySelector('#question-count').textContent = String(questionIndex + 1).padStart(2, '0') + ' / 03';
}
function selectScenario(button, focus) {
  activeScenario = button.dataset.scenario;
  questionIndex = 0;
  scenarioTabs.forEach(tab => { const selected = tab === button; tab.setAttribute('aria-selected', String(selected)); tab.tabIndex = selected ? 0 : -1; });
  scenarioPanel.setAttribute('aria-labelledby', button.id);
  renderQuestion();
  if (focus) button.focus();
}
scenarioTabs.forEach((button, index) => {
  button.addEventListener('click', () => selectScenario(button, false));
  button.addEventListener('keydown', event => {
    let target;
    if (event.key === 'ArrowRight' || event.key === 'ArrowDown') target = (index + 1) % scenarioTabs.length;
    if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') target = (index - 1 + scenarioTabs.length) % scenarioTabs.length;
    if (event.key === 'Home') target = 0;
    if (event.key === 'End') target = scenarioTabs.length - 1;
    if (target !== undefined) { event.preventDefault(); selectScenario(scenarioTabs[target], true); }
  });
});
document.querySelector('#question-next').addEventListener('click', () => { questionIndex = (questionIndex + 1) % 3; renderQuestion(); });
document.querySelector('#question-prev').addEventListener('click', () => { questionIndex = (questionIndex + 2) % 3; renderQuestion(); });

})();

// First-touch attribution for this visit, ported from the previous site's main.js
// (same sessionStorage key, same allowlist). The entry page and the first external
// referrer are kept; the UTMs and click ids of the most recent tagged landing replace
// earlier ones, so an enquiry sent pages later still carries where the visitor came from.
(() => {
  const TRACKING_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'gclid', 'fbclid'];
  const KEY = 'collective_attribution';
  const read = () => {
    try { return JSON.parse(sessionStorage.getItem(KEY)) || null; } catch { return null; }
  };
  window.CollectiveAttribution = Object.freeze({ read });
  const params = new URLSearchParams(window.location.search);
  const found = {};
  let hasTracking = false;
  for (const key of TRACKING_KEYS) {
    const value = params.get(key);
    if (value) { found[key] = value.slice(0, 200); hasTracking = true; }
  }
  const current = read();
  if (current && !hasTracking) return;
  let referrer = '';
  try {
    if (document.referrer && new URL(document.referrer).host !== window.location.host) referrer = document.referrer.slice(0, 500);
  } catch { referrer = ''; }
  const next = {
    tracking: found,
    referrer: referrer || (current && current.referrer) || '',
    entry_page: (current && current.entry_page) || window.location.pathname
  };
  try { sessionStorage.setItem(KEY, JSON.stringify(next)); } catch { /* storage unavailable */ }
})();
