# Fixpoint

An API to search and scrape web data about companies and people.

Connect live company and people data, web search, and scraping in one API to
power your AI agents, applications, or analytics.

<h3>

[Homepage](https://www.fixpoint.co/) | [Documentation](https://docs.fixpoint.co/) | [Discord](https://discord.gg/tdRmQQXAhY) | [Examples](https://github.com/gofixpoint/fixpoint/tree/main/examples)

</h3>

## Table of contents

- [Why Fixpoint?](#why-fixpoint)
- [Examples](#examples)
- [Getting started](#getting-started)


## Why Fixpoint?

Normally, to get the right company and people data, you need to buy and combine
datasets from dozens of providers, bolt on custom web-scraping code, and review
data quality manually.

Instead, you can integrate Fixpoint's API and get all of the above.

## Examples

Some examples:

- [Using AI to crawl a website and extract structured data](https://docs.fixpoint.co/examples/extract-crawl)
- [Parse a website (or web crawl) into LLM-ready text](https://docs.fixpoint.co/examples/parse-site)


## Getting started

Fixpoint is a Python package. First, install it:

```bash
pip install fixpoint
```

```python
from fixpoint.client import FixpointClient
from fixpoint.client.types import CreateRecordExtractionRequest, CrawlUrlSource

client = FixpointClient(api_key="...")

extraction = client.extractions.record.create(
    CreateRecordExtractionRequest(
        workflow_id="my-workflow-id",
        source=CrawlUrlSource(crawl_url="https://fixpoint.co", depth=2, page_limit=3),
        questions=[
            "What is the product summary?",
            "What are the industries the business serves?",
            "What are the use-cases of the product?",
            "According to the privacy policy, what data is collected from users?",
        ],
    )
)

print(extraction.model_dump_json(indent=2))
```

See [our docs](https://docs.fixpoint.co/) for more features and how-to's!
