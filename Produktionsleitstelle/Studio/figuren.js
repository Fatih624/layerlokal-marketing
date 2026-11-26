const cast = [
  {name:"Mina", page:8, width:1774, height:887, front:[58,74,308,651]},
  {name:"Pino", page:14, width:1536, height:1024, front:[117,118,308,258]},
  {name:"Riko", page:17, width:1536, height:1024, front:[25,127,415,321]},
  {name:"Jan", page:20, width:1536, height:1024, front:[247,65,198,507]},
  {name:"Sami", page:23, width:1312, height:1199, front:[18,89,377,472]},
  {name:"Samis Vater", page:26, width:1536, height:1024, front:[58,76,405,415]}
];
const preview = document.getElementById("preview");
function showCharacter(character) {
  const {name,page,width,height} = character;
  const path = "figuren/" + name.replaceAll(" ","-");
  document.getElementById("characterName").textContent = name;
  const art = document.getElementById("characterArt");
  art.src = path + ".png";
  art.alt = name + " – Figurenreferenz";
  document.getElementById("sheetDownload").href = path + ".pdf";
  const download = document.getElementById("imageDownload");
  download.href = art.src;
  download.textContent = "PNG · " + width + " × " + height + " px";
  document.getElementById("chapterLink").href = "#seite-" + page;
  preview.showModal();
}
document.getElementById("closePreview").onclick = () => preview.close();
document.getElementById("chapterLink").onclick = () => preview.close();
window.addEventListener("hashchange", () => { if (preview.open) preview.close(); });
for (const character of cast) {
  for (const id of ["homeCast","allCast"]) {
    const card = document.createElement("button");
    card.className = "cast-card";
    const name = character.name;
    card.setAttribute("aria-label", name + " – Charactersheet ansehen und herunterladen");
    card.setAttribute("aria-haspopup","dialog");
    const frame = document.createElement("span");
    frame.className = "cast-frame";
    const front = document.createElement("span");
    front.className = "cast-front";
    const [x, y, width, height] = character.front;
    const scale = 100 / height;
    front.style.width = width * scale + "px";
    front.style.backgroundImage = 'url("figuren/' + name.replaceAll(" ","-") + '.png")';
    front.style.backgroundSize = character.width * scale + "px auto";
    front.style.backgroundPosition = -x * scale + "px " + -y * scale + "px";
    frame.append(front);
    const label = document.createElement("span");
    label.textContent = name;
    label.className = "cast-label";
    const eye = document.createElement("span");
    eye.className = "eye";
    eye.setAttribute("aria-hidden","true");
    label.append(eye);
    card.append(frame,label);
    card.onclick = () => showCharacter(character);
    document.getElementById(id).append(card);
  }
}
