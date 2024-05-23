# Top 40 crawler

- Crawls every weekly top 40 from 1956 till presents.
- Augment results using OpenAI API.
- Store everything in redis

## Todo

- [ ] Get youtube music metadata and video url from
  api https://ytmusicapi.readthedocs.io/en/stable/reference.html#ytmusicapi.YTMusic.search

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