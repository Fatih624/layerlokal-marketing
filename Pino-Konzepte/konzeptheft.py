"""Erstellt das aktuelle Konzeptheft aus den Bildern in diesem Ordner."""

import os
from io import BytesIO
from pathlib import Path

from PIL import Image
from reportlab import rl_config
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle


ROOT = Path(__file__).resolve().parent
FIGURES = ROOT / "Meshy-Referenzen"
DRAFTS = ROOT / "Entwuerfe-Vater-und-Sohn"
FACES = ROOT / "Grease-Pencil"
PAGES = 11
FILE = ROOT / "LayerLokal-Pino-Konzeptheft.pdf"
BG, INK, RUST, GREEN, LINE, WHITE = map(
    HexColor, ["#FBF6EF", "#2B211B", "#93401F", "#E1ECDF", "#E4D4C2", "#FFFFFF"]
)
W, H = A4
M = 42
CONTENT = W - 2 * M
FONTS = Path(os.environ["WINDIR"]) / "Fonts"
for name, file in [("Body", "arial.ttf"), ("Strong", "arialbd.ttf"), ("Title", "georgiab.ttf")]:
    pdfmetrics.registerFont(TTFont(name, str(FONTS / file)))

rl_config.useA85 = False
temp = FILE.with_suffix(".tmp")
canvas = Canvas(str(temp), pagesize=A4, pageCompression=1)
canvas.setTitle("Pinos Nachbarschaft - Serienkonzept")
canvas.setAuthor("LayerLokal")


def text(value, x, top, size, font="Body", color=INK):
    canvas.setFillColor(color)
    canvas.setFont(font, size)
    canvas.drawString(x, H - top - size, value)


def paragraph(value, x, top, width=CONTENT, size=13, leading=19, color=INK):
    style = ParagraphStyle("Body", fontName="Body", fontSize=size, leading=leading, textColor=color)
    block = Paragraph(value, style)
    _, height = block.wrap(width, H)
    block.drawOn(canvas, x, H - top - height)
    return top + height


def box(x, top, width, height, color=WHITE, radius=9):
    canvas.setFillColor(color)
    canvas.roundRect(x, H - top - height, width, height, radius, fill=1, stroke=0)


def picture(path, x, top, width, height):
    with Image.open(path) as img:
        factor = min(width / img.width, height / img.height)
        dw, dh = img.width * factor, img.height * factor
        jpeg = BytesIO()
        img.convert("RGB").save(jpeg, format="JPEG", quality=92, optimize=True)
        jpeg.seek(0)
        canvas.drawImage(
            ImageReader(jpeg), x + (width - dw) / 2,
            H - top - (height + dh) / 2, dw, dh
        )


def page(number, section):
    canvas.setFillColor(BG)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)
    text("LAYERLOKAL  /  PINOS NACHBARSCHAFT", M, 30, 9, "Strong", RUST)
    canvas.setStrokeColor(LINE)
    canvas.line(M, H - 52, W - M, H - 52)
    canvas.line(M, 47, W - M, 47)
    text(section.upper(), M, H - 36, 8, "Strong", RUST)
    canvas.setFillColor(RUST)
    canvas.setFont("Strong", 8)
    canvas.drawRightString(W - M, 20, f"{number:02} / {PAGES:02}")


def heading(title, description):
    text(title, M, 73, 31, "Title")
    paragraph(description, M, 126)


def card(title, body, x, top, width, height, color=WHITE):
    box(x, top, width, height, color)
    text(title, x + 14, top + 12, 13, "Strong", RUST)
    paragraph(body, x + 14, top + 33, width - 28, 11, 15)


page(1, "Serienkonzept")
text("Animierte Kinderserie · Konzeptstand 20. November 2026", M, 81, 11, "Strong", RUST)
text("Pinos", M, 105, 56, "Title")
text("Nachbarschaft", M, 160, 56, "Title")
paragraph(
    "Ein Bollerwagen verliert ein Rad. Mina, Pino und Riko wollen ihn bis zum Hoffest wieder flottmachen.",
    M, 244, CONTENT, 15, 21
)
picture(DRAFTS / "Darmstadt-Riegerplatz-v2.png", M, 321, CONTENT, 288)
text("Frühere Ortsstudie für den stilisierten Riegerplatz im Darmstädter Martinsviertel.", M, 619, 10, "Body", RUST)
box(M, 663, CONTENT, 83, GREEN)
text("Die Pilotfolge  /  Das vierte Rad", M + 15, 676, 15, "Strong")
paragraph("Für Kinder von 6 bis 9 Jahren · höchstens 90 Sekunden", M + 15, 703, CONTENT - 30, 12, 17)
canvas.showPage()

