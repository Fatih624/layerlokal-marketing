# Blender · Das vierte Rad

**Pino-Pilotvorlage.blend** in Blender 5.2 LTS öffnen. Die Szene **PILOT - Das vierte Rad** enthält die Einstellungen als Kameramarker. Sie läuft mit 24 Bildern/s von Bild 1 bis 2160 (90 s) und ist für Eevee in 1920 × 1080 eingerichtet.

| Zeit | Bild | Kamerabereich |
| --- | ---: | --- |
| 00 s | 1 | Riegerplatz |
| 08 s | 193 | Wagenstopp am Riegerplatz |
| 17 s | 409 | Hilfe und Übergang in die Werkstatt |
| 25 s | 601 | Montagekamera für die Demontage am abgestützten Wagen |
| 37 s | 889 | Frontaler Vergleich der ovalen und runden Nabe |
| 49 s | 1177 | Werkbank für Messen und Druckaufbau |
| 60 s | 1441 | Werkbank für den Zeitsprung zum fertigen Rad |
| 67 s | 1609 | Montagekamera für Rad, Scheibe und Sicherungsclip |
| 79 s | 1897 | Abgesenkter Wagen für die anschließende Probefahrt |
| 85 s | 2041 | Hof und Hoffest |

Im Outliner sind Riegerplatz, Hof, Werkstatt, Figuren-/Mechanikanker, Kameras und Licht getrennt. Die Werkbankoberfläche liegt auf Z = 1 m. Die Wagen- und Nabenobjekte wurden aus [Bollerwagen-Mechanik.blend](../Mechanik/Bollerwagen-Mechanik.blend) übernommen und als editierbare, statische Arbeitsgruppen an den Sets platziert. Die Farben und Formen der Sets sind Blockout. Modellübergänge, Figuren, Handlung, Drucker, Ton und Bewegung brauchen eigene Arbeit in den Einstellungen. Vor der Animation die Hinweise zur [Mechanikprüfung](../Mechanik/Mechanikpruefung.md) lesen.

## Separater 12-Sekunden-Blicktest

Im Szenenmenü **WERKBANK - 12 Sekunden** wählen. Die Schnitte bei Bild **1 / 97 / 193** folgen dem früheren Kompositionstest aus dem Konzeptheft. Die Arbeitsgruppe **PLATZHALTER - Werkbankfiguren und Räder** enthält die Stellvertreter für diesen Test. Die Mechanik-Collections des Piloten sind in der View Layer dieser Testszene ausgeblendet. Die alte Größenprobe ist als eigener Blick- und Schnitttest vorhanden. Der Pilot zeigt zwei gleich große Räder mit unterschiedlichen Naben.

Für die Einstellungsprüfung eine Testszene beziehungsweise einen kurzen Bildbereich auswählen. Die Vorlage speichert PNG-Einzelbilder in den jeweiligen relativen Renderordner.

## Gesicht · Grease Pencil

**Grease-Pencil-Gesichtstest.blend** ist eine editierbare Kopie des vorhandenen lokalen Gesichtstests. Das Objekt **Gesicht · Grease Pencil** enthält die Ebenen **Augen und Pupillen**, **Augenbrauen**, **Nase** und **Mund**. Die Referenzzeichnungen liegen auf Bildern 1, 17, 20 und 31. Die Nase ist als durchgehende Zeichnung auf Bild 1 angelegt.

Meshy-Figuren mit einer möglichst glatten Gesichtsfläche für die Zeichnungen vorbereiten. Nach dem Import insbesondere auf modellierte oder eingebackene Augen, Brauen, Nase und Mund achten. Das Grease-Pencil-Objekt per **File → Append → Object** übernehmen, an den Kopfcontroller binden und an die Form und Vorderseite des jeweiligen Kopfes anpassen. Die Gesichtszeichnungen bleiben auf ihren eigenen Ebenen animierbar. Bei starken Kopfdrehungen eigene Profilzeichnungen vorsehen.

Die [Animationsbibliothek](../Animationen/Pino-Animationsbibliothek.blend) enthält Kopf-, Blick- und Reaktionsgesten. Körpergesten können mit den gezeichneten Gesichtsausdrücken kombiniert werden.
