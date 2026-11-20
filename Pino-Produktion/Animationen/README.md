# Pinos Nachbarschaft · Animationsbibliothek

**Pino-Animationsbibliothek.blend** in Blender 5.2 LTS öffnen. Die Szene **GESTENTEST** enthält ein sichtbares Prüfrig mit einer NLA-Spur und drei aufeinanderfolgenden Gesten. Im Szenenmenü liegt daneben die unbespielte **RIGVORLAGE**.

| Action | NLA-Demo | Bilder der Action | Controller und Kanal |
| --- | --- | --- | --- |
| Kopfnicken | 1–24 | 1–24 | CTRL_Kopf · lokale Rotation X |
| Blickwechsel | 25–52 | 1–28 | CTRL_Blick · lokaler Versatz entlang X, Halt auf 9–16 |
| Reaktion - merken und warten | 53–88 | 1–36 | CTRL_Rumpf · lokale Rotation X, Pause auf 15–25 |

Alle Actions verwenden den Objektslot **Charaktergesten** und sind als Assets gespeichert. Die Rig-Collection **Rigvorlage - Charaktergesten** ist ebenfalls ein Asset. Die Datei ist auf 24 Bilder/s eingerichtet.

## Im Asset Browser

Den Ordner **Animationen** in den Blender-Einstellungen bei **File Paths → Asset Libraries** als Bibliothek hinzufügen. **blender_assets.cats.txt** gehört in diesen Ordner und definiert die Kataloge für Kopf, Reaktion und Rig. Ohne globale Einrichtung lassen sich die Assets in der geöffneten Datei über die Asset-Browser-Quelle **Current File** ansehen oder per **File → Append** übernehmen.

## In eine Produktion übernehmen

1. Die Rig-Collection und die benötigten Actions aus der Bibliothek übernehmen. Die enthaltenen Meshes dienen der Vorschau. Die Rig-Collection lässt sich per **Append → Collection** direkt als editierbare Gruppe laden.
2. Das **Armature-Objekt** wählen. Im **Dope Sheet → Action Editor** eine Action und den Slot **Charaktergesten** auswählen. Für die sequenzielle Demonstration das Armature-Objekt **RIG_Demo_Charaktergesten** im NLA-Editor prüfen. Jeder Strip verwendet denselben Slotnamen der jeweiligen Action.
3. Die Kanäle erwarten **CTRL_Rumpf → CTRL_Kopf → CTRL_Blick** mit Rotation **XYZ Euler**. Die lokale Y-Achse zeigt bei allen drei Steuerknochen in Neutralstellung nach Welt +Z. Der Prüfkörper schaut nach Welt −Y. Bei einem Serienrig mit anderen Namen oder Achsen die Kurven umsetzen und Bewegung samt Nullstellung abgleichen.
4. Die Blickmarker sind Prüfgeometrie. Für Serienfiguren lassen sich stattdessen die Augen- und Pupillenzeichnungen in der [Grease-Pencil-Referenz](../Blender/Grease-Pencil-Gesichtstest.blend) zeichnen und takten.
