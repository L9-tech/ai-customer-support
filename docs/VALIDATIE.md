# Technische validatie

Datum: 10 november 2026. Uitvoerder: assistent. Echte klantgegevens zijn niet gebruikt.

De suite bevat 20 geslaagde offline tests. Ze controleren databaseclaims, herhaald aanbieden, menselijke escalatie, gesprekskoppeling met afzendercontrole, lege invoer, HTML-parsing, foutregistratie, alleen-lezen ophalen, verouderde concepten, verzending met onbekende uitkomst, kennisbankversies en API-toegang. Eén test voert de echte Pydantic AI-orkestratie met nagebootste modellen uit, inclusief kennisbanktool en tokenregistratie.

Het React-dashboard is gebouwd met Vite. De browsercontrole test inloggen, zes voorbeeldmails verwerken, een ticket openen, een concept opslaan, de kennisbank en gebeurtenissen openen. Een gevonden probleem met het direct verversen van de audit is hersteld.

Deze controles zijn geen echte OpenAI-evaluatie. De 18 cases in evals/run_evals.py zijn voorbereid, maar niet tegen een model uitgevoerd. Hostinger, SMTP, PostgreSQL/Supabase, Docker en VPS zijn in deze bouwsessie niet live getest. De gebruiker meldde eerder een werkende inboxverbinding voor de oorspronkelijke tester; dat blijft gebruikersbewijs en is geen nieuwe live controle van de uitgebreide adapter.
