/* Google Analytics 4 for wearecollective.com.au.
   Same consent pattern as the Stratosphere site: analytics storage granted,
   every advertising signal denied and ads data redacted, so Google Analytics
   is the only third party a page reaches. The measurement ID lives here and
   nowhere else in the repo; every page loads this file from its head. */
(function(){
  var GA4_ID = 'G-GTJXEGTF0G';

  var dl = window.dataLayer = window.dataLayer || [];
  function gtag(){ dl.push(arguments); }
  window.gtag = window.gtag || gtag;

  var live = /^G-[A-Z0-9]{6,}$/.test(GA4_ID);

  function text(el){
    return ((el.textContent || '').replace(/\s+/g, ' ')).trim().slice(0, 100);
  }

  var collective = window.collective = window.collective || {};

  collective.track = function(name, params){
    if (!name || !live) return;
    var payload = {};
    if (params){
      for (var key in params){
        if (Object.prototype.hasOwnProperty.call(params, key) && params[key] !== '' && params[key] != null){
          payload[key] = params[key];
        }
      }
    }
    try { gtag('event', name, payload); } catch(e){}
  };

  if (live){
    var config = {
      allow_google_signals: false,
      allow_ad_personalization_signals: false
    };
    try { if (/[?&]ga_debug=1/.test(location.search)) config.debug_mode = true; } catch(e){}
    /* Consent defaults must be set before config. */
    gtag('consent', 'default', {
      ad_storage: 'denied',
      ad_user_data: 'denied',
      ad_personalization: 'denied',
      analytics_storage: 'granted'
    });
    gtag('set', 'ads_data_redaction', true);
    gtag('js', new Date());
    gtag('config', GA4_ID, config);
    var tag = document.createElement('script');
    tag.async = true;
    tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(GA4_ID);
    document.head.appendChild(tag);
  }

  /* The site has no form: the enquiry path is the Cal.com booking link and
     the email address, so those clicks are the conversion events. */
  document.addEventListener('click', function(event){
    var target = event.target;
    if (!target || !target.closest) return;
    var el = target.closest('a[href]');
    if (!el) return;
    var href = el.getAttribute('href') || '';
    var params = { link_url: href, link_text: text(el), page_path: location.pathname };
    if (href.indexOf('mailto:') === 0){
      collective.track('email_click', params);
    } else if (href.indexOf('tel:') === 0){
      collective.track('phone_click', params);
    } else if (href.indexOf('cal.com/') !== -1){
      params.cta_label = 'book_strategy_call';
      collective.track('cta_click', params);
    }
  }, true);
})();
