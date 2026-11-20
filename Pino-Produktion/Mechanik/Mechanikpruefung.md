# Mechanikprüfung · Bollerwagen

Der Blender-Blockout zeigt das linke Vorderrad in drei Zuständen: montiert, in axialer Explosionslage und als direkter Nabenvergleich. Der Wagenkörper ist 505 mm lang und 230 mm breit. Der Achsabstand beträgt 330 mm, der Rollradius 90 mm.

## Koordinaten und Bewegungen

| Bezug | Richtung |
| --- | --- |
| Wagen | +X vorwärts zur Deichsel, +Y links, +Z oben |
| Linkes Vorderrad | Mittelpunkt in Nennlage (165, 139, 90) mm |
| Rad links | Lokal +X = Welt +X, lokal +Y = Welt −Z, lokal +Z = Welt +Y |
| Rad rechts | Lokal +X = Welt +X, lokal +Y = Welt +Z, lokal +Z = Welt −Y |
| Montage links | Rad und Scheibe von +Y nach −Y, Clip von +Z nach −Z |
| Geradeauslauf +X | Rotation um Welt +Y, also um lokal +Z links und lokal −Z rechts |

Die Achszapfen sind am Wagen fest. Das Rad dreht sich um den Zapfen. Der innere Anschlag, die Scheibe und der Clip begrenzen seine axiale Verschiebung.

## Geprüfte Geometrie

| Stelle | Maß und Prüfung |
| --- | --- |
| Achszapfen | Ø16 mm, Überstand bis Y=174 mm |
| Intakte Nabe | Ø16,8 mm, 0,4 mm nominelles radiales Spiel |
| Verschlissene Nabe | 23,2 × 17,6 mm, entlang der langen Achse mindestens 6 mm nachgewiesener Gesamtweg zwischen zwei geprüften Exzenterpositionen |
| Radnabe | 30 mm axial, Nennlage Y=124–154 mm |
| Unterlegscheibe | Ø34/17 mm, axial 4 mm, Nennlage Y=155–159 mm |
| Clip | Ø4,4 mm quer durch Bohrung Ø5 mm, Mitte bei Y=162 mm |
| Axialspiel | Insgesamt 1,8 mm zwischen innerem Anschlag und Clip, durch Rad und Scheibe geteilt |
| Freigängigkeit | Mindestens 10,5 mm zwischen Reifen und Achsträger, 11,5 mm zur Längswand, 150 mm zwischen Vorder- und Hinterreifen |
| Laufprobe | 500 mm Vorwärtsweg entsprechen 5,556 rad bzw. rund 318° Radrotation. Der Reifen berührt bei abgesenktem Wagen die Bodenebene. |

Das Skript prüft konzentrisches Aufschieben, Freigängigkeit der rotationssymmetrischen Außenkontur, nutzbaren Clipweg und Verschiebung der runden Achse in der ovalen Nabe. Die Abstützung in der Montageansicht hält die Reifen 8 mm über Boden.

## Reihenfolge für die Bilder

1. Wagen steht beim Befund. Das belastete Rad beziehungsweise die Nabe lässt sich von Hand leicht quer zur Achse bewegen. Für die Demontage steht der Wagen auf Stützen.
2. Sicherungsclip nach oben herausziehen. Scheibe und altes Rad nacheinander gerade entlang der Achse nach außen abziehen.
3. Ausgebaute Räder frontal vergleichen. Das ovale Loch des alten Rads liegt links im Bild, die runde Bohrung des Ersatzrads rechts.
4. Das intakte Rad bis zum inneren Anschlag entlang des Zapfens schieben. Die Scheibe aufschieben. Clip von oben in die Querbohrung einsetzen und den Federbügel am Zapfen einrasten lassen.
5. Am abgestützten Wagen das fertig gesicherte Rad drehen. Erst danach Wagen absenken, Stützen entfernen und geradeaus rollen. In der Ansicht von +Y bewegt er sich im Bild nach links.

## Geprüfte Ansichten und Modellgrenzen

- **01-Fahrbereit.png** zeigt die montierte Außenseite und die Deichsel vor dem linken Vorderrad.
- **02-Montage.png** zeigt die Explosionslage entlang +Y und den Clip darüber. Für einen Insert von der Vorderseite entlang −X bleiben die Schritte räumlich lesbar.
- **03-Nabenvergleich.png** zeigt das ovale und runde Loch frontal in gleicher Vergrößerung.
- Der Blockout verwendet starre Teile und eine vereinfachte Federbügelgeometrie. Die sichtbare Rastbewegung braucht eine kleine elastische Auslenkung im Animationsrig. Lastabhängiger Verschleiß, Federkraft und der unregelmäßige Radlauf vor der Reparatur sind nicht simuliert. Die Laufprobe nach dem Einbau ist geometrisch geprüft.
