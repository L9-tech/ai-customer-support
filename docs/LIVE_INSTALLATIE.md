# Live installatie op Hostinger

De webapp en HTTPS staan op https://support.oumarbalde.com. De broncode staat op https://github.com/L9-tech/ai-customer-support. Een bereikbare webapp is nog geen werkende AI-koppeling: live modus vereist de instellingen hieronder.

## Benodigde instellingen

- `APP_MODE=live`
- `OPENAI_API_KEY`: een eigen OpenAI-projectsleutel, alleen in de lokale en serverconfiguratie.
- `CLASSIFIER_MODEL=openai:gpt-6-luna`
- `AGENT_MODEL=openai:gpt-6.1-sol`
- Hostinger mailboxadres en mailboxwachtwoord, IMAP 993 en SMTP 465 met TLS.
- `DATABASE_URL`: PostgreSQL op de interne Docker-host `db`, database en gebruiker `support`.
- Een privé `DASHBOARD_PASSWORD` van minstens 16 tekens.
- `ENABLE_SENDING=false` totdat verzenden bewust wordt vrijgegeven.

De app gebruikt de OpenAI Responses API. De modelnamen zijn teruggevonden in de officiële documentatie; daadwerkelijke toegang in het account moet met de eigen sleutel worden getest.

## Database en starten

`compose.live.yaml` voegt een aparte PostgreSQL-container met een persistent volume toe. PostgreSQL heeft geen gepubliceerde hostpoort. Het databasewachtwoord staat in `secrets/postgres_password`, buiten Git. De map en het bestand moeten alleen voor de serverbeheerder leesbaar zijn.

Na het veilig invullen van `.env`:

```sh
docker compose -f compose.yaml -f compose.live.yaml --profile live up -d --build
```

De API blijft op `127.0.0.1:8080` gebonden. Caddy verzorgt HTTPS. De poller maakt concepten en escalaties, maar verstuurt nooit automatisch mail.

## Eerste mailboxcontrole

Bij de eerste controle wordt de hoogste bestaande UID vastgelegd. Bestaande berichten worden niet inhoudelijk opgehaald of door AI verwerkt. Alleen later binnengekomen berichten worden verwerkt. De beginwaarde blijft bewaard bij een herstart. Bij een nieuwe UIDVALIDITY wordt een nieuwe beginwaarde vastgelegd.

Dit voorkomt een onverwachte import van de volledige bestaande inbox. Er is nog geen functie om oudere berichten alsnog te importeren.

## Controles vóór gebruik

1. Controleer `/health`, de containerstatus en de databaseverbinding.
2. Voer `python -m evals.run_evals --live` uit met de eigen sleutel. Deze evaluatie gebruikt fictieve tekst, geen mailbox. Dit maakt betaalde API-aanroepen.
3. Log privé in en initialiseer de mailbox. Controleer dat de bestaande inbox is overgeslagen.
4. Laat een eigen nieuwe testmail binnenkomen. Controleer ticket, gebruikte kennisbankbron, concept, verwerkingsstatus en tokens.
5. Beoordeel de kennisbank. De meegeleverde Harbor & Pine-informatie is cursusmateriaal en geen vastgesteld beleid van een echt bedrijf.
6. Verzenden blijft een aparte menselijke handeling. Een SMTP-login bewijst nog geen geslaagde verzending.

## Gecontroleerd op 10 november 2026

- HTTPS en Docker op de VPS werken.
- 27 offline tests en de TypeScript/productiebuild slagen lokaal.
- Echte IMAP-login, INBOX-selectie en SMTP-login slagen vanaf de ontwikkelmachine. Er zijn daarbij geen berichtteksten gelezen en geen mails verstuurd.
- De OpenAI-sleutel is ingevuld en geldig. Modelgeneratie is geblokkeerd door ontbrekend API-tegoed (429 / credit_balance_exhausted). De privéconfiguratie wordt klaargezet; volledige live verwerking is nog niet gevalideerd.

Bronnen: [Datalumina](https://learn.datalumina.com/docs/customer-support-automation), [Pydantic AI OpenAI](https://pydantic.dev/docs/ai/models/openai/), [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna), [GPT-6.1 Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol).

Op verzoek is geen API-tegoed toegevoegd. De live omgeving gebruikt daarom `AI_ENABLED=false`. Nieuwe mail kan worden vastgelegd, maar er worden geen modelaanroepen gedaan. Na aanvullen van tegoed zijn een geslaagde echte evaluatie, `AI_ENABLED=true` en herstart nodig. Mislukte verwerking kan via het dashboard opnieuw worden vrijgegeven.