page(2, "Welt und Bildsprache")
heading("Das Watzeverdel", "Pinos Geschichten spielen im Darmstädter Martinsviertel. Zwischen Riegerplatz, Hinterhöfen und Werkstatt ist Hilfe oft gleich um die Ecke.")
picture(DRAFTS / "Darmstadt-Riegerplatz-v2.png", M, 195, CONTENT, 288)
card("Woran man Darmstadt erkennt",
     "Ein Quartiersplatz mit Altbaufassaden, rotem Sandstein, Fahrrädern und dem Riegerplatz-Schild. Der Platz ist für die Serie frei stilisiert.", M, 508, CONTENT, 73)
card("Wie die Serie aussieht",
     "Körper, Haare, Kleidung und Kulisse sind 3D. Augen, Brauen, Nase und Mund wirken wie mit warmer Tinte auf die Formen gezeichnet.", M, 592, CONTENT, 73)
card("Wie LayerLokal vorkommt",
     "Samis Vater findet über den lokalen Marktplatz Jan, den Nachbarn mit 3D-Drucker. Die Reparatur und die Begegnung stehen in der Geschichte im Vordergrund.", M, 676, CONTENT, 73, GREEN)
canvas.showPage()


page(3, "Besetzungsvorschlag")
heading("Sechs Figuren", "Mina, Pino und Riko tragen den Pilotfilm. Jan hilft kurz in der Werkstatt. Sami und sein Vater bleiben im Serienensemble für spätere Geschichten.")
characters = [
    ("Pino", "Der genaue Beobachter",
     "Neugierig und geduldig. Er zeigt mit einem Blick, welches Detail alle übersehen. Sein Auge und die acht Schichten bleiben wie im bisherigen Entwurf.",
     FIGURES / "Pino-T-Pose.png"),
    ("Riko", "Der spontane Tüftler",
     "Einfallsreich, schnell begeistert und zuweilen voreilig. Wenn seine Idee danebenliegt, rückt er die Brille zurecht und probiert es noch einmal.",
     FIGURES / "Riko-T-Pose.png"),
    ("Mina", "Die witzige Freundin",
     "In Darmstadt aufgewachsen, mutig und schlagfertig. Sie ahmt das Klackern des Wagens nach und bringt andere zum Lachen. Locken, Latzhose, Messingknöpfe.",
     FIGURES / "Mina-T-Pose.png"),
    ("Sami", "Der leise Erfinder",
     "Etwa sieben, einfallsreich und hartnäckig. Er sammelt Fundstücke und merkt sich, welches Teil woher kommt. Senfblitz am Shirt, kleiner Knieflicken.",
     FIGURES / "Sami-T-Pose.png"),
    ("Samis Vater", "Der ruhige Begleiter",
     "Hört zu, stellt eine einfache Frage und vermittelt über LayerLokal zu Jan. Eine Stimme aus dem Off ist für den Pilot optional. Der Figurenentwurf bleibt verfügbar.",
     DRAFTS / "Vater-T-Pose-v2.png"),
    ("Jan", "Der Werkstattnachbar",
     "Ein Darmstädter Werkstattbetreiber mit trockenem Humor. Beim Reparieren erklärt er den Kindern, was sie selbst prüfen können. Salbeifarbene Schürze.",
     FIGURES / "Jan-T-Pose.png"),
]
width = (CONTENT - 14) / 2
for index, (name, role, copy, photo) in enumerate(characters):
    x = M + index % 2 * (width + 14)
    y = 182 + 179 * (index // 2)
    box(x, y, width, 166)
    picture(photo, x + 8, y + 18, 96, 118)
    text(name, x + 111, y + 11, 15, "Title")
    role_end = paragraph(role, x + 111, y + 35, width - 122, 10, 13, RUST)
    paragraph(copy, x + 111, role_end + 6, width - 122, 9.5, 12.5)
paragraph("Mina hat im Pilot die Hauptrolle. Sami ist ihr Freund und kann in einer späteren Folge einsteigen.", M, 727, CONTENT, 10.5, 14)
canvas.showPage()

page(4, "Pilotfolge")
heading("Das vierte Rad", "Ein Problem am Riegerplatz führt Mina in Jans Werkstatt. Das sekundengenaue Drehbuch auf D: hat 90 Sekunden.")
beats = [
    ("01  Ein Klack auf dem Pflaster", "Auf dem Weg zum Hoffest klackert der Bollerwagen. Mina hält an und macht das Geräusch nach. Pino zeigt auf das linke Vorderrad."),
    ("02  Hilfe gleich um die Ecke", "Pinos Schichten leuchten kurz auf. Samis Vater sagt aus dem Off: „Über LayerLokal hab ich Jan gefunden. Gleich um die Ecke.“"),
    ("03  Rikos erster Versuch", "Jan nimmt am abgestützten Wagen das alte Rad ab. Riko sieht zwei gleich große Reifen und hält die Räder für gleich."),
    ("04  Schau mal in die Mitte", "Pino lenkt den Blick in die Mitte. Das alte Nabenloch ist oval, die runde Bohrung im intakten Vergleichsrad sitzt passend."),
    ("05  Ein Rad nach Maß", "Jan misst den Zapfen und fertigt das Ersatzrad. Er montiert Rad und Scheibe entlang des Zapfens und sichert sie mit dem Federstecker."),
    ("06  Freie Fahrt zum Hoffest", "Nach der Handprobe zieht Mina den Wagen zum Hoffest. Das Klackern bleibt aus und die Wimpel kommen rechtzeitig an."),
]
for index, (title, body) in enumerate(beats):
    card(title, body, M, 169 + 94 * index, CONTENT, 82, GREEN if index == 3 else WHITE)
canvas.showPage()

page(5, "Animationstest")
heading("Zwölf Sekunden", "Drei Einstellungen in der Werkstatt testen, ob Blick, Pause und Schnitt den Aha-Moment verständlich machen.")
for index, (title, body) in enumerate([
    ("0–4 Sekunden  /  Riko ist sicher", "Halbnah auf Pino und Riko. Riko sagt „Passt doch“. Pinos Pupille wandert zum großen Rad."),
    ("4–8 Sekunden  /  Beide Räder", "Fester Schnitt. Beide Räder haben denselben Außendurchmesser. Auf gleicher Höhe sieht man die ovale Bohrung links und die runde rechts. Pino sagt: „Schau mal in die Mitte.“"),
    ("8–12 Sekunden  /  Riko versteht", "Nahaufnahme. Rikos Blick geht nach oben. Die Brille rutscht leicht. Nach einer Pause sagt er: „Ach …“"),
]):
    card(title, body, M, 169 + 80 * index, CONTENT, 72, GREEN if index == 1 else WHITE)
picture(ROOT / "Pino-Werkstatt.png", M, 414, CONTENT, 288)
text("Früher Werkstattentwurf. Referenz für Licht, Material und die Anordnung an der Werkbank.", M, 710, 10, "Body", RUST)
paragraph("Zuerst Standbilder und Tempoton schneiden. Dann Mimik und Brille animieren. Für einen Eevee-Vergleich je 48 Bilder bei 720p rendern.", M, 736, CONTENT, 10.5, 14)
canvas.showPage()

page(6, "Modellvorlagen")
heading("Erst die beiden Kinder", "Mina behält ihre Latzhose. Sami bekommt einen kleinen Blitz und eine sichtbar geflickte Hose. Jan ist der neue Entwurf für die Werkstattrolle.")
width = (CONTENT - 20) / 3
for index, (name, img) in enumerate([
    ("Mina", "Mina-T-Pose.png"),
    ("Sami", "Sami-T-Pose.png"),
    ("Jan", "Jan-T-Pose.png"),
]):
    x = M + index * (width + 10)
    box(x, 178, width, 194)
    picture(FIGURES / img, x + 7, 186, width - 14, 151)
    text(name, x + 12, 346, 13, "Strong", RUST)
card("Zuerst Mina in Meshy",
     "Minas Vorderseite, Profil und Rückseite sind bereit. Das private Meshy-Modell und die exportierten Bewegungen liegen in der Blender-Produktion auf D:.",
     M, 399, CONTENT, 78, GREEN)
card("Gesicht für Zeichnung vorbereiten",
     "Minas Gesichtsfläche ist glatt. Augen, Brauen, Nase und Mund werden komplett mit Grease Pencil gezeichnet. Der Kopfanker liegt am Skelett.",
     M, 489, CONTENT, 78)
card("Bestehende Figuren weiterverwenden",
     "Pino und Riko bleiben im bisherigen Design. Pinos Schichten und Rikos Brille bleiben einzeln animierbar. Der Vater kann für den Pilot aus dem Off sprechen.",
     M, 579, CONTENT, 78)
paragraph("Der Entwurf des Vaters mit kleinerem Kopf und die Riegerplatz-Szene liegen im Ordner Entwuerfe-Vater-und-Sohn.", M, 686, CONTENT, 10.5, 15)
canvas.showPage()

page(7, "Farbpalette")
heading("Farben aus LayerLokal", "Die Hauptfarben stammen direkt aus der Landingpage. Auf Stoff, Stein und Holz wirken sie weicher, damit die Silhouetten und Gesichter lesbar bleiben.")
colors = [
    ("Creme", "#FBF6EF", "Putz, T-Shirts, Augenweiß", False),
    ("Tinte", "#2B211B", "Gesichtslinien, dunkler Stoff", True),
    ("Terrakotta", "#B5502F", "Pino, Sandstein, Samis Flicken", True),
    ("Helles Orange", "#FF8A55", "Pinos Lichtimpuls und kleine Lichtakzente", False),
    ("Salbei", "#3F6B4A", "Samis Shirt, Jans Schürze, Türen", True),
    ("Senf", "#C98A16", "Samis Blitz und Minas Knöpfe", False),
    ("Nacht", "#171210", "Dunkelste Akzente der Werkstatt", True),
]
width = (CONTENT - 28) / 3
for i, (name, code, use, dark) in enumerate(colors):
    x = M + i % 3 * (width + 14)
    y = 175 + i // 3 * 142
    box(x, y, width, 128)
    box(x + 7, y + 7, width - 14, 63, HexColor(code), 6)
    text(code, x + 17, y + 33, 12, "Strong", WHITE if dark else INK)
    text(name, x + 10, y + 76, 12, "Strong")
    paragraph(use, x + 10, y + 97, width - 20, 9.5, 12)
x, y = M + width + 14, 459
box(x, y, width, 128)
box(x + 7, y + 7, width - 14, 63, HexColor("#3C6872"), 6)
text("#3C6872", x + 17, y + 33, 12, "Strong", WHITE)
text("Petrol", x + 10, y + 76, 12, "Strong")
paragraph("Zusatzfarbe nur für Minas Latzhose", x + 10, y + 97, width - 20, 9.5, 12)
card("Farbregie am Riegerplatz",
     "Creme und Terrakotta geben den Fassaden ihre Grundstimmung. In der Werkstatt kommen Salbei und Tinte hinzu. Helles Orange bleibt Pinos kurzen Lichtimpulsen vorbehalten.",
     M, 616, CONTENT, 85, GREEN)
text("Quelle der sieben Markenfarben: LayerLokal, landingpage/css/base.css.", M, 730, 10, "Body", RUST)
canvas.showPage()

page(8, "Grease Pencil")
heading("Gezeichnete Gesichter", "Die Köpfe bleiben räumlich. Gezeichnete Augen, Brauen, Nase und Mund sorgen für die Mimik. So kann die gleiche Kopfform neugierig schauen, blinzeln oder sich erschrecken.")
picture(FACES / "Mina-und-Sami-Gesichtsstil.png", M, 190, CONTENT, 342)
text("Von links: neugierig · blinzeln · überrascht. Oben Mina, unten Sami.", M, 545, 10, "Body", RUST)
card("Gesicht in Ebenen aufbauen",
     "Augen und Pupillen, Brauen, Nase und Mund auf eigene Grease-Pencil-Ebenen legen. Die Nase kann eine kurze Tintenlinie bleiben. Bei einer stärkeren Drehung hilft eine separat gezeichnete Profilansicht.",
     M, 584, CONTENT, 83, GREEN)
card("Zwei kurze Eevee-Tests",
     "Jeweils dieselbe Mimik testen: einmal frontal, einmal mit etwa 30 Grad Kopfdrehung. Prüfen, ob die Linien an der Oberfläche bleiben und Pupillen, Blinzeln und Mund aus Kameradistanz lesbar sind.",
     M, 679, CONTENT, 82)
canvas.showPage()

page(9, "Produktion")
heading("Klein anfangen", "Für den Pilot reichen der Riegerplatz als kurze Ortsansicht, eine Werkbank und ein reparierter Wagen. Die Besetzung kann sich nach dem Test weiterentwickeln.")
card("Meshy für einzelne Kulissenteile",
     "Parkbank und Altbau-Fassadenmodul wurden in Meshy erstellt und für Eevee auf 10.000 bzw. 25.000 Dreiecke reduziert. Originale und Blender-Assets liegen auf D:. Straße und Bürgersteig bleiben modulare Blender-Geometrie.",
     M, 176, CONTENT, 102, GREEN)
card("Blender und Eevee",
     "Auf diesem Rechner wurde Blender 5.2.1 LTS gefunden. Für den Pilot bei 5.2 LTS bleiben und bei Gelegenheit auf 5.2.4 aktualisieren. Blender 5.3 bringt unter anderem bessere Auswahl, Carver und Füllwerkzeuge im Grease-Pencil-Zeichenmodus.",
     M, 292, CONTENT, 102)
card("Mechanik vor dem nächsten Storyboard",
     "Wagen, Nabe, Achse, Scheibe und Sicherung wurden separat nachgebaut und geometrisch geprüft. Die elastische Bewegung des Federbügels und der Radlauf unter Last bleiben Produktionsschritte. Die Vorlage enthält Kameras auf die geprüften Teile.",
     M, 408, CONTENT, 102, GREEN)
card("Wo sich der Pilot begrenzt",
     "Das Drehbuch umfasst Sekunde 00:00 bis 01:29. Mina trägt die Geschichte. Gehen und Laufen liegen als geprüfte Blender-Actions für erste Layouts vor. Für Nahaufnahmen sind Kinn-Shading und Fingersteuerung weiter zu bearbeiten.",
     M, 524, CONTENT, 102)
paragraph('Quellen: <link href="https://www.meshy.ai/use-cases/free-game-assets/game-props" color="#93401F">Meshy-Props</link> · <link href="https://www.meshy.ai/tutorials/how-to-create-architectural-models" color="#93401F">Meshy-Architektur</link> · <link href="https://www.blender.org/releases/5-2/" color="#93401F">Blender 5.2 LTS</link> · <link href="https://www.blender.org/download/releases/5-3/" color="#93401F">Blender 5.3</link>', M, 664, CONTENT, 10.5, 15)
canvas.showPage()

page(10, "Eevee-Probe")
heading("Das Gesicht in Blender", "Eine einfache 3D-Kopfform mit echten Grease-Pencil-Zeichnungen. Die Gesichter im Stilblatt zeigen den gewünschten Serienlook, diese vier Bilder zeigen die technische Probe.")
shots = [
    ("Bild 1  /  Neugierig", "GP-01.png"),
    ("Bild 17  /  Blinzeln", "GP-17.png"),
    ("Bild 31  /  Überrascht", "GP-31.png"),
    ("Bild 31  /  30 Grad", "GP-31-Seitenansicht.png"),
]
width = (CONTENT - 16) / 2
for index, (label, frame) in enumerate(shots):
    x = M + index % 2 * (width + 16)
    y = 179 + 247 * (index // 2)
    box(x, y, width, 234)
    picture(FACES / frame, x + 10, y + 9, width - 20, 201)
    text(label, x + 12, y + 212, 10, "Strong", RUST)
paragraph("Gerendert in Blender 5.2.1 LTS mit Eevee. In der .blend-Datei lassen sich Augen, Brauen, Nase und Mund auf eigenen Ebenen bearbeiten. Die Probe verwendet einen Platzhalterkopf.", M, 696, CONTENT, 10.5, 15)
canvas.showPage()



page(11, "Mina · Gesichtsanimation")
heading("Fünf Ausdrücke für Mina", "Die Grease-Pencil-Zeichnungen folgen Minas Kopf- und Nackenbewegung. Die Locken bewegen sich mit dem Kopf. Die Standbilder stammen aus der editierbaren Eevee-Studie.")
mina_faces = FACES / "Mina-Gesichtsstudie"
mina_stills = [
    ("Neutral", "001-Neutral.png"),
    ("Freude", "022-Freude.png"),
    ("Lachen", "067-Lachen.png"),
    ("Verwunderung", "113-Verwunderung.png"),
    ("Weinen", "177-Weinen.png"),
    ("Skepsis", "221-Skepsis.png"),
]
width = (CONTENT - 22) / 3
for index, (label, image) in enumerate(mina_stills):
    x = M + index % 3 * (width + 11)
    y = 177 + 205 * (index // 3)
    box(x, y, width, 191)
    picture(mina_faces / image, x + 6, y + 7, width - 12, 154)
    text(label, x + 10, y + 169, 11, "Strong", RUST)
card("Was der Test zeigt",
     "Alle fünf Gefühle sind unterscheidbar. Die Gesichtslinien bleiben bei Kopfdrehung auf der Gesichtsform. Beim Weinen setzen die Tränen an den unteren Lidern an und laufen unterschiedlich weit über die Wangen.",
     M, 595, CONTENT, 83, GREEN)
paragraph("Für finale Nahaufnahmen bleiben der Haaransatz, die Ohrkonturen und der Schatten am Kinn zu verfeinern. Geprüfte Vorschau und Blender-Datei liegen auf D: in Animationen/Mina-Gesichtsstudie.", M, 700, CONTENT, 10.5, 15)
canvas.showPage()

canvas.save()
temp.replace(FILE)
