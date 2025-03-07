# Microcenter Scraper & Monitor
## Overview

This project scrapes open-box items from Microcenter and monitors for new listings. When a new item matching the defined conditions appears, it sends notifications via Discord.  Uses `prefect` to orchestrate workflow.

## Features

* Scrapes open-box items from Microcenter
* Monitors items based on configurable conditions
* Sends alerts via Discord Webhook
* Supports configurable sleep intervals
* Docker support for easy deployment
* `prefect` orchestration

## Installation

### Prerequisites
* Python 3.12 (`prefect server` currently has runtime issues with 3.13)
* uv package manager
* `docker` (optional)

### Setup Virtual Environment & Install Dependencies
1. `uv venv`
2. `uv sync`


## Configuration

Update `config.yaml` to set store URLs, webhook URLs.

Example config.yaml:
```yaml
stores:
  microcenter:
    url: "https://www.microcenter.com/search/search_results.aspx?Ntk=all&sortby=match&prt=clearance&N=4294966938&myStore=false"
    load_cookies: ""

discord:
  webhook_url: "https://your-discord-webhook-url"

```

## Running the Project
### Run Locally
Start `prefect server` first.
1. `prefect server start --host 0.0.0.0`
2. `python main.py --store microcenter`

### Run with Docker

```commandline
docker compose build
docker compose up
```

## License

MIT License