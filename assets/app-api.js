(function () {
  const apiBases = [...new Set([
    window.MITKAPELIM_API_URL,
    window.location.origin,
    'https://mitkapelim-api.onrender.com'
  ].filter(Boolean))];
  const webhookUrl = 'https://hook.eu2.make.com/j5f2rhugimacqf60yvo7iv6bmvnjea1i';

  async function post(path, payload) {
    let lastError;
    for (const base of apiBases) {
      try {
        const response = await fetch(base + path, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (!response.ok) throw new Error('API request failed');
        return response.json();
      } catch (error) {
        lastError = error;
      }
    }
    throw lastError || new Error('API request failed');
  }

  async function sendWebhook(type, data) {
    const record = { ...data, created_at: data.created_at || new Date().toISOString() };
    const response = await fetch(webhookUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type, created_at: record.created_at, source: record.source || 'אתר מתקפלים', data: record })
    });
    if (!response.ok) throw new Error('Webhook request failed');
  }

  window.mitkapelimApi = {
    enabled: apiBases.length > 0,
    async send(path, payload) {
      try {
        await post(path, payload);
      } catch (error) {
        await sendWebhook(path === '/api/leads' ? 'lead' : 'page_view', payload);
      }
      return true;
    },
    async track(payload) {
      return this.send('/api/analytics', payload);
    },
    async summary(password) {
      const response = await fetch(apiBases[0] + '/api/admin/summary?password=' + encodeURIComponent(password));
      if (!response.ok) throw new Error('Unauthorized');
      return response.json();
    },
    async clear(password) {
      const response = await fetch(apiBases[0] + '/api/admin/data?password=' + encodeURIComponent(password), { method: 'DELETE' });
      if (!response.ok) throw new Error('Clear request failed');
      return true;
    },
    csv(path, password) {
      return apiBases[0] + path + '?password=' + encodeURIComponent(password);
    }
  };
})();
