const el=id=>document.getElementById(id);
let n=4,mode="A",plain=false;
const prefix="pino.01.page.";
const draft=i=>localStorage.getItem(prefix+i);
function openPage(i){location.hash="seite-"+i;show(i)}
function show(i){n=i;mode=i===3||i>=35?"B":"A";el("github").hidden=true;el("reader").hidden=false;el("editor").hidden=true;el("sheet").hidden=false;el("msg").textContent="";const p=pages[n-1];el("title").textContent=n<4?["Arbeitsbuch","Inhalt A","Inhalt B"][n-1]:p.key;el("where").textContent=(mode==="A"?"A · SERIENHANDBUCH":"B · DAS VIERTE RAD")+"   /   SEITE "+i+" VON "+pages.length;el("sheet").replaceChildren();const node=document.createElement(plain?"pre":"img");if(plain)node.textContent=draft(i)??p.text;else{node.src="seiten/"+i+".webp";node.alt=p.cap+" · "+p.key}el("sheet").append(node);el("view").textContent=plain?"Originalansicht":"Textansicht";el("back").disabled=[1,4,35].includes(i);el("next").disabled=i===34||i===pages.length;nav();listing()}
function nav() {
  const views = {home: "H", episodes: "E", cast: "C", github: "G"};
  for (const [id, value] of Object.entries(views)) el(id).hidden = mode !== value;
  el("reader").hidden = mode !== "A" && mode !== "B";
  for (const [id, active] of [["homeLink",mode==="H"],["series",mode==="A"],["castLink",mode==="C"],["episode",["B","E"].includes(mode)],["repo",mode==="G"]]) {
    el(id).classList.toggle("active",active);
    if (active) el(id).setAttribute("aria-current","true");
    else el(id).removeAttribute("aria-current");
  }
}
function listing() {
  const list = el("list");
  list.replaceChildren();
  function link(parent, title, page) {
    const a = document.createElement("a");
    a.href = "#seite-" + page;
    a.textContent = title;
    if (page === n) a.setAttribute("aria-current","page");
    parent.append(a);
  }
  const query = el("search").value.trim().toLocaleLowerCase("de");
  if (query) {
    for (const p of pages) {
      if ((p.key + " " + (draft(p.n) ?? p.text)).toLocaleLowerCase("de").includes(query))
        link(list,p.key + " · " + p.n,p.n);
    }
    if (!list.childElementCount) list.textContent = "Keine Treffer.";
    return;
  }
  function group(parent,title,open) {
    const item = document.createElement("details");
    const summary = document.createElement("summary");
    summary.textContent = title;
    item.open = open;
    item.append(summary);
    parent.append(item);
    return item;
  }
  for (const [title,page] of chapters.filter(([k]) => k.startsWith(mode))) {
    if (page === 7) {
      const figures = group(list,"Figuren",n >= 7 && n <= 28);
      link(figures,"Besetzung im Überblick",7);
      cast.forEach(({name,page:start},index) => {
        const end = cast[index+1]?.page ?? 29;
        const item = group(figures,name,n >= start && n < end);
        for (let i = start; i < end; i++) {
          const heading = pages[i-1].text.split("\n").find(line => line.includes(name + " · "));
          link(item,heading?.split(" · ").slice(1).join(" · ") || "Charakterbogen",i);
        }
      });
    } else if (page < 8 || page > 28) {
      link(list,title + " · " + page,page);
    }
  }
}
function route() {
  const page = Number(location.hash.match(/^#seite-(\d+)$/)?.[1]);
  if (page >= 1 && page <= pages.length) { show(page); return; }
  el("search").value = "";
  mode = location.hash === "#figuren" ? "C" : location.hash === "#folgen" ? "E" : location.hash === "#github" ? "G" : "H";
  nav();
}
onhashchange=route;el("search").oninput=listing;el("back").onclick=()=>openPage(n-1);el("next").onclick=()=>openPage(n+1);el("view").onclick=()=>{plain=!plain;show(n)};el("edit").onclick=()=>{el("editor").hidden=false;el("sheet").hidden=true;el("field").value=draft(n)??pages[n-1].text;el("field").focus()};el("cancel").onclick=()=>show(n);el("save").onclick=()=>{localStorage.setItem(prefix+n,el("field").value);plain=true;show(n);el("msg").textContent="Textentwurf in diesem Browser gespeichert."};
el("export").onclick=()=>{const v=pages.filter(p=>draft(p.n)!==null).map(p=>"## Seite "+p.n+" · "+p.key+"\n\n"+draft(p.n));if(!v.length){alert("Keine gespeicherten Textentwürfe vorhanden.");return}const a=document.createElement("a");a.href=URL.createObjectURL(new Blob([v.join("\n\n")],{type:"text/markdown;charset=utf-8"}));a.download="Pino-Textentwuerfe.md";a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)};
el("print").onclick=async()=>{document.querySelector(".printed")?.remove();const block=document.createElement("div");block.className="printed";document.body.append(block);const imgs=[];for(const p of pages){const s=document.createElement("section");if(draft(p.n)!==null){const t=document.createElement("pre");t.textContent=draft(p.n);s.append(t)}else{const im=new Image();im.src="seiten/"+p.n+".webp";s.append(im);imgs.push(im.decode())}block.append(s)}await Promise.all(imgs);window.print()};route();
