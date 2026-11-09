# GRIZE LI? AKCIJE — MVP

Funkcionalna statička web-stranica s pretragom, filtriranjem, sortiranjem i dnevnom automatiziranom provjerom cijena.

## Lokalno pokretanje

```bash
python -m http.server 8000
```

Otvori `http://localhost:8000`. Za provjeru cijena:

```bash
pip install -r requirements.txt
python scripts/check_deals.py
```

## Objavljivanje

1. Otvori novi GitHub repozitorij i prenesi sadržaj ovog direktorija u njegov korijen.
2. U Settings → Pages postavi Deploy from a branch, `main`, `/ (root)`.
3. Stranica će se pojaviti na `https://KORISNIK.github.io/REPO/`.
4. U Actions omogući workflow; `daily.yml` radi svakog dana u 06:15 UTC (07:15/08:15 u Hrvatskoj, ovisno o ljetnom računanju vremena). Moguća su kašnjenja rasporeda.
5. U `sources.json` dodaj dopuštene **pojedinačne URL-ove proizvoda** s dokumentiranom redovnom cijenom; za poznatu najnižu cijenu u 30 dana unesi `lowest_30d`.

Primjer unosa (izmišljena domena, samo prikaz strukture):

```json
{
  "products": [
    {
      "store": "Primjer trgovine",
      "category": "Varalice",
      "url": "https://example.com/proizvod/varalica",
      "regular_price": 25.0,
      "lowest_30d": 25.0
    }
  ]
}
```

**Važno:** Prva verzija namjerno ima prazan popis izvora i ponuda. Ne predstavlja se kao da je provjerila svih 15 trgovina. Skripta čita samo JSON-LD Product/Offer cijene s javnih stranica gdje robots.txt to dopušta. Neki webshopovi ne objavljuju takve podatke, blokiraju botove ili zahtijevaju partner API/feed; za njih je potrebna zasebna integracija uz dopuštenje. Polje `regular_price` je ručno dokumentirano: ova verzija ga **ne ažurira automatski**, pa prije javne komercijalne upotrebe treba izraditi pouzdan automatski izvor referentnih cijena i povijest promjena. Ako je `lowest_30d` naveden, prikazuju se samo ponude koje su barem 15% niže i od tog minimuma. Ako nije, 30-dnevna usporedba nije potvrđena.

Nemoj automatski preuzimati slike i tekst protivno uvjetima trgovina. Prije pokretanja zamijeni identifikaciju bota u `scripts/check_deals.py` valjanim kontaktom. GitHub Pages i Actions imaju uvjete korištenja i ograničenja; za komercijalnu produkciju provjeri odgovarajući hosting i dopuštenost automatizacije.

## Sljedeće nadogradnje

- Administratorski panel za autorizirane izvore i provjeru redovnih cijena
- Baza povijesti cijena i automatski 30-dnevni minimum
- Partner feedovi/API-ji trgovina
- Automatske obavijesti i označavanje affiliate poveznica
- Provjera promjena zaliha, dostave i duplikata
