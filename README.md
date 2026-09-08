# Basketkalender

En statisk GitHub Pages-sida som jämför basketmatcher från Profixio (primär
källa) med SportAdmin. Python hämtar, tolkar, matchar och genererar JSON före
publicering; webbläsaren får aldrig kalender-URL:er eller credentials.

## Lokal installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

Fyll i `PROFIXIO_CALENDAR_URL` i `.env`. Filen är ignorerad av Git och får inte
delas. `SPORTADMIN_CALENDAR_URL` kan också anges där.

## Uppdatera och visa lokalt

```bash
source .venv/bin/activate
PYTHONPATH=src python -m basket_calendar.cli build
python -m http.server 8000 --directory build/site
```

Öppna `http://localhost:8000`. Sidan läser enbart `data/matches.json`; inga
kalenderadresser, tokens eller råa ICS-filer kopieras till den publicerade
webbplatsen.

## Testa

```bash
PYTHONPATH=src:. pytest -q
```

Tester omfattar iCalendar-tidszoner, saknade fält, dubbletter, normalisering,
fältjämförelse och säkra/osäkra matchningar.

## Matchning

Profixio är primär källa: varje dess matchhändelse blir en rad. SportAdmin
filtreras till händelser med två lag i det observerade formatet
`Match: hemma - borta`. Kandidater måste ha samma svensk lokal dag och vara
högst två timmar från varandra. Poängen består av datum (30 %), tid (20 %),
hemma- och bortalag (25 % vardera) samt arena (5 %).

Båda lagen måste dessutom var för sig nå minst 65 % textlikhet. En arena kan
alltså aldrig ensam skapa en matchning. Minst 85 % blir `matched_confident`,
70–84 % blir `matched_probable`; nära konkurrerande kandidater blir
`ambiguous`.

## Säker drift och felhantering

Skapa följande GitHub Actions-secrets under **Settings → Secrets and variables
→ Actions**:

- `PROFIXIO_CALENDAR_URL` — obligatorisk, full signerad URL.
- `SPORTADMIN_CALENDAR_URL` — rekommenderas också som secret även om den
  för närvarande verkar mindre känslig.

Workflowen körs dagligen och kan startas manuellt. Den testar koden, hämtar
kalendrar, vägrar skapa ny version om Profixio har färre än fem användbara
matcher (justera `MIN_PROFIXIO_MATCHES` medvetet vid lågsäsong), och deployar
först därefter en GitHub Pages-artifact. Ett fel lämnar tidigare publicerad
version orörd.

Välj **Settings → Pages → Source: GitHub Actions** efter första pushen.
Felsökning sker i Actions-loggen; URL-frågesträngar maskeras i programmets
felmeddelanden. Ändra aldrig `.env` till en spårad Git-fil.
