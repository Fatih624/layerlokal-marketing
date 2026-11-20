# Pinos Nachbarschaft · Produktion

**Einstieg für den Pilotfilm „Das vierte Rad“**

24 Bilder pro Sekunde, maximal 90 Sekunden. Die Arbeitskopie liegt auf D:. Dieser GitHub-Stand enthält das Drehbuch, die einsatzbereiten Blender-Dateien und die Meshy-Dreiansichten. Mina führt durch die Geschichte. Pino, Riko und Jan sind die weiteren sichtbaren Figuren, Samis Vater bleibt als optionale Stimme aus dem Off. Sami kann in einer späteren Folge dazukommen.

## Öffnen und ansehen

1. [Drehbuch Sekunde für Sekunde](Drehbuch/Das-vierte-Rad-90-Sekunden.md) mit Bild, Ton und Dialog von 00:00 bis 01:29.
2. [Blender-Pilotvorlage](Blender/Pino-Pilotvorlage.blend) mit zehn Kameramarkern, drei Schauplatz-Blockouts und Prüfgeometrie. Die 12-Sekunden-Szene darin ist ein früher Blicktest. Die aktuelle Handlung vergleicht die Nabenbohrungen bei gleichem Raddurchmesser.
3. [Mechanik](Mechanik/Mechanikpruefung.md) mit geprüften Ansichten für Achse, Nabe, Scheibe und Federstecker. Die eigentliche gezeichnete Animation bleibt ein Produktionsschritt.
4. [Grease-Pencil-Probe](Blender/Grease-Pencil-Gesichtstest.blend) mit einzelnen Augen-, Brauen-, Nasen- und Mundebenen.

## Assets in Blender verwenden

Im Blender Asset Browser lassen sich die Ordner **Animationen** und **Assets/Modelle/Blender-Assets** als zwei Asset Libraries eintragen. Dadurch bleiben Figuren, Kulissen und Actions im gleichen Projekt wiederverwendbar. Die .blend-Dateien können auch direkt geöffnet oder über „Datei → Anhängen“ genutzt werden. Bestehende Blender-Voreinstellungen bleiben lokal nutzbar.

- [Mina · Rig und Bewegungen](Animationen/Mina-Rig-und-Bewegungen.blend). Die Collection enthält den neutralen Körper, das Mixamo-Rig und einen Kopfanker für Grease Pencil. Gehen und Laufen liegen als getrennte Action-Assets bei 24 fps vor. Beim Zuordnen Minas Mixamo-Armature und den aus dem Export stammenden Action-Slot wählen.
- [Kopfnicken, Blickwechsel und Reaktion](Animationen/README.md). Diese drei generischen Actions nutzen das beiliegende Referenzrig. Sie müssen bei Bedarf auf Mina übertragen werden.
- [Pino und Riko](Assets/Modelle/Blender-Assets/Pino-und-Riko.blend). Acht getrennte bewegliche Schichten für Pino, Rikos Brille als eigenes Element. Beide Gesichter sind vorbereitet für Grease Pencil.
- [Riegerplatz-Kulissen](Assets/Modelle/Blender-Assets/Riegerplatz-Kulissen.blend). Die Bank hat 10.000 Dreiecke, die Fassade 25.000. Beide enthalten gepackte 2K-PBR-Texturen und stehen auf Z = 0.
- [Meshy-Referenzen aller drei Figuren](Assets/Charaktere). Jeweils Vorderseite, linkes Profil und Rückseite in derselben T-Pose. Für Meshy nur die neutralen Ansichten im Unterordner Meshy hochladen.
- Die unveränderten Meshy-Downloads und ausgepackten FBX-Dateien bleiben in der Arbeitskopie auf D:. Die Blender-Dateien enthalten die verwendeten Texturen.

## Stil und Abnahme

Matte, leicht handgemachte 3D-Körper und Kulissen in der LayerLokal-Palette, mit gezeichneter Mimik und dezentem, warmem Licht. Ebene Materialien und klare Silhouetten helfen, die Mimik auch in kleinen Einstellungen zu lesen. Erst bei Bedarf mehr Struktur als feine Textur ergänzen. Die Straße bleibt modular in Blender, Bank und Fassadenmodul sind unabhängige Kulissenobjekte.

Mina wurde in drei Ansichten vor dem Rig geprüft. Die glatte Gesichtsfläche bleibt frei von Augen, Brauen, modellierter Nase und Mund. Alle 33.004 Punkte sind gewichtet, das Rig hat 28 Knochen. Gehen ist für den Blockout und mittlere Einstellungen geeignet. Beim Laufen stauchen einzelne Bereiche an Achsel und gebogenem Bein. Für Nahaufnahmen die Stufen am Kinn glätten. Eigenes Finger-Rig oder Posenkorrektur einplanen, sobald Mina sichtbar zugreift. Beim Ziehen des Wagens den Gehzyklus als Ausgangspunkt und den Griff als eigene Pose mit Kontaktprüfung verwenden.

Erste Meshy-Runde: drei private Standard-Generierungen mit je 30 Credits (Mina, Parkbank, Fassade). Fahrzeuge, Räder und Maskottchen sind in Blender entstanden. Jan ist als Entwurfsreferenz und Platzhalter vorgesehen.
