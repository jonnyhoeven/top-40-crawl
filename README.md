# top-40-crawl

Springboot as rest api with db connection and `PUT` statement
Python application crawling top 40 music chart data and requesting OpenAI interactions to provision DB.

[reference](https://spring.io/guides/tutorials/rest)

## Scraping

- Scrape from https://www.top40.nl/top40/1965/week-1 to current date.
- Find artist - title, chart position, week, year, image(minimalization needed).
- store to Python binary blobs

## Springboot is my new thing

- Springboot rest API https://spring.io/guides/tutorials/rest
- DB connection
- OpenAI API Java dependency
- rest api input example: PUT title, chart position, week, year, image.
- Check if title + artist has a record in `open-ai-results` then only save week, year, chart position and original data using SQL and skip next step.
- Use OpenAI API and create prompt for artist info, title description, lyrics, genre, bpm, key, keywords, release date and publisher.
- Store call results to db, make sure to include original prompt, model and processing start/end datetimestamp.

## Calling

- Parse Binary blobs and call the Springboot rest API.
- Bonus if rest/swagger results from db are avalailable with a GET request.

## Data model

```sql
CHANGE DATABASE top40
CREATE crawl TABLE
  id            AUTO_NUMERIC,
  title         STRING,
  artist        STRING,
  chart_pos     NUMERIC,
  year          NUMERIC,
  week          NUMERIC,
  image_id      NUMERIC,
  result_id     NUMERIC,
  datetimestamp CURRENT();

CREATE image TABLE
  id            AUTO_NUMERIC,
  url           STRING,
  datetimestamp CURRENT();

CREATE result TABLE
  id            AUTO_NUMERIC,
  model         STRING,
  prompt_type   ENUM,
  prompt        STRING,
  result        STRING,
  crawl_id   many-to-one join to top-40-crawl.id,
  datetimestamp CURRENT();
```

### Check for existing results

```sql
SELECT COUNT(*) FROM crawl
LEFT JOIN result ON result.crawl_id = crawl.id AS r
WHERE  r.title = "title"
  AND r.artist = "artist";
```

### Prompting example

```yaml
model: google/gemma-7b-it
messages:
  - role: system
    content: >2-
      Music top charts parsing.
      Desired format:
      Title: Come A little Bit Closer
      Artist: jay and the americans
      Chart Year: 1965
      Chart Week: 2
      Chart Position: 15
      Title description: -||-
      Artist description: -||-
      Lyrics: -||-
      Genre: -||-
      BPM: -||-
      Key: -||-
      Search Engine Keywords: -||-
      Release date: -||-
      Publisher: -||-
  - role: "user"
    content: >2-
      Output desired format for the following data: 
```

