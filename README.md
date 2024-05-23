# Top 40 crawler

- Crawls every weekly top 40 from 1956 till present.
- Augment results using OpenAI API.
- Get youtube music metadata and video url from
  api https://ytmusicapi.readthedocs.io/en/stable/reference.html#ytmusicapi.YTMusic.search
- Store everything in Redis

De [NL Top 40](https://www.top40.nl/top40/1965/week-1) website bevat data vanaf 1965 met elke week de top 40 van die week.
Dit Python script crawlt `Yaar`, `Maand`, `Week`, `Rank`, `Artiest` en `Titel`. En word opgeslagen in Redis met de prefix `charts`

Na het opslaan van chart song data zijn er 2 verschillende calls, OpenAI API en Youtube Music API.

Eerst OpenAI, er zijn geen interdependecies, het is bij beide de inputs `artist` en `title`.

```text
{
    "role": "system",
    "content": "You will reply to music titles and artists in this desired format:\n" +
               "Title description: -||-\n" +
               "Artist description: -||-\n" +
               "Genre: -||-\n" +
               "Lyrics: -||-\n" +
               "BPM: -||-\n" +
               "Key: -||-\n" +
               "Release date: -||-\n" +
               "Publisher: -||-\n"
},
{
    "role": "user",
    "content": f"Describe the song {sng.title} from the artist {sng.artist} in the desired format"
}
```

Met als resultaat:

```text
Here is the description of the song "Ringo" by Lorne Greene:

Title description: A narrative song about a gunslinger named Ringo, inspired by the popularity of the Ringo Starr, the drummer of The Beatles -||-
Artist description: Lorne Greene, a Canadian actor and musician, best known for his roles in the TV series Bonanza and Battlestar Galactica -||-
Genre: Country/Folk -||-
Lyrics: The song tells the story of a mysterious and deadly gunslinger named Ringo, with lyrics that paint a vivid picture of the American West -||-
BPM: 96 -||-
Key: C Major -||-
Release date: 1964 -||-
Publisher: RCA Victor -||-
```

In totaal zijn er ongeveer 125.000 chart entries, elke unieke combinatie met `result:artiest-titel` zal opgezocht worden in de OpenAI
API zolang er geen eerdere `key` is gevonden met `result:artiest-titel` in Redis.

Gemiddeld kost een call 200~300 tokens per request met `Lama 30b chat`.

Hierna gaat een Youtube Music API open call uit om met de string `artist - title` de eerste `song` uit de gemengde resultaten van YouTube music API te geven `thumbnail_url`, `video_url` en `duration` pakt het script op, maar er zit veel meer in de api.

De resultaten worden opgeslagen met key `result:artist-title` in Redis.

# Volgende stappen 

- Volgende stap zou zijn om de data in een SQL db te zetten, en met wat queries op een frontend applicatie te tonen.
- Uitbreiden YouTube API scraping, `views`, `Related Artist`, `Album` enzo.

Voorlopig heb ik weer wat nieuwe muziek ontdekt.

## Requirements

### Environment variables

Copy the `.env.example` file to `.env` and fill in the required values.

```bash
cp .env.example .env
```

### Python

Install python3, pip and requirements

```bash
pip install -r requirements.txt
```

### Redis stack server

```markdown
curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
sudo chmod 644 /usr/share/keyrings/redis-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list
sudo apt-get update
sudo apt-get install redis-stack-server
sudo service redis-server start
```

### Redis insight

https://redis.io/insight/

### Run the process script

```bash
python3 process.py
```

