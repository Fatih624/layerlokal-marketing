# Lokales Pino-Produktionsstudio

Start.cmd startet die lokale HTML-Leitstelle mit Python 3.11 oder neuer. Git muss verfügbar sein. Der bestehende Desktop-Starter ruft diese Datei auf. Das Studio liest die HTML-Dateien und das Arbeitsbuch direkt aus Studio/. Die Arbeitsquellen im Bereich GitHub kommen aus Pino-Produktion/.

„Aktuellen Stand abrufen“ holt origin/main des Marketing-Repositorys mit git pull --ff-only und lädt nach Erfolg das Handbuch neu. Git meldet Konflikte oder Verbindungsfehler im Studio. Der angezeigte Commit bezeichnet den lokalen Git-Stand. Browserentwürfe werden separat im Browser gespeichert und lassen sich im Bereich GitHub exportieren.

Für eine gemeinsame Buchversion alle geänderten Studio-Dateien einschließlich buch.js, Seitenbildern und Arbeitsbuch.pdf zusammen versionieren. Änderungen an Markdown-Quellen erscheinen beim Abruf direkt unter Arbeitsquellen. Die gesetzten Buchseiten bilden die zuletzt eingecheckte Buchausgabe ab.

## Moodboard (Bereich C)

Im Moodboard sammelst du Inspiration aus dem Internet: Figuren, Schauplätze, Licht & Farbe, Animation und Marketing.

- **Suchen:** Suchbegriff eingeben und eine Quelle wählen, zum Beispiel Pinterest, Behance, ArtStation, Google Bilder oder Openverse für frei lizenzierte Bilder. Die Suche öffnet sich in einem neuen Tab.
- **Hinzufügen:** Bild kopieren und in der Leitstelle mit Strg+V einfügen, ein Bild hineinziehen, eine Datei wählen oder einen Bild- oder Seitenlink einfügen. Bei Seitenlinks verwendet die Leitstelle das Vorschaubild der Seite.
- **Ordnen:** Mit einem Klick aufs Bild ergänzt du Titel, Bereich, Tags, eine Notiz und die Quelle. Oben filterst du nach Bereich, Tag oder Suchtext. Die Farbwelt zeigt die Hauptfarben der sichtbaren Bilder. Ein Klick auf eine Farbe kopiert ihren Hex-Code.
- **Speicherort:** Der lokale Server lädt die Bilder herunter und legt sie in `Studio/moodboard/bilder/` ab, die Angaben in `Studio/moodboard/moodboard.json`. Externe Bilder lädt die Seite aus Sicherheitsgründen nicht direkt. Die Bilder bleiben so auch erhalten, wenn der Originallink verschwindet. Eingefügte Bilder werden auf höchstens 1800 px verkleinert.
- **Teilen:** Neue Bilder sind lokale Änderungen im Repository. Committe und pushe sie wie gewohnt auf einen eigenen Branch, dann sieht Yasin sie im Pull Request.
- Achte bei Bildern aus dem Internet auf das Urheberrecht. Das Moodboard dient als interne Inspiration. Für Veröffentlichungen nur eigene oder frei lizenzierte Bilder verwenden.
