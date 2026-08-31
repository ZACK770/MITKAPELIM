(function(){
  const apiBase=window.MITKAPELIM_API_URL||'';
  window.mitkapelimApi={
    enabled:Boolean(apiBase),
    async send(path,payload){
      if(!apiBase)return false;
      const response=await fetch(apiBase+path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
      if(!response.ok)throw new Error('API request failed');
      return true;
    },
    async summary(password){
      if(!apiBase)throw new Error('API is not configured');
      const response=await fetch(apiBase+'/api/admin/summary',{headers:{'X-Admin-Password':password}});
      if(!response.ok)throw new Error('Unauthorized');
      return response.json();
    },
    csv(path,password){
      return apiBase+path+'?password='+encodeURIComponent(password);
    }
  };
})();
