# Technische validatie

Datum: 10 november 2026. Uitvoerder: assistent. Testvragen zijn fictief. Er is geen e-mail verstuurd.

## Code en interface

27 offline tests slagen lokaal. Ze controleren onder andere claims, herhaalde invoer, afzendercontrole, escalatie, lege data, MIME/HTML, BODY.PEEK, conceptversies, onzekere verzending, kennisbankversies en API-authenticatie. Vier tests controleren de beginwaarde voor nieuwe mail. Twee aanvullende tests controleren herstel na modeluitval en bewust opnieuw vrijgeven na drie fouten. De echte Pydantic AI-orkestratie is apart uitgevoerd met nagebootste modellen en kennisbanktools.

TypeScript en de Vite-productiebuild slagen. De browsercontrole van de eerdere demo omvat inloggen, zes voorbeeldmails, ticketdetails, concept opslaan, kennisbank, gebeurtenissen en mobiele weergave. Na privéactivatie zijn inloggen, de live status, de AI-pauzemelding en de handmatige mailboxcontrole in de browser gecontroleerd. Er was nog geen nieuw live ticket om de herstelknop op te bedienen; de herstelroute is wel met de geautomatiseerde tests gecontroleerd.

## Echte infrastructuur en mailbox

De webapp draait op de eigen Hostinger VPS achter Caddy met HTTPS. De PostgreSQL-container is healthy en heeft geen publieke databasepoort. Een integratietest in een apart schema verwerkt zes fictieve berichten tot twee concepten en vier escalaties; opnieuw aanbieden geeft zes duplicates. De beginwaarde voor nieuwe mail is ook in PostgreSQL getest. Dit is databasebewijs, geen AI-kwaliteitsbewijs.

Alle 27 tests slagen ook in het Linux Docker-image op de VPS zonder netwerk, in 2,068 seconden. Een eerdere run liep vast op leesrechten van gemounte testcode; na mode 644 voor dat niet-geheime bestand slaagde de suite. De eindrun omvat ook de hersteltests en de test dat AI-pauze geen provider aanroept.

Een nieuwe echte IMAP-login, alleen-lezen INBOX-selectie en SMTP-login zijn vanaf de ontwikkelmachine geslaagd. Er zijn daarbij geen berichtteksten gelezen. SMTP-login bewijst niet dat een antwoord is verstuurd.

## Echte AI-evaluatie

De OpenAI-sleutel is geldig en modeltoegang voor gpt-6-luna is bevestigd. De eerste poging met achttien fictieve evaluatievragen is geblokkeerd door HTTP 429 / credit_balance_exhausted. Er zijn nul modelresultaten. Dit levert geen kwaliteitspercentage op: het API-account moet eerst worden aangevuld.

De evaluatierunner is hersteld voor de vereiste datasetnaam. Daarna is toegevoegd dat de eerste providercontrole buiten de dataset plaatsvindt: bij ontbrekend tegoed stopt de run na één mislukte vraag. Een aparte lokale controle met nagebootste antwoorden bevestigt achttien geregistreerde successen en stoppen na één providerfout. Die controle doet geen API-verzoek.

## Nog te bewijzen

De privéomgeving is geactiveerd. API en database zijn healthy, de poller draait en de eerste mailboxcontrole heeft 41 bestaande berichten overgeslagen. Een handmatige browsercontrole gaf nul nieuwe berichten en nul fouten. De live database bevatte bij de eindcontrole nul tickets en één mailboxbeginwaarde.

Nog open: na een toekomstige keuze om API-tegoed toe te voegen de echte modeluitkomsten beoordelen, één nieuw binnengekomen eigen testbericht door de volledige route volgen en de bruikbaarheid met een medewerker testen. Een echte gebruikerstest en AI-engineerreview zijn niet uitgevoerd. Supabase is niet gebruikt: de server heeft een eigen PostgreSQL-database.

De extra pauzetest bevestigt dat `AI_ENABLED=false` geen modelprovider aanroept. Oumar heeft aangegeven nu geen API-tegoed toe te voegen; daarom blijft AI-verwerking bewust gepauzeerd.
