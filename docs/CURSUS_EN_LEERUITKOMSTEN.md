# Cursusroute en twee eigen datapunten

De referentie is https://learn.datalumina.com/docs/customer-support-automation. De vervolgpagina's zijn op 10 november 2026 geraadpleegd. Hun voorbeelden worden gebruikt als inhoudelijke leerroute, niet als opdrachten om zonder controle productieaccounts te wijzigen.

| Cursusonderdeel | Projectbestand | Uitwerking en grens |
|---|---|---|
| Project setup | app/config.py, pyproject.toml | Settings en bestaande dependencies behouden en uitgebreid |
| Mailtoegang en mailclient | app/hostinger.py | Hostinger IMAP/SMTP; echte login gecontroleerd, nieuwe-mailroute privé geactiveerd |
| Poller | app/poller.py | Afzonderlijk proces; batchverwerking en databaseclaims |
| Database | app/db.py, supabase/migrations | Eigen PostgreSQL in live; Supabase niet gevalideerd; SQLite uitsluitend voor demo en tests |
| Eerste antwoord | app/main.py | Bewerken en bewust verzenden van een concept; standaard uit |
| Knowledge base | knowledge_base, app/seed.py | Zes secties, revisies, kennisbankeditor; beknopt voorbeeldbeleid |
| AI pipeline | app/ai, app/pipeline.py | Pydantic AI met OpenAI, classifier, kennisbanktools, beslisregels en menselijke controle |
| Evals | tests, evals/run_evals.py | Offline technische tests en aparte set van 18 echte modelevaluaties |
| Dashboard | dashboard/src | React, tickets, gesprekken, gebeurtenissen, tokengebruik, kennisbank; eigen CSS in plaats van shadcn |
| Server en Docker | Dockerfile, compose.yaml | Docker, PostgreSQL en Caddy met HTTPS op de eigen VPS uitgevoerd |

## Datapunt 1 Volledig technisch dossier voor LU1 en LU4

Het eerste datapunt bevat de hele technische documentatie: eigen e-mailtester, verdere customer support-app, cursuskeuzes, gegevensstroom, code, testbewijs, live servercontrole, bronnen en alle relevante Notionnotities. LU1 onderbouwt de methodische aanpak en controles; LU4 de vertaling van een concreet supportprobleem naar een beroepsproduct.

De eigen eerste IMAP-code is apart bewaard. De uitbreiding en technische controles zijn op verzoek met AI-hulp uitgevoerd. Echte IMAP- en SMTP-authenticatie, PostgreSQL en Docker zijn gecontroleerd. Alle 27 offline tests slagen lokaal en op de server. De OpenAI-evaluaties leverden geen antwoorden wegens ontbrekend API-tegoed; de live AI-route blijft daarom zichtbaar gepauzeerd. De kwaliteit van echte modelantwoorden en bruikbaarheid voor een medewerker zijn nog niet aangetoond.

## Datapunt 2 Review en presentatie voor LU2 en LU3

De gekozen activiteit is een technische peer review en presentatie met een echte AI engineer. Samen één concreet probleem kiezen, taken afspreken, een wijziging uitvoeren en hertesten vormt het beoogde bewijs voor LU2. Uitleggen, luisteren, doorvragen, de uitleg aanpassen en besluiten bevestigen vormt het beoogde bewijs voor LU3.

De reviewopzet, taakverdeling, presentatievragen en bewijsregistratie zijn voorbereid. De reviewer, het gesprek en gezamenlijke resultaat zijn nog niet vastgelegd. Dit is dus nog geen afgerond datapunt. Na uitvoering worden feedback, eigen en gezamenlijke bijdrage, wijziging, hertest en persoonlijke reflectie toegevoegd. AI-hulp geldt niet als bewijs van menselijke samenwerking.

## Gezamenlijke reflectie in het schoolformat

Gebruik het aangeleverde document Reflectie eigen datapunten. Neem beide datapunten op in de matrix en beschrijf per LU1 tot en met LU4: ontwikkeldoel, concreet bewijs, verband met het doel en reflectie. LU5 beschrijft ontwikkeling en vervolgstappen. Maak het verschil zichtbaar tussen eigen code, AI-uitwerking, technische tests en eigen uitleg. Persoonlijke ervaringen, gesprekken en resultaten worden pas ingevuld als ze werkelijk zijn beschreven of uitgevoerd.

## Volgende demonstratie

Open de offline demo, verwerk zes berichten en controleer dat opnieuw verwerken geen dubbele tickets maakt. Toon één concept, één escalatie en de kennisbank. Leg daarna met een echte tester vast welke vraag hij moest beantwoorden, welke keuze hij maakte, waar hij vastliep en welke verbetering volgde. Herhaal na een wijziging dezelfde taak. Koppel deze bewijzen aan het gezamenlijke reflectiedocument en de feedbackbundel.
