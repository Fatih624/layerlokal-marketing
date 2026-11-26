const get = id => document.getElementById(id);
async function api(path, options) {
  const response = await fetch(path, {cache: "no-store", ...options});
  const data = await response.json();
  if (!response.ok) throw Error(data.error || response.statusText);
  return data;
}
async function loadSource() {
  const id = get("sources").value;
  if (!id) return;
  const response = await fetch("/api/quelle?id=" + encodeURIComponent(id), {cache:"no-store"});
  const content = response.ok ? await response.text() : "Quelldatei konnte nicht geladen werden.";
  if (get("sources").value === id) get("sourceText").textContent = content;
}
async function refresh() {
  const data = await api("/api/status");
  get("revision").textContent = data.branch+" · "+data.revision+(data.changed?" · lokale Änderungen":"");
  get("sources").replaceChildren(...Object.entries(data.sources).map(([id,title]) => new Option(title,id)));
  await loadSource();
}
async function monitor() {
  get("pull").disabled=true;
  try {
    for (;;) {
      const job = await api("/api/job");
      get("syncmsg").textContent=job.message;
      if (job.status==="done") {
        sessionStorage.setItem("pino.lastPull",job.message);
        location.reload();
        return;
      }
      if (job.status!=="running") break;
      await new Promise(resolve=>setTimeout(resolve,450));
    }
  } finally {get("pull").disabled=false;}
}
get("sources").onchange=()=>loadSource().catch(e=>get("sourceText").textContent=e.message);
get("pull").onclick=async()=>{
  get("pull").disabled=true;
  try {
    const {token}=await api("/api/session");
    await api("/api/pull",{method:"POST",headers:{"X-Leitstelle":token}});
    await monitor();
  } catch(e) {get("syncmsg").textContent=e.message;get("pull").disabled=false;}
};
(async()=>{
  get("syncmsg").textContent=sessionStorage.getItem("pino.lastPull")||"";
  sessionStorage.removeItem("pino.lastPull");
  await refresh();
  if ((await api("/api/job"))?.status==="running") await monitor();
})().catch(e=>get("syncmsg").textContent=e.message);
