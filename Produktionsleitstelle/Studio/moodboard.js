// Moodboard: Inspiration aus dem Internet sammeln.
// Die Bilder lädt der lokale Leitstellen-Server herunter und speichert sie unter Studio/moodboard/.
(() => {
  const $ = id => document.getElementById(id);
  const AREAS = [
    {id: "figuren", name: "Figuren", color: "#bb602f"},
    {id: "orte", name: "Schauplätze", color: "#28523f"},
    {id: "licht", name: "Licht & Farbe", color: "#c4952a"},
    {id: "bewegung", name: "Animation", color: "#55689d"},
    {id: "marketing", name: "Marketing", color: "#923f27"},
  ];
  const SOURCES = [
    ["Pinterest", q => "https://www.pinterest.de/search/pins/?q=" + q],
    ["Behance", q => "https://www.behance.net/search/projects?search=" + q],
    ["ArtStation", q => "https://www.artstation.com/search?sort_by=relevance&query=" + q],
    ["Dribbble", q => "https://dribbble.com/search/" + q],
    ["Google Bilder", q => "https://www.google.com/search?tbm=isch&q=" + q],
    ["Openverse · frei lizenziert", q => "https://openverse.org/search/image?q=" + q],
    ["Wikimedia Commons", q => "https://commons.wikimedia.org/w/index.php?title=Special:MediaSearch&type=image&search=" + q],
  ];
  const IDEAS = ["Bilderbuch Nachbarschaft Aquarell", "Werkstatt warmes Licht Illustration", "Stop-Motion Figuren Kinder",
                 "Hinterhof Fest Lichterkette", "3D Druck bunte Spielzeuge", "Kinderserie Farbpalette"];
  const area = id => AREAS.find(a => a.id === id) || AREAS[0];
  const state = {pins: [], area: "alle", tag: null, find: "", current: null, busy: false};
  const palettes = new Map();

  async function api(action, body) {
    const {token} = await (await fetch("/api/session", {cache: "no-store"})).json();
    const response = await fetch("/api/moodboard/" + action, {
      method: "POST", cache: "no-store",
      headers: {"Content-Type": "application/json", "X-Leitstelle": token},
      body: JSON.stringify(body),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw Error(data.error || "Die Leitstelle hat nicht geantwortet.");
    return data;
  }

  async function load() {
    try {
      const response = await fetch("moodboard/moodboard.json", {cache: "no-store"});
      state.pins = response.ok ? (await response.json()).pins || [] : [];
    } catch { state.pins = []; }
    render();
  }

  // ---- Farbpalette aus dem Bild (lokale Bilder, daher ohne CORS-Probleme)
  function palette(img, count = 5) {
    const size = 48, canvas = document.createElement("canvas");
    canvas.width = canvas.height = size;
    const ctx = canvas.getContext("2d", {willReadFrequently: true});
    ctx.drawImage(img, 0, 0, size, size);
    const data = ctx.getImageData(0, 0, size, size).data, buckets = new Map();
    for (let i = 0; i < data.length; i += 4) {
      if (data[i + 3] < 128) continue;
      const key = (data[i] >> 4) << 8 | (data[i + 1] >> 4) << 4 | data[i + 2] >> 4;
      const b = buckets.get(key) || {n: 0, r: 0, g: 0, b: 0};
      b.n++; b.r += data[i]; b.g += data[i + 1]; b.b += data[i + 2];
      buckets.set(key, b);
    }
    const sorted = [...buckets.values()].sort((a, b) => b.n - a.n).map(b => [b.r / b.n, b.g / b.n, b.b / b.n]);
    const picked = [];
    for (const c of sorted) {
      if (picked.every(p => Math.hypot(p[0] - c[0], p[1] - c[1], p[2] - c[2]) > 42)) picked.push(c);
      if (picked.length === count) break;
    }
    return picked.map(c => "#" + c.map(v => Math.round(v).toString(16).padStart(2, "0")).join(""));
  }

  function swatches(target, colors) {
    target.replaceChildren(...colors.map(hex => {
      const s = document.createElement("button");
      s.type = "button"; s.className = "mb-swatch"; s.style.background = hex;
      s.title = hex + " · klicken zum Kopieren";
      s.setAttribute("aria-label", "Farbe " + hex + " kopieren");
      s.onclick = event => {
        event.stopPropagation();
        navigator.clipboard?.writeText(hex);
        s.dataset.copied = "kopiert";
        setTimeout(() => delete s.dataset.copied, 1100);
      };
      return s;
    }));
  }

  function world(visible) {
    const all = visible.flatMap(p => (palettes.get(p.id) || []).slice(0, 3));
    const unique = [];
    for (const hex of all) {
      const rgb = [1, 3, 5].map(i => parseInt(hex.slice(i, i + 2), 16));
      if (unique.every(u => Math.hypot(u.rgb[0] - rgb[0], u.rgb[1] - rgb[1], u.rgb[2] - rgb[2]) > 38)) unique.push({hex, rgb});
      if (unique.length === 12) break;
    }
    swatches($("mbWorld"), unique.map(u => u.hex));
  }

  // ---- Darstellung
  function visiblePins() {
    const find = state.find.toLocaleLowerCase("de");
    return state.pins.filter(p =>
      (state.area === "alle" || p.bereich === state.area) &&
      (!state.tag || p.tags.includes(state.tag)) &&
      (!find || [p.titel, p.notiz, p.quelle, ...p.tags].join(" ").toLocaleLowerCase("de").includes(find)));
  }

  function chip(label, active, onclick, color, count) {
    const b = document.createElement("button");
    b.type = "button"; b.className = "mb-chip"; b.setAttribute("aria-pressed", active);
    if (color) { const dot = document.createElement("i"); dot.style.background = color; b.append(dot); }
    b.append(label);
    if (count !== undefined) { const c = document.createElement("span"); c.textContent = count; b.append(c); }
    b.onclick = onclick;
    return b;
  }

  function render() {
    $("mbAreas").replaceChildren(
      chip("Alle", state.area === "alle", () => { state.area = "alle"; render(); }, null, state.pins.length),
      ...AREAS.map(a => chip(a.name, state.area === a.id, () => { state.area = state.area === a.id ? "alle" : a.id; render(); },
        a.color, state.pins.filter(p => p.bereich === a.id).length)));
    const tags = new Map();
    for (const p of state.pins) for (const t of p.tags) tags.set(t, (tags.get(t) || 0) + 1);
    if (state.tag && !tags.has(state.tag)) state.tag = null;
    $("mbTags").replaceChildren(...[...tags].sort((a, b) => b[1] - a[1]).slice(0, 24).map(([t]) =>
      chip("#" + t, state.tag === t, () => { state.tag = state.tag === t ? null : t; render(); })));

    const visible = visiblePins();
    $("mbBoard").replaceChildren(...visible.map(card));
    $("mbEmpty").hidden = visible.length > 0;
    $("mbFoot").textContent = state.pins.length
      ? `${visible.length} von ${state.pins.length} Bildern · gespeichert in Produktionsleitstelle/Studio/moodboard/ · zum Teilen mit Yasin committen und pushen`
      : "";
    world(visible);
  }

  function card(pin) {
    const a = area(pin.bereich);
    const fig = document.createElement("figure");
    fig.className = "mb-card"; fig.style.setProperty("--area", a.color);
    const open = document.createElement("button");
    open.type = "button"; open.className = "mb-open";
    open.setAttribute("aria-label", (pin.titel || "Inspiration") + " öffnen");
    const img = new Image();
    img.loading = "lazy"; img.decoding = "async"; img.alt = pin.titel || "";
    img.src = "moodboard/" + pin.bild;
    const colors = document.createElement("div");
    colors.className = "mb-swatches";
    img.onload = () => {
      if (!palettes.has(pin.id)) { try { palettes.set(pin.id, palette(img)); } catch { palettes.set(pin.id, []); } }
      swatches(colors, palettes.get(pin.id));
      clearTimeout(render.world); render.world = setTimeout(() => world(visiblePins()), 120);
    };
    open.append(img);
    open.onclick = () => detail(pin);
    const cap = document.createElement("figcaption");
    const badge = document.createElement("small");
    badge.textContent = a.name;
    cap.append(badge);
    if (pin.titel) { const t = document.createElement("strong"); t.textContent = pin.titel; cap.append(t); }
    if (pin.notiz) { const n = document.createElement("p"); n.textContent = pin.notiz; cap.append(n); }
    if (pin.tags.length) {
      const tags = document.createElement("div"); tags.className = "mb-cardtags";
      for (const t of pin.tags) {
        const b = document.createElement("button"); b.type = "button"; b.textContent = "#" + t;
        b.onclick = () => { state.tag = t; render(); };
        tags.append(b);
      }
      cap.append(tags);
    }
    cap.append(colors);
    fig.append(open, cap);
    return fig;
  }

  // ---- Detailansicht und Bearbeiten
  function fillAreas(select) {
    select.replaceChildren(...AREAS.map(a => new Option(a.name, a.id)));
  }
  function detail(pin) {
    state.current = pin;
    $("mbDlgTitle").textContent = pin.titel || "Inspiration";
    $("mbDlgImg").src = "moodboard/" + pin.bild;
    $("mbDlgImg").alt = pin.titel || "";
    $("mbEdTitle").value = pin.titel || "";
    $("mbEdArea").value = pin.bereich;
    $("mbEdTags").value = pin.tags.join(", ");
    $("mbEdNote").value = pin.notiz || "";
    $("mbEdSource").value = pin.quelle || "";
    $("mbEdOpen").hidden = !/^https?:\/\//.test(pin.quelle || "");
    $("mbEdOpen").href = pin.quelle || "#";
    $("mbEdMeta").textContent = "Hinzugefügt am " + new Date(pin.datum).toLocaleDateString("de-DE") + " · Datei " + pin.bild;
    $("mbEdMsg").textContent = "";
    swatches($("mbDlgColors"), palettes.get(pin.id) || []);
    $("mbDialog").showModal();
  }
  $("mbClose").onclick = () => $("mbDialog").close();
  $("mbEdit").onsubmit = async event => {
    event.preventDefault();
    try {
      const updated = await api("aendern", {id: state.current.id, titel: $("mbEdTitle").value, bereich: $("mbEdArea").value,
        tags: $("mbEdTags").value, notiz: $("mbEdNote").value, quelle: $("mbEdSource").value});
      Object.assign(state.current, updated);
      $("mbDialog").close();
      render();
    } catch (e) { $("mbEdMsg").textContent = e.message; }
  };
  $("mbDelete").onclick = async () => {
    if (!confirm("Dieses Bild vom Moodboard entfernen?")) return;
    try {
      await api("loeschen", {id: state.current.id});
      state.pins = state.pins.filter(p => p !== state.current);
      $("mbDialog").close();
      render();
    } catch (e) { $("mbEdMsg").textContent = e.message; }
  };

  // ---- Hinzufügen: Link, Einfügen (Strg+V), Ziehen, Datei
  function status(text, error) {
    $("mbStatus").textContent = text;
    $("mbStatus").classList.toggle("error", !!error);
  }
  async function add(body, label) {
    if (state.busy) return;
    state.busy = true; $("mbSubmit").disabled = true;
    status(label + " …");
    try {
      const pin = await api("neu", {bereich: $("mbArea").value, ...body});
      state.pins.unshift(pin);
      state.area = "alle"; state.tag = null;
      render();
      status("Hinzugefügt. Klicke auf das Bild, um Titel, Tags und Notiz zu ergänzen.");
      return pin;
    } catch (e) { status(e.message, true); }
    finally { state.busy = false; $("mbSubmit").disabled = false; }
  }
  async function shrink(file) {
    // Große Bilder werden vor dem Speichern verkleinert, damit das Repository schlank bleibt.
    if (file.type === "image/gif") return readData(file);
    const bitmap = await createImageBitmap(file);
    const scale = Math.min(1, 1800 / Math.max(bitmap.width, bitmap.height));
    const canvas = document.createElement("canvas");
    canvas.width = Math.round(bitmap.width * scale); canvas.height = Math.round(bitmap.height * scale);
    canvas.getContext("2d").drawImage(bitmap, 0, 0, canvas.width, canvas.height);
    const blob = await new Promise(resolve => canvas.toBlob(resolve, "image/webp", 0.86));
    return readData(blob || file);
  }
  const readData = blob => new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result); reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
  async function addFiles(files, source = "") {
    for (const file of files) {
      if (!file.type.startsWith("image/")) { status("Bitte nur Bilddateien hinzufügen.", true); continue; }
      try { await add({bild: await shrink(file), titel: file.name && !/^image\.\w+$/.test(file.name) ? file.name.replace(/\.\w+$/, "") : "", quelle: source}, "Bild wird gespeichert"); }
      catch { status("Das Bild konnte nicht gelesen werden.", true); }
    }
  }
  $("mbAdd").onsubmit = async event => {
    event.preventDefault();
    const link = $("mbLink").value.trim();
    if (!link) { status("Füge zuerst einen Link ein.", true); return; }
    if (await add({link}, "Bild wird aus dem Internet geladen")) $("mbLink").value = "";
  };
  $("mbPick").onclick = () => $("mbFile").click();
  $("mbFile").onchange = () => { addFiles([...$("mbFile").files]); $("mbFile").value = ""; };
  const section = $("moodboard");
  section.addEventListener("dragover", event => { event.preventDefault(); section.classList.add("mb-dragging"); });
  section.addEventListener("dragleave", event => { if (!section.contains(event.relatedTarget)) section.classList.remove("mb-dragging"); });
  section.addEventListener("drop", event => {
    event.preventDefault(); section.classList.remove("mb-dragging");
    const files = [...event.dataTransfer.files].filter(f => f.type.startsWith("image/"));
    if (files.length) { addFiles(files); return; }
    // Bild aus einem anderen Browserfenster gezogen: Bildadresse verwenden.
    const html = event.dataTransfer.getData("text/html");
    const src = html && new DOMParser().parseFromString(html, "text/html").querySelector("img")?.src;
    const link = src || event.dataTransfer.getData("text/uri-list") || event.dataTransfer.getData("text/plain");
    if (/^https?:\/\//.test(link || "")) add({link: link.trim()}, "Bild wird aus dem Internet geladen");
  });
  document.addEventListener("paste", event => {
    if (section.hidden || $("mbDialog").open) return;
    const files = [...event.clipboardData.files].filter(f => f.type.startsWith("image/"));
    if (files.length) { event.preventDefault(); addFiles(files); return; }
    const text = event.clipboardData.getData("text/plain").trim();
    if (document.activeElement?.matches("input,textarea") || !/^https?:\/\/\S+$/.test(text)) return;
    event.preventDefault();
    add({link: text}, "Bild wird aus dem Internet geladen");
  });

  // ---- Inspirationssuche
  $("mbSources").replaceChildren(...SOURCES.map(([name, url]) => {
    const b = document.createElement("button");
    b.type = "button"; b.className = "mb-source"; b.textContent = name;
    b.onclick = () => {
      const query = $("mbQuery").value.trim() || $("mbQuery").placeholder.split(", ")[0].replace(/^z\. B\. /, "");
      window.open(url(encodeURIComponent(query)), "_blank", "noopener");
    };
    return b;
  }));
  $("mbQuery").placeholder = "z. B. " + IDEAS.slice(0, 3).join(", ");
  $("mbSearch").onsubmit = event => { event.preventDefault(); $("mbSources").firstElementChild.click(); };
  $("mbFind").oninput = () => { state.find = $("mbFind").value.trim(); render(); };

  fillAreas($("mbArea")); fillAreas($("mbEdArea"));
  window.addEventListener("hashchange", () => { if (location.hash === "#moodboard") load(); });
  load();
})();
