# Flagship 26/27 Binder

Verzamelmap-app voor Topps Flagship Premier League 2026/27, gedeeld tussen twee telefoons.
Vanilla HTML/JS, geen build-stap. Backend: Supabase. Hosting: GitHub Pages.

## Opzetten (eenmalig, ~15 minuten)

### 1. Supabase
1. Maak een gratis project op supabase.com (regio: eu-central).
2. Open **SQL Editor**, plak `supabase/schema.sql`, vervang het tweede e-mailadres in de `members`-tabel door dat van je partner, en voer uit.
3. Plak `supabase/seed.sql` en voer uit (zet de 205 afgevinkte kaarten erin).
4. **Authentication > Providers > Email**: laat "Enable email provider" aan. Zet "Confirm email" uit is niet nodig; magic links werken standaard.
5. **Authentication > URL Configuration**: zet *Site URL* op je GitHub Pages-adres (bijv. `https://nintemank.github.io/flagship-binder/`) en voeg hetzelfde adres toe bij *Redirect URLs*.
6. **Project Settings > API**: kopieer *Project URL* en *anon public key*.

### 2. Config
Kopieer `config.example.js` naar `config.js` en vul URL en anon key in.
`config.js` staat in `.gitignore`. Voor GitHub Pages moet hij wel mee: haal de regel uit `.gitignore` of commit hem bewust.
De anon key is bedoeld voor in de browser; de toegang wordt afgedwongen door Row Level Security (alleen e-mailadressen in `members`).

### 3. GitHub Pages
1. Nieuwe repo `flagship-binder`, push deze map.
2. **Settings > Pages**: Source = *Deploy from a branch*, branch `main`, folder `/ (root)`.
3. Na een minuut staat hij op `https://<gebruikersnaam>.github.io/flagship-binder/`.

### 4. Op de telefoon
Open het adres in Chrome, log in met je e-mailadres (link komt per mail), en kies in het Chrome-menu **Installeren** of **Toevoegen aan startscherm**. De ander doet hetzelfde met haar adres.

## Gebruik
- Tik op een kaart: afvinken. Vasthouden: één exemplaar eraf. "Dubbelen tellen" aan: elke tik telt +1.
- "Foto van deze kant": fotografeer een kant van de map recht van boven; de app knipt hem in 12 vakjes. "Bijsnijden" om de randen bij te schuiven.
- "Kopieer mislijst": de nummers die je nog zoekt, klaar om te plakken.
- Alles synct direct tussen jullie telefoons. Offline afvinken kan; het wordt verstuurd zodra er verbinding is.

## Bestanden
- `index.html`: de hele app (data, weergave, sync).
- `config.js`: Supabase-gegevens.
- `sw.js`, `manifest.json`, `icons/`: PWA.
- `supabase/schema.sql`: tabellen, RLS, storage. `supabase/seed.sql`: beginstand.
