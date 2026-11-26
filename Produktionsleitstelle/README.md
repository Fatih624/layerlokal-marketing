# Lokales Pino-Produktionsstudio

Start.cmd startet die lokale HTML-Leitstelle mit Python 3.11 oder neuer. Git muss verfügbar sein. Der bestehende Desktop-Starter ruft diese Datei auf. Das Studio liest die HTML-Dateien und das Arbeitsbuch direkt aus Studio/. Die Arbeitsquellen im Bereich GitHub kommen aus Pino-Produktion/.

„Aktuellen Stand abrufen“ holt origin/main des Marketing-Repositorys mit git pull --ff-only und lädt nach Erfolg das Handbuch neu. Git meldet Konflikte oder Verbindungsfehler im Studio. Der angezeigte Commit bezeichnet den lokalen Git-Stand. Browserentwürfe werden separat im Browser gespeichert und lassen sich im Bereich GitHub exportieren.

Für eine gemeinsame Buchversion alle geänderten Studio-Dateien einschließlich buch.js, Seitenbildern und Arbeitsbuch.pdf zusammen versionieren. Änderungen an Markdown-Quellen erscheinen beim Abruf direkt unter Arbeitsquellen. Die gesetzten Buchseiten bilden die zuletzt eingecheckte Buchausgabe ab.
