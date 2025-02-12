api_registry = {
    "job_get": {
        "type": "api",
        "url": "https://jsonplaceholder.typicode.com/posts/1",
        "method": "GET",
        "params": None,
        "credentials": {},
    },
    "job_posting_post": {
        "type": "api",
        "url": "https://jsonplaceholder.typicode.com/posts",
        "method": "POST",
        "params": {
            "data": {"title": "temporary", "body": "temporary", "userId": 1}
        },
        "credentials": {},
    },
    "firecrawl_scrape": {
        "type": "api",
        "url": "https://api.firecrawl.dev/v1/scrape",
        "method": "POST",
        "params": {
            "url": "string which is url to be scraped",
            "formats": ["markdown"]
        },
        "credentials": {"bearer": "FIRECRAWL_API_KEY"},
    },
    "gemini": {
        "type": "llm",
        "model": "Gemini",
        "model_type": "gemini-2.0-flash-exp",
        "credentials": {"env": "GEMINI_API_KEY"},
        "prompt": "Tell me a joke."
    }
}