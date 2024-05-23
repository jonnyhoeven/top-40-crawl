# Top 40 crawler

- Crawls every weekly top 40 from 1956 till presents.
- Augment results using OpenAI API.
- Store everything in redis
- Get youtube music metadata and video url from
  api https://ytmusicapi.readthedocs.io/en/stable/reference.html#ytmusicapi.YTMusic.search

## Overview

Ik wilde eerste de OpenAI en YouTube API in een SpringBoot rest API zetten, echter kwam ik er al snel achter dat
de meeste web resultaten van OpenAI en Springboot naar de mogelijkheid om je swagger api te documenteren.
Wat ik dus niet wil, ik wilde een simpele API die ik kon gebruiken om data te verrijken en op te slaan in Redis.
Voorlopig wel wat kunnen doen met springboot, met name het opzetten een nieuw project en environment config.

The top 40 website https://www.top40.nl/top40/1965/week-1 bevat data vanaf 1965 met elke week de top 40 van die week.
Het script crawlt deze data en slaat deze op in Redis met de prefix `charts`.

Hierna volgt een OpenAI API call om de data te verrijken:

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

In totaal zijn er ongeveer 125.000 chart entries, elke combinatie van `artiest-titel` zal worden opgezocht in de OpenAI API
Daarnaast gebruiken we de Youtube Music API om de videourl en metadata op te halen, deze resultaten worden opgeslagen
in Redis met de prefix `result`. De youtube API geeft niet altijd de beste resultaten, met name als er album 
resultaten worden weergegeven i.p.v. song resultaten.

Aan het einde van de rit kunnen we bepalen hoeveel unieke nummers we hebben kunnen vinden en verrijken.

Goede volgende stap zou zijn om de data in een SQL db te zetten, en met wat queries op een frontend applicatie te tonen.



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
echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs)
main" | sudo tee /etc/apt/sources.list.d/redis.list
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

