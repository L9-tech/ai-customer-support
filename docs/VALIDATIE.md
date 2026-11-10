# Technische validatie

Datum: 10 november 2026. Uitvoerder: assistent. Testvragen zijn fictief. Er is geen e-mail verstuurd.

## Code en interface

27 offline tests slagen lokaal. Ze controleren onder andere claims, herhaalde invoer, afzendercontrole, escalatie, lege data, MIME/HTML, BODY.PEEK, conceptversies, onzekere verzending, kennisbankversies en API-authenticatie. Vier tests controleren de beginwaarde voor nieuwe mail. Twee aanvullende tests controleren herstel na modeluitval en bewust opnieuw vrijgeven na drie fouten. De echte Pydantic AI-orkestratie is apart uitgevoerd met nagebootste modellen en kennisbanktools.

TypeScript en de Vite-productiebuild slagen. De browsercontrole van de eerdere demo omvat inloggen, zes voorbeeldmails, ticketdetails, concept opslaan, kennisbank, gebeurtenissen en mobiele weergave. De nieuwe live herstelknop wacht nog op de browsercontrole na privéactivatie.

## Echte infrastructuur en mailbox

De webapp draait op de eigen Hostinger VPS achter Caddy met HTTPS. De PostgreSQL-container is healthy en heeft geen publieke databasepoort. Een integratietest in een apart schema verwerkt zes fictieve berichten tot twee concepten en vier escalaties; opnieuw aanbieden geeft zes duplicates. De beginwaarde voor nieuwe mail is ook in PostgreSQL getest. Dit is databasebewijs, geen AI-kwaliteitsbewijs.

De eerdere suite van 24 tests slaagt ook in het Linux Docker-image zonder netwerk. De eerste run van de nieuwe testfile liep vast op leesrechten van de gemounte testcode; na mode 644 voor dat niet-geheime bestand slaagden alle 24. De twee laatste hersteltests zijn lokaal geslaagd en moeten nog in het nieuwe serverimage worden herhaald.

Een nieuwe echte IMAP-login, alleen-lezen INBOX-selectie en SMTP-login zijn vanaf de ontwikkelmachine geslaagd. Er zijn daarbij geen berichtteksten gelezen. SMTP-login bewijst niet dat een antwoord is verstuurd.

## Echte AI-evaluatie

De OpenAI-sleutel is geldig en modeltoegang voor gpt-6-luna is bevestigd. De eerste poging met achttien fictieve evaluatievragen is geblokkeerd door HTTP 429 / credit_balance_exhausted. Er zijn nul modelresultaten. Dit levert geen kwaliteitspercentage op: het API-account moet eerst worden aangevuld.

De evaluatierunner is hersteld voor de vereiste datasetnaam. Daarna is toegevoegd dat de eerste providercontrole buiten de dataset plaatsvindt: bij ontbrekend tegoed stopt de run na één mislukte vraag. Een aparte lokale controle met nagebootste antwoorden bevestigt achttien geregistreerde successen en stoppen na één providerfout. Die controle doet geen API-verzoek.

## Nog te bewijzen

Na aanvullen van API-tegoed: echte evaluatie-uitkomsten en controle van de antwoorden, privé live activeren, één nieuw binnengekomen testbericht door de volledige route volgen en de interface opnieuw beoordelen. Een echte gebruikerstest en AI-engineerreview zijn niet uitgevoerd. Supabase is niet gebruikt: de server heeft een eigen PostgreSQL-database.

De extra pauzetest bevestigt dat `AI_ENABLED=false` geen modelprovider aanroept. Oumar heeft aangegeven nu geen API-tegoed toe te voegen; daarom blijft AI-verwerking bewust gepauzeerd.
