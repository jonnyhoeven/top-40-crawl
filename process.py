from os import environ
import requests
import redis

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
req_path = environ['REQUEST_PATH']
api_key = environ['OPENAI_API_KEY']
api_url = environ['API_URL']
default_model = "meta-llama/Llama-3-70b-chat-hf"

client = OpenAI(
    api_key=api_key,
    base_url=api_url
)

r = redis.Redis(host='localhost', port=6379, decode_responses=True)


def retrieve_top40(scrape_year, scrape_week):
    u = f'https://www.top40.nl/top40/{scrape_year}/week-{scrape_week}'
    r = requests.get(u)
    if r.status_code != 200:
        print(f'Error: No 200 response {u}')
        return ''
    return r.text


def parse_top40_page(html):
    return html.split('<div class="top40-list__item__container">')


def retrieve_ml_response(model, messages):
    return client.chat.completions.create(
        model=model,
        messages=messages,
    )


def parse_ml_response(r):
    rd = dict()
    m = r.choices[0].message.content
    try:
        rd['title_description'] = m.split("Title description:")[1].split("-||-\n")[0].strip()
        rd['artist_description'] = m.split("Artist description:")[1].split("-||-\n")[0].strip()
        rd['genre'] = m.split("Genre:")[1].split("-||-\n")[0].strip()
        rd['lyrics'] = m.split("Lyrics:")[1].split("-||-\n")[0].strip()
        rd['bpm'] = m.split("BPM:")[1].split("-||-\n")[0].strip()
        rd['key'] = m.split("Key:")[1].split("-||-\n")[0].strip()
        rd['release_date'] = m.split("Release date:")[1].split("-||-\n")[0].strip()
        rd['publisher'] = m.split("Publisher:")[1].split("-||-")[0].strip()
        rd['total_tokens'] = r.usage.total_tokens
    except:
        rd['title_description'] = f'Error: {r.choices[0].message.content}'
    return rd


for year in range(1965, 2024):

    for week in range(1, 53):

        html = retrieve_top40(year, week)

        items = parse_top40_page(html)

        for rank, hit in enumerate(items):
            if rank == 40:
                break
            x = hit.split('title="Details ')[1].split('"')[0]
            artist = x.split(' - ')[0]
            title = x.split(' - ')[1]
            rkey = f'result:{artist}-{title}'
            print(year, week, rank + 1, artist, '-', title)

            r.hset(f'charts:{year}-{week}-{rank + 1}', mapping={
                'title': title,
                'artist': artist,
                'result_key': rkey,
            })

            if r.hgetall(f'result:{artist}-{title}'):
                print('Already processed')
            else:
                print('Processing')
                messages = [
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
                                   "Publisher: -||-"
                    },
                    {
                        "role": "user",
                        "content": f"Describe the song {title} from the artist {artist} in the desired format"
                    }
                ]
                response = retrieve_ml_response(default_model, messages)

                d = parse_ml_response(response)
                d['artist'] = artist
                d['title'] = title
                d['week'] = week
                d['year'] = year
                d['rank'] = rank + 1

                r.hset(rkey, mapping=d)
