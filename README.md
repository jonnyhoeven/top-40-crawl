# Top 40 Crawler

Python client and Springboot REST API service, crawling and augmenting top 40 music charts together...

[reference](https://spring.io/guides/tutorials/rest)


## Scraping

- Scrape some stuff from https://www.top40.nl/top40/1965/week-1.
- Store artist, title, chart position, week, year and image url.
- Store it to Python binary objects for later client replayability against Springboot POC

## Call player client

- Parse binary objects and call the Springboot rest API.

## Springboot POC

- Springboot REST API [Tutorial](https://spring.io/guides/tutorials/rest)
- DB connection
- OpenAI API Java dependency
  - [Azure OpenAI client library for Java](https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/openai/azure-ai-openai)
  - [openai-java by Theo Kanning](https://github.com/TheoKanning/openai-java)
  - Bare REST calls?
- Rest API input example: PUT artist, title, chart position, year, week and image url.
- Insert artist, title, chart position, year, week and image url into TABLE `crawl`.
- Is title + artist in TABLE `result`?
  - No, Use OpenAI API data to and save result, prompt and model name in TABLE `result`.

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


## Data model

```sql
CHANGE DATABASE top40;

CREATE crawl TABLE
  id            AUTO_NUMERIC,
  title         STRING,
  artist        STRING,
  chart_pos     NUMERIC,
  week          NUMERIC,
  year          NUMERIC,
  image_id      NUMERIC,
  result_id     NUMERIC,
  created       CURRENT()
;

CREATE image TABLE
  id            AUTO_NUMERIC,
  url           STRING,
  created       CURRENT()
;

CREATE result TABLE
  id            AUTO_NUMERIC,
  model         STRING,
  input_prompt  STRING,
  output_result STRING,
  title_desc    STRING,
  created       CURRENT()
;
```

### Check for existing results

```sql
SELECT COUNT(*) FROM crawl AS c
LEFT JOIN result ON result.crawl_id = crawl.id AS r
WHERE  c.title = "title"
  AND c.artist = "artist"
;


