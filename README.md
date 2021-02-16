# zsolozsma
Élő zsolozsma- és miseközvetítések szöveggel: https://zsolozsma.herokuapp.com

Soha nem használtam még "éles" projektben Pythont, Djangót, PostgreSQL-t vagy Herokut, úgyhogy majd úgy javul a kód, ahogy tanulom ezeket ;-)

## Adatbázis

![Adatbázisséma](docs/db.png?raw=true "Adatbázisséma")

## API

Minden közvetítéseket listázó oldal eredménye elérhető JSON formátumban is, a `?json` paraméter hozzáadásával. Az eredmények mindig a következő 3 nap közvetítéseit tartalmazzák.

### Válasz formátuma

```
[{
    "date": "YYYY-MM-DD", 
    "time": "HH:MM:SS", 
    "city": "Település", 
    "location": "Helyszín", 
    "name": "Szertartás helyi elnevezése", 
    "state": Közvetítés állapota, 
    "url": "Hivatkozás a közvetítés oldalára"
},
..]
```

A közvetítés állapota a következő értékeket veheti fel:
|`state`|A közvetítés elvileg...|
|---|---|
|1| több, mint 15 perc múlva kezdődik|
|2| 15 percen belül kezdődik|
|3| élőben megy|
|4| legfeljebb 15 perce ért véget|

*A közvetítések befejezése becsült érték, így elképzelhető, hogy az adott napon a közvetítés hamarabb véget ért vagy elhúzódik.*

### URL-ek

| URL | Leírás |
|---|---|
|/|Minden közvetítés|
|/szertartas/`szertartás`|Egy szertartás (pl. `szentmise`) közvetítései|
|/felekezet/`felekezet`[/`település`]|Egy felekezet/rítus (pl. `gorog-katolikus`) szertartásainak közvetítései, opcionálisan egy adott településre leszűkítve (pl. `gorog-katolikus`/`miskolc`) |
|/varos/`település`[/`helyszín`]|Egy település (pl. `budapest`) vagy egy konkrét helyszín (pl. `budapest`/`pasaret`) közvetítései |

### Példa

`https://zsolozsma.herokuapp.com/szertartas/szentmise/?json`

```
[
    {
        "date": "2021-02-16",
        "time": "16:00:00",
        "city": "Szeged",
        "location": "Móraváros",
        "name": "Szentmise",
        "state": 3,
        "url": "https://zsolozsma.herokuapp.com//kozvetites/6acdf3b4/2021-02-16/"
    },
    {
        "date": "2021-02-16",
        "time": "17:00:00",
        "city": "Csíksomlyó",
        "location": "Kegytemplom",
        "name": "Szentmise",
        "state": 1,
        "url": "https://zsolozsma.herokuapp.com//kozvetites/d78232c5/2021-02-16/"
    },
    {
        "date": "2021-02-16",
        "time": "17:00:00",
        "city": "Déva",
        "location": "Böjte Csaba",
        "name": "Szentmise",
        "state": 1,
        "url": "https://zsolozsma.herokuapp.com//kozvetites/eae7c12d/2021-02-16/"
    },
    ...
]
```