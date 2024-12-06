from fastapi import FastAPI
from REST_API import dtt_class
from REST_API.dtt_class import *
from query_processor import QueryProcessor
from cachetools import cached, TTLCache
import hashlib
import json

# tmux attach -t fastapi
# ctrl + B, D -> 세션 나오기
# ctrl + C -> fastapi 종료
# uvicorn main:app --host 0.0.0.0 --port 8000 --reload -> 다시 실행

app = FastAPI()

cache = TTLCache(maxsize=100, ttl=60)


def generate_cache_key(request_data):
    request_json = json.dumps(request_data, sort_keys=True)
    return hashlib.md5(request_json.encode()).hexdigest()


@app.get("/")
async def read_root():
    return {"watch-me root directory"}


@app.post("/main_page/")
async def main_page_query(item: MainPage):
    cache_key = generate_cache_key(item.model_dump(exclude_none=True))
    if cache_key in cache:
        return {"movies": cache[cache_key]}

    query_processor = QueryProcessor()
    result = query_processor.process_main_page(item)
    cache[cache_key] = result

    return {"movies": result}


@app.post("/search_page/")
async def search_page_query(item: SearchPage):
    cache_key = generate_cache_key(item.model_dump(exclude_none=True))
    if cache_key in cache:
        return {"movies": cache[cache_key]}

    query_processor = QueryProcessor()
    result = query_processor.process_search_page(item)
    cache[cache_key] = result

    return {"movies": result}
