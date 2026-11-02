import asyncio
from celery import shared_task
from .crawler import run_async_crawler

@shared_task
def crawl_snappfood():
    asyncio.run(run_async_crawler())