# Customer support automation

Oumar Balde · eigen datapunten · 10 november 2026

Deze app bouwt voort op mijn eigen e-mailtester en de leerroute van Dave Ebbelaar. De nieuwe implementatie is met hulp van AI uitgewerkt. Hostinger Mail vervangt Gmail; OpenAI vervangt Anthropic. FastAPI, een aparte poller, PostgreSQL, Pydantic AI, evaluaties, een React-dashboard en Docker volgen de onderdelen uit de leerroute.

## Online omgeving

De app staat op https://support.oumarbalde.com. Het doel is de echte mailbox- en AI-koppeling met privétoegang. De server en PostgreSQL zijn gecontroleerd. De live AI-evaluatie wacht op API-tegoed; zie [de actuele validatie](docs/VALIDATIE.md) en [live installatie](docs/LIVE_INSTALLATIE.md).

## Lokale demo voor ontwikkeling

Start `./start-demo.command` en open http://127.0.0.1:8080. Gebruik de lokaal ingestelde dashboardgegevens. De launcher zet alleen voor dit proces demo-instellingen. Klik op **Voorbeeldmails verwerken**. De zes fictieve e-mails worden tickets. Je kunt een gesprek openen, een concept aanpassen, gebeurtenissen bekijken en de kennisbank wijzigen.

De demo werkt zonder mailbox, modelaanroepen of PostgreSQL. De vaste demoregels zijn uitdrukkelijk geen test van AI-kwaliteit. De oorspronkelijke `.env` blijft behouden.

Handmatig starten vanuit de projectmap:

```sh
APP_MODE=demo DASHBOARD_PASSWORD='<eigen lokaal wachtwoord>' uv run uvicorn app.main:app --host 127.0.0.1 --port 8080
```

## Lokale controle

```sh
APP_MODE=demo PYDANTIC_AI_NO_BANNER=1 uv run python -m unittest discover -s tests -v
cd dashboard
pnpm install --frozen-lockfile
pnpm run build
```

De unittestset gebruikt tijdelijke databases en nagebootste mail- en modelantwoorden. De Pydantic AI-test controleert wel de echte agentroute, de kennisbanktool en tokenregistratie; hij doet geen OpenAI-verzoek. De browsercontrole is apart vastgelegd in `docs/VALIDATIE.md`.

## Echte verbindingen

Controleer de variabelen in `.env.example` en vul de eigen `.env` aan. `APP_MODE=live` vereist een eigen PostgreSQL-database, OpenAI-sleutel, mailboxgegevens en een dashboardwachtwoord van minstens 16 tekens. Modelnamen moeten beschikbaar zijn voor het gebruikte account. Geheime waarden horen niet in Git, Notion, screenshots of bewijsbestanden.

1. Gebruik een aparte testmailbox en testdatabase. Initialiseer de database met de SQL in `supabase/migrations/` of `uv run python -m app.seed`. Het backendaccount moet de tabellen kunnen beheren; bij Supabase zijn de publieke tabellen door RLS afgeschermd.
2. Controleer en vervang het voorbeeldbeleid in `knowledge_base/`. Het korte onderwijsvoorbeeld is geen volledige kopie van de cursuskennisbank en geen bevestigd bedrijfsbeleid.
3. Zet `APP_MODE=live`, houd `ENABLE_SENDING=false` en start de API opnieuw. Bij de eerste **Mailbox controleren** wordt een beginwaarde opgeslagen en worden bestaande berichten overgeslagen. Volgende controles halen nieuwe berichten op en kunnen OpenAI gebruiken. Daarbij gaan berichtteksten en maximaal acht opgeslagen gespreksberichten naar OpenAI.
4. Voer de echte modelevaluatie apart uit: `uv run python -m evals.run_evals --live`. Dit maakt betaalde modelaanroepen, maar verstuurt geen mail. Bekijk elke afwijking; een geslaagde offline test zegt niets over de semantische kwaliteit van de modelantwoorden.
5. Start voor periodieke verwerking een tweede proces: `uv run python -m app.poller`. Gebruik één poller. De database claimt elk bericht voordat de verwerking begint.
6. Zet pas voor een gecontroleerde verzendtest `ENABLE_SENDING=true`. De ingelogde medewerker moet het exacte opgeslagen concept bevestigen. De poller verstuurt niets automatisch. Dit is een bewuste afwijking van de automatische cursusroute.

