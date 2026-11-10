# Cursusroute en twee eigen datapunten

De referentie is https://learn.datalumina.com/docs/customer-support-automation. De vervolgpagina's zijn op 10 november 2026 geraadpleegd. Hun voorbeelden worden gebruikt als inhoudelijke leerroute, niet als opdrachten om zonder controle productieaccounts te wijzigen.

| Cursusonderdeel | Projectbestand | Uitwerking en grens |
|---|---|---|
| Project setup | app/config.py, pyproject.toml | Settings en bestaande dependencies behouden en uitgebreid |
| Mailtoegang en mailclient | app/hostinger.py | Hostinger IMAP/SMTP; echte login gecontroleerd, nieuwe-mailroute privé geactiveerd |
| Poller | app/poller.py | Afzonderlijk proces; batchverwerking en databaseclaims |
| Database | app/db.py, supabase/migrations | PostgreSQL/Supabase in live; SQLite uitsluitend voor demo en tests |
| Eerste antwoord | app/main.py | Bewerken en bewust verzenden van een concept; standaard uit |
| Knowledge base | knowledge_base, app/seed.py | Zes secties, revisies, kennisbankeditor; beknopt voorbeeldbeleid |
| AI pipeline | app/ai, app/pipeline.py | Pydantic AI met OpenAI, classifier, kennisbanktools, beslisregels en menselijke controle |
| Evals | tests, evals/run_evals.py | Offline technische tests en aparte set van 18 echte modelevaluaties |
| Dashboard | dashboard/src | React, tickets, gesprekken, gebeurtenissen, tokengebruik, kennisbank; eigen CSS in plaats van shadcn |
| Server en Docker | Dockerfile, compose.yaml | Docker, PostgreSQL en Caddy met HTTPS op de eigen VPS uitgevoerd |

## Datapunt 1 Mijn e-mailtester als gegevensbron

Vraag: hoe haal ik e-mail betrouwbaar en controleerbaar op als mogelijke invoer voor customer support?

Eigen bijdrage: keuze voor Hostinger en OpenAI, eerste IMAP-code, configuratievragen, correcties op klassenaam en instellingen, statuscontrole en UID-zoekopdracht. Het eigen bestand van vóór de uitbreiding is apart bewaard. De gebruiker meldde eerder dat verbinden en de inbox openen werkte. De nieuwe adapter, parser en tests zijn door de assistent uitgewerkt op verzoek van de gebruiker.

Bewijs: oorspronkelijke code, logboek, offline controle, huidige adapter, testgevallen voor lege inbox en fouten. Dit ondersteunt onderdelen van LU1 en LU4. Het bewijst nog niet zelfstandig het volledige data-analyseproces.

## Datapunt 2 Customer support verwerking en beoordeling

Vraag: hoe helpt de datastroom een supportmedewerker kiezen tussen een onderbouwd conceptantwoord en menselijke opvolging?

Product: verwerking, database, kennisbank, twee modelrollen, beslisregels, dashboard en evaluatieopzet. Offline is zichtbaar hoe zes synthetische mails tot tickets, concepten en escalaties leiden. De nieuwe implementatie en technische controles zijn met AI gemaakt. Echte modelkwaliteit en bruikbaarheid voor een medewerker moeten nog worden getest.

Bewijs: code, schema, demo, screenshot, technische testresultaten, evaluatiecases en vastgelegde beperkingen. Dit ondersteunt onderdelen van LU1 en LU4. Voor LU3 is een demonstratie met een echte belanghebbende en verwerkt advies nodig. Voor LU2 ontbreken een menselijke samenwerkingspartner, afspraken en een gezamenlijk resultaat. AI-hulp geldt niet als bewijs dat die samenwerking plaatsvond.

## Gezamenlijke reflectie in het schoolformat

Gebruik het aangeleverde document Reflectie eigen datapunten. Neem beide datapunten op in de matrix en beschrijf per LU1 tot en met LU4: ontwikkeldoel, concreet bewijs, verband met het doel en reflectie. LU5 beschrijft ontwikkeling en vervolgstappen. Maak het verschil zichtbaar tussen eigen code, AI-uitwerking, technische tests en eigen uitleg. Persoonlijke ervaringen, gesprekken en resultaten worden pas ingevuld als ze werkelijk zijn beschreven of uitgevoerd.

## Volgende demonstratie

Open de offline demo, verwerk zes berichten en controleer dat opnieuw verwerken geen dubbele tickets maakt. Toon één concept, één escalatie en de kennisbank. Leg daarna met een echte tester vast welke vraag hij moest beantwoorden, welke keuze hij maakte, waar hij vastliep en welke verbetering volgde. Herhaal na een wijziging dezelfde taak. Koppel deze bewijzen aan het gezamenlijke reflectiedocument en de feedbackbundel.
