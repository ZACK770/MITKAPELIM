(function () {
  var GA4_ID = 'G-KP8LY60TCH';
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
  if (!document.querySelector('script[src*="gtag/js"]')) {
    var loader = document.createElement('script');
    loader.async = true;
    loader.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA4_ID;
    document.head.appendChild(loader);
    window.gtag('js', new Date());
    window.gtag('config', GA4_ID);
  }
  var push = function (event, payload) {
    window.dataLayer.push(Object.assign({ event: event }, payload || {}));
    window.gtag('event', event, payload || {});
  };
  var pageName = document.title || location.pathname;

  var ready = function (fn) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  };

  ready(function () {
    push('page_view_custom', { page_path: location.pathname, page_title: pageName });

    var plannerTimer = null;
    var plannerStarted = false;
    var readPlanner = function () {
      var text = function (id) {
        var node = document.getElementById(id);
        return node ? node.textContent.trim() : '';
      };
      return {
        room_length: (document.getElementById('roomW') || {}).value || '',
        room_width: (document.getElementById('roomL') || {}).value || '',
        mode: (document.querySelector('#planner .mode.active') || {}).textContent || '',
        result_groups: text('groups'),
        result_seats: text('seats'),
        result_storage: text('storage'),
        result_storage_area: text('storageArea')
      };
    };
    var reportPlanner = function (trigger) {
      if (!document.getElementById('planner')) return;
      if (!plannerStarted) {
        plannerStarted = true;
        push('calculator_start', { trigger: trigger });
      }
      clearTimeout(plannerTimer);
      plannerTimer = setTimeout(function () {
        push('calculator_use', Object.assign({ trigger: trigger }, readPlanner()));
      }, 900);
    };
    ['roomW', 'roomL'].forEach(function (id) {
      var input = document.getElementById(id);
      if (input) input.addEventListener('input', function () { reportPlanner(id); });
    });
    document.querySelectorAll('#planner .mode').forEach(function (button) {
      button.addEventListener('click', function () { reportPlanner('mode'); });
    });
    document.querySelectorAll('#planner .stepper button').forEach(function (button) {
      button.addEventListener('click', function () { reportPlanner('stepper'); });
    });

    var form = document.querySelector('#quote-form');
    if (form) {
      var formStarted = false;
      form.addEventListener('input', function () {
        if (formStarted) return;
        formStarted = true;
        push('form_start', { form_id: 'quote-form' });
      });
      var status = document.querySelector('#form-status');
      var submitButton = document.querySelector('#server-submit');
      if (submitButton) {
        submitButton.addEventListener('click', function () {
          var data = new FormData(form);
          push('form_submit_attempt', {
            form_id: 'quote-form',
            project_type: String(data.get('project') || ''),
            bench_quantity: String(data.get('benchQuantity') || '')
          });
          if (!status) return;
          var seen = status.textContent;
          var poll = setInterval(function () {
            if (status.textContent === seen) return;
            clearInterval(poll);
            var success = status.textContent.indexOf('נשלח') !== -1;
            push(success ? 'generate_lead' : 'form_submit_error', {
              form_id: 'quote-form',
              message: status.textContent
            });
          }, 400);
          setTimeout(function () { clearInterval(poll); }, 20000);
        });
      }
    }

    document.addEventListener('click', function (event) {
      var link = event.target.closest && event.target.closest('a[href]');
      if (!link) return;
      var href = link.getAttribute('href') || '';
      if (href.indexOf('wa.me') !== -1) push('contact_click', { channel: 'whatsapp' });
      else if (href.indexOf('tel:') === 0) push('contact_click', { channel: 'phone' });
      else if (href.indexOf('mailto:') === 0) push('contact_click', { channel: 'email' });
      else if (href.indexOf('products/') !== -1 || href.indexOf('/products/') !== -1) push('product_click', { destination: href });
      else if (href.indexOf('projects/') !== -1) push('project_click', { destination: href });
    });

    var depths = [25, 50, 75, 100];
    var fired = {};
    window.addEventListener('scroll', function () {
      var height = document.documentElement.scrollHeight - window.innerHeight;
      if (height <= 0) return;
      var percent = Math.round((window.scrollY / height) * 100);
      depths.forEach(function (depth) {
        if (percent >= depth && !fired[depth]) {
          fired[depth] = true;
          push('scroll_depth', { percent: depth });
        }
      });
    }, { passive: true });
  });
})();