## Gegevensstroom

```text
Hostinger IMAP → parser → claim in events → ticket en messages
                                         ↓
                          classifier → kennisbanktools → concept
                                         ↓
                             Pythonregels → review of escalated
                                         ↓
                       medewerker → SMTP → uitgaand bericht + audit
```

De sleutel bevat account, map, UIDVALIDITY en UID. Berichtnummers alleen zijn niet genoeg. Gesprekken worden gekoppeld via References/In-Reply-To en dezelfde afzender; onderwerpregels alleen zijn geen bewijs van een gesprek. De database is leidend voor de verwerkingsstatus, niet UNSEEN of niet gegarandeerd ondersteunde IMAP-labels. Alleen gesprekken die deze app heeft opgeslagen, worden als historie gebruikt.

`review` betekent concept klaar; `escalated` betekent menselijke beoordeling; `sent` betekent SMTP heeft het bericht geaccepteerd. `delivery_unknown` blokkeert automatisch opnieuw verzenden wanneer het resultaat onzeker is. Controleer dan het unieke uitgaande Message-ID in de audit en de mailbox. Een ontbrekende kopie in Sent na SMTP-succes veroorzaakt geen tweede verzending.

## Wat nog een echte controle nodig heeft

IMAP- en SMTP-login, PostgreSQL, Docker en HTTPS zijn gecontroleerd. Echte AI-antwoorden zijn nog niet gevalideerd omdat het API-tegoed ontbreekt. De volledige mailroute en verzending moeten nog worden getest. Er is geen automatische geldteruggave, orderwijziging of verzending van producten. De applicatie levert voorstellen en conceptantwoorden. Kosten in euro worden niet verzonnen: alleen gerapporteerde tokenaantallen worden opgeslagen.

Bij een crash kan een event op `processing` blijven staan. Controleer eerst dat de oude poller gestopt is en inspecteer het event. Een beheerder kan alleen zo'n niet verzendend event bewust op `failed` zetten voor een nieuwe poging. Na drie mislukte pogingen blijft het bericht zichtbaar als Verwerking mislukt. Na herstel van de oorzaak kan de medewerker het ticket opnieuw vrijgeven met Opnieuw verwerken en Mailbox controleren. Een verzendstatus wordt nooit met een algemene retry teruggezet.

## Docker en server

```sh
docker compose up -d --build api
# Alleen na eigen live configuratie:
docker compose --profile live up -d poller
```

De API bindt in Compose uitsluitend aan de loopbackinterface. Open de serveromgeving via een SSH-tunnel: `ssh -L 8080:127.0.0.1:8080 gebruiker@jouw-server`. De handleiding `docs/CURSUS_EN_LEERUITKOMSTEN.md` maakt per onderdeel duidelijk wat is gebouwd, aangepast en nog te valideren. Voor de eigen Hostinger VPS is een subdomein met HTTPS ingericht. Gebruik `compose.live.yaml` voor de eigen PostgreSQL-database. De laatste status staat in `docs/VALIDATIE.md`.

## Leerroute

Datalumina: https://learn.datalumina.com/docs/customer-support-automation

De code is een eigen, op dit project aangepaste implementatie. De zes kennisbanksecties zijn een beknopt, geparafraseerd onderwijsvoorbeeld. De originele e-mailtester blijft als bewijs bewaard in `bewijs_oorspronkelijk/`.
