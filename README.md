# Pangolin für Home Assistant

Jede öffentliche und private Ressource der konfigurierten Organisation wird als Schalter angelegt. Ein/Aus steuert ausschließlich `enabled`. Statusabfrage und Erkennung neuer Ressourcen alle 30 Sekunden. Gelöschte Ressourcen werden nicht verfügbar. Keine YAML-Konfiguration nötig.

## Installation

Den Ordner `custom_components/pangolin` nach `/config/custom_components/pangolin` kopieren und Home Assistant neu starten. Unter Einstellungen → Geräte & Dienste → Integration hinzufügen nach **Pangolin** suchen.

API-Adresse (beispielsweise `https://api.pangolin.i9o.de/v1`), Organisations-ID und API-Schlüssel eingeben. Der Schlüssel braucht Lese- und Änderungsrechte für öffentliche und private Ressourcen der Organisation. Die API muss von Home Assistant erreichbar sein. TLS-Zertifikate werden geprüft.

## HACS

Dieses Verzeichnis ist als Repository aufgebaut. Für die Installation über HACS muss es zunächst in einem GitHub-Repository veröffentlicht werden. Anschließend dessen URL in HACS als benutzerdefiniertes Repository vom Typ Integration hinzufügen. Noch nicht veröffentlicht oder in HACS gelistet. Vor öffentlicher Veröffentlichung `codeowners` im Manifest auf den tatsächlichen GitHub-Maintainer setzen.

## API

Grundlage: https://api.pangolin.i9o.de/v1/docs/

- Bearer-Authentifizierung.
- GET `/org/{orgId}/public-resources` und `/org/{orgId}/private-resources`, seitenweise.
- POST `/public-resource/{resourceId}` bzw. `/private-resource/{siteResourceId}` mit `{"enabled": true/false}`.
- Erwartete Listen: `data.resources` bzw. `data.siteResources`; private Listen unterstützen alternativ `data.resources`.

Die Swagger-Spezifikation beschreibt die inneren Antwortdaten nicht vollständig. Daher muss das konkrete Antwortformat an der Zielinstanz noch geprüft werden. Es wurden keine echten Ressourcen geschaltet. Home Assistant 2025.1 oder neuer erforderlich; ein vollständiger Laufzeittest in Home Assistant steht aus.
