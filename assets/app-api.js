(function () {
  const apiBase = window.MITKAPELIM_API_URL || 'https://mitkapelim-api.onrender.com';
  const webhookUrl = 'https://hook.eu2.make.com/j5f2rhugimacqf60yvo7iv6bmvnjea1i';

  async function post(path, payload) {
    const response = await fetch(apiBase + path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!response.ok) throw new Error('API request failed');
    return response.json();
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
    enabled: Boolean(apiBase),
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
      const response = await fetch(apiBase + '/api/admin/summary?password=' + encodeURIComponent(password));
      if (!response.ok) throw new Error('Unauthorized');
      return response.json();
    },
    csv(path, password) {
      return apiBase + path + '?password=' + encodeURIComponent(password);
    }
  };
})();
