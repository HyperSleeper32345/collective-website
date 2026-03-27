/* ==========================================================================
   COLLECTIVE — main.js
   Mobile menu, services dropdown, smooth scroll, interactions.
   ========================================================================== */

(function () {
  'use strict';

  /* ---------- DOM refs ---------- */
  const hamburger = document.querySelector('.hamburger');
  const navLinks = document.querySelector('.nav-links');
  const dropdown = document.querySelector('.nav-dropdown');
  const dropdownToggle = document.querySelector('.nav-dropdown-toggle');
  const header = document.querySelector('.site-header');

  /* ---------- Mobile menu toggle ---------- */
  if (hamburger && navLinks) {
    hamburger.addEventListener('click', function () {
      hamburger.classList.toggle('active');
      navLinks.classList.toggle('open');
      document.body.style.overflow = navLinks.classList.contains('open') ? 'hidden' : '';
    });

    /* Close mobile menu when a link is clicked */
    navLinks.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        hamburger.classList.remove('active');
        navLinks.classList.remove('open');
        document.body.style.overflow = '';
      });
    });
  }

  /* ---------- Services dropdown ---------- */
  if (dropdown && dropdownToggle) {
    dropdownToggle.addEventListener('click', function (e) {
      e.preventDefault();
      dropdown.classList.toggle('open');
    });

    /* Close dropdown when clicking outside */
    document.addEventListener('click', function (e) {
      if (!dropdown.contains(e.target)) {
        dropdown.classList.remove('open');
      }
    });
  }

  /* ---------- Close mobile menu on resize to desktop ---------- */
  window.addEventListener('resize', function () {
    if (window.innerWidth > 900 && navLinks) {
      hamburger.classList.remove('active');
      navLinks.classList.remove('open');
      document.body.style.overflow = '';
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
