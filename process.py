from os import environ
import requests
import redis
from dotenv import load_dotenv
from openai import OpenAI

ml_model = "meta-llama/Llama-3-70b-chat-hf"
chart_song_count = 40
scrape_artist_title_delim = ' - '

scrape_baseurl = 'https://www.top40.nl/top40'
load_dotenv()
req_path = environ['REQUEST_PATH']
openapi_key = environ['OPENAI_API_KEY']
openapi_url = environ['API_URL']
redis_host = environ['REDIS_HOST']
redis_port = environ['REDIS_PORT']

client = OpenAI(
    api_key=openapi_key,
    base_url=openapi_url
)

try:
    rds = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
except:
    print('Error: Redis connection failed', redis_host, redis_port)


def retrieve_top40_page(scrape_year, scrape_week):
    u = f'{scrape_baseurl}/{scrape_year}/week-{scrape_week}'
    res = requests.get(u)
    if res.status_code != 200:
        print(f'Error: No 200 response {u}')
        return ''
    return res.text


def parse_top40_page(html):
    return html.split('<div class="top40-list__item__container">')


def retrieve_ml_response(model, messages):
    return client.chat.completions.create(
        model=model,
        messages=messages,
    )


def get_ml_content(c, tag):
    return c.split(tag)[1].split("-||-\n")[0].strip()


def parse_ml_response(r):
    rd = dict()
    c = r.choices[0].message.content
    try:
        rd['title_description'] = get_ml_content(c, "Title description:")
        rd['artist_description'] = get_ml_content(c, "Artist description:")
        rd['genre'] = get_ml_content(c, "Genre:")
        rd['lyrics'] = get_ml_content(c, "Lyrics:")
        rd['bpm'] = get_ml_content(c, "BPM:")
        rd['key'] = get_ml_content(c, "Key:")
        rd['release_date'] = get_ml_content(c, "Release date:")
        rd['publisher'] = get_ml_content(c, "Publisher:")
    except:
        print('Error: Failure parsing response')

    rd['raw_content'] = c
    rd['total_tokens'] = r.usage.total_tokens

    return rd


class Song:
    def __init__(self, year, week, idx, scrape_str):
        self.scrape_str = scrape_str
        self.year = year
        self.week = week
        self.rank = idx + 1

        try:
            x = scrape_str.split('title="Details ')[1].split('"')[0]
            xs = x.split(scrape_artist_title_delim)
            self.artist = xs[0]
            self.title = xs[1]
        except:
            print(f'Error: Failure parsing scrape string {scrape_str}')
            self.artist = 'unknown artist'
            self.title = 'unknown title'

        self.result_key = f'result:{self.artist}-{self.title}'


def __str__(self):
    return f'{self.artist}{scrape_artist_title_delim}{self.title}'


def parse_chart(year, week):
    html = retrieve_top40_page(year, week)
    items = parse_top40_page(html)

    for idx, scrape_str in enumerate(items):
        sng = Song(year, week, idx, scrape_str)

        if sng.rank > chart_song_count:
            break

        print(sng.year, sng.week, sng.rank, sng.artist, scrape_artist_title_delim, sng.title)

        rds.hset(sng.result_key, mapping={
            'artist': sng.artist,
            'title': sng.title,
            'week': sng.week,
            'year': sng.year,
            'rank': sng.rank,
            'result_key': sng.result_key,
        })

        if rds.hgetall(sng.result_key):
            print('Previously processed by ml model')
        else:
            print('Processing ML model: ', ml_model)
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
                               "Publisher: -||-\n"
                },
                {
                    "role": "user",
                    "content": f"Describe the song {sng.title} from the artist {sng.artist} in the desired format"
                }
            ]
            response = retrieve_ml_response(ml_model, messages)

            d = parse_ml_response(response)
            d.update(sng.__dict__)
            rds.hset(sng.result_key, mapping=d)

    for year in range(1965, 2024):
        for week in range(1, 53):
            parse_chart(year, week)
