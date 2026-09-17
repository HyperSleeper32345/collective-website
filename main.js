/* ==========================================================================
   COLLECTIVE: main.js
   Mobile menu, dropdowns, smooth scroll, attribution, the enquiry form.
   ========================================================================== */

(function () {
  'use strict';

  /* ---------- DOM refs ---------- */
  const hamburger = document.querySelector('.hamburger');
  const navLinks = document.querySelector('.nav-links');
  const dropdowns = document.querySelectorAll('.nav-dropdown');
  const header = document.querySelector('.site-header');

  /* ---------- Mobile menu toggle ---------- */
  if (hamburger && navLinks) {
    hamburger.addEventListener('click', function () {
      hamburger.classList.toggle('active');
      navLinks.classList.toggle('open');
      var isOpen = navLinks.classList.contains('open');
      document.body.style.overflow = isOpen ? 'hidden' : '';
      document.body.classList.toggle('mobile-menu-open', isOpen);
    });

    /* Close mobile menu when a link is clicked */
    navLinks.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        hamburger.classList.remove('active');
        navLinks.classList.remove('open');
        document.body.style.overflow = '';
        document.body.classList.remove('mobile-menu-open');
        dropdowns.forEach(function (d) { d.classList.remove('open'); });
      });
    });
  }

  /* ---------- Nav dropdowns (generic: Services, Insights) ---------- */
  dropdowns.forEach(function (dropdown) {
    var toggle = dropdown.querySelector('.nav-dropdown-toggle');
    if (!toggle) return;
    toggle.addEventListener('click', function (e) {
      e.preventDefault();
      dropdown.classList.toggle('open');
    });
  });

  /* Close dropdowns when clicking outside */
  document.addEventListener('click', function (e) {
    dropdowns.forEach(function (dropdown) {
      if (!dropdown.contains(e.target)) {
        dropdown.classList.remove('open');
      }
    });
  });

  /* ---------- Close mobile menu on resize to desktop ---------- */
  window.addEventListener('resize', function () {
    if (window.innerWidth > 900 && navLinks) {
      hamburger.classList.remove('active');
      navLinks.classList.remove('open');
      document.body.style.overflow = '';
      document.body.classList.remove('mobile-menu-open');
      dropdowns.forEach(function (d) { d.classList.remove('open'); });
    }
  });

  /* ---------- Smooth scroll for anchor links ---------- */
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      var target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  /* ---------- Attribution: first touch in this visit ----------
     The UTMs, click ids, referrer and entry page of the visit are kept in
     sessionStorage on the first page seen, so an enquiry sent three pages
     later still carries where the visitor came from. */
  var TRACKING_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'gclid', 'fbclid'];
  var ATTR_KEY = 'collective_attribution';

  function readAttribution() {
    try { return JSON.parse(sessionStorage.getItem(ATTR_KEY)) || null; } catch (e) { return null; }
  }

  (function captureAttribution() {
    var params = new URLSearchParams(window.location.search);
    var found = {};
    var hasTracking = false;
    TRACKING_KEYS.forEach(function (k) {
      var v = params.get(k);
      if (v) { found[k] = v.slice(0, 200); hasTracking = true; }
    });
    var current = readAttribution();
    if (current && !hasTracking) return;
    var referrer = '';
    try {
      if (document.referrer && new URL(document.referrer).host !== window.location.host) {
        referrer = document.referrer.slice(0, 500);
      }
    } catch (e) { referrer = ''; }
    var next = {
      tracking: found,
      referrer: referrer || (current && current.referrer) || '',
      entry_page: (current && current.entry_page) || window.location.pathname
    };
    try { sessionStorage.setItem(ATTR_KEY, JSON.stringify(next)); } catch (e) { /* storage off */ }
  })();

  /* ---------- Enquiry form ---------- */
  var form = document.querySelector('[data-enquiry-form]');
  if (form && window.fetch) {
    var status = form.querySelector('.form-status');
    var button = form.querySelector('button[type="submit"]');
    var FIELDS = ['name', 'email', 'phone', 'message'];

    var setError = function (name, text) {
      var input = form.elements[name];
      var error = document.getElementById('enquiry-' + name + '-error');
      if (!input || !error) return;
      if (text) {
        input.setAttribute('aria-invalid', 'true');
        input.setAttribute('aria-describedby', error.id);
        error.textContent = text;
        error.hidden = false;
      } else {
        input.removeAttribute('aria-invalid');
        input.removeAttribute('aria-describedby');
        error.textContent = '';
        error.hidden = true;
      }
    };

    var validate = function () {
      var errors = {};
      var v = function (n) { return (form.elements[n].value || '').trim(); };
      if (!v('name')) errors.name = 'Please enter your name.';
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v('email'))) errors.email = 'Please enter a valid email address.';
      if (v('phone') && !/^[0-9+()\-.\s]{6,40}$/.test(v('phone'))) errors.phone = 'Please check the phone number.';
      if (!v('message')) errors.message = 'Please tell us a little about what you need.';
      return errors;
    };

    var show = function (errors) {
      FIELDS.forEach(function (n) { setError(n, errors[n]); });
      var first = FIELDS.filter(function (n) { return errors[n]; })[0];
      if (first) form.elements[first].focus();
    };

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      status.textContent = '';
      status.removeAttribute('data-state');

      var errors = validate();
      if (Object.keys(errors).length) { show(errors); return; }
      show({});

      var attribution = readAttribution() || {};
      var body = {
        name: form.elements.name.value,
        email: form.elements.email.value,
        phone: form.elements.phone.value,
        message: form.elements.message.value,
        company_website: form.elements.company_website.value,
        page: window.location.pathname,
        referrer: attribution.referrer || '',
        entry_page: attribution.entry_page || '',
        tracking: attribution.tracking || {}
      };

      button.disabled = true;
      button.textContent = 'Sending';

      fetch(form.getAttribute('action'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      }).then(function (response) {
        return response.json().catch(function () { return {}; }).then(function (data) {
          return { status: response.status, data: data };
        });
      }).then(function (result) {
        if (result.status === 200 && result.data.ok) {
          form.reset();
          status.textContent = 'Thank you. Your enquiry has been received and David will reply by email.';
          status.setAttribute('data-state', 'success');
          window.dataLayer = window.dataLayer || [];
          window.dataLayer.push({ event: 'form_submit', form: 'contact-enquiry' });
          return;
        }
        if (result.status === 422 && result.data.errors) { show(result.data.errors); return; }
        status.textContent = result.data.error || 'The enquiry could not be sent. Please email david@wearecollective.com.au.';
        status.setAttribute('data-state', 'error');
      }).catch(function () {
        status.textContent = 'The enquiry could not be sent. Please email david@wearecollective.com.au.';
        status.setAttribute('data-state', 'error');
      }).then(function () {
        button.disabled = false;
        button.textContent = 'Send an Enquiry';
      });
    });
  }

  /* ---------- Subtle header background on scroll ---------- */
  if (header) {
    window.addEventListener('scroll', function () {
      if (window.scrollY > 10) {
        header.style.backgroundColor = 'rgba(10, 10, 15, 0.98)';
      } else {
        header.style.backgroundColor = 'rgba(10, 10, 15, 0.92)';
      }
    }, { passive: true });
  }

})();
