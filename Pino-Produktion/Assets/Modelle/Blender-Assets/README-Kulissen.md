# Riegerplatz · Kulissen

**Riegerplatz-Kulissen.blend** enthält zwei einzeln importierbare Collection-Assets aus den vorhandenen texturierten Meshy-FBX-Exporten. Beide liegen mit dem tiefsten Mesh-Punkt auf Z = 0 und haben ihren Ursprung mittig am Boden. +Z zeigt nach oben, −Y zur Vorderseite.

| Asset | Breite × Tiefe × Höhe | Dreiecke im FBX | Dreiecke im Asset |
| --- | --- | ---: | ---: |
| Riegerplatz - Parkbank | 1,700 × 1,126 × 1,143 m | 280.570 | 10.000 |
| Riegerplatz - Altbau-Fassadenmodul | 4,714 × 4,120 × 12,000 m | 260.734 | 25.000 |

Die Reduktion übernimmt die UVs aus dem FBX. Basisfarbe, Metall, Rauheit und Normalen sind mit dem Principled BSDF verbunden und in der Blender-Datei gepackt. Die Bank behält die Proportionen des Exports bei 1,70 m Breite. Beim Fassadenmodul sind Front, Seiten und Rückseite wie im Export gestaltet. Die Eingangstür und Fenster sind Bestandteil des Fassadenmeshs.

## Verwenden

1. In der eigenen Blender-Datei **Datei → Anhängen → Collection** wählen und die gewünschte Collection öffnen. Beide Assets erscheinen auch im Asset Browser der Bibliotheksdatei unter **Current File**.
2. Die Collection auf dem gewünschten Boden platzieren. In der Bibliothek können Bank und Fassade separat in den beiden Eevee-Szenen betrachtet werden. Studio, Licht und Kamera gehören zu den Vorschau-Szenen.

[Vorschau Parkbank](Riegerplatz-Parkbank-Vorschau.png) · [Vorschau Fassade](Riegerplatz-Fassade-Vorschau.png)

Die unveränderten herstellerseitigen ZIPs mit hochaufgelöstem FBX und Texturen liegen unter [Prop-Parkbank](../Meshy-Originale/Prop-Parkbank) und [Prop-Fassade](../Meshy-Originale/Prop-Fassade).
