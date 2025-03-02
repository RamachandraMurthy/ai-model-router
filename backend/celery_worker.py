from celery import Celery
from config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND
from loguru import logger
import time

celery_app = Celery("celery_worker", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

@celery_app.task
def process_async_workflow(prompt: str, model: str):
    logger.info(f"Started async workflow for prompt: {prompt} using model {model}")
    # Simulate asynchronous processing (e.g., additional validations, external API calls)
    time.sleep(2)
    response = f"[{model}] Async workflow completed for prompt: {prompt}"
    logger.info(f"Completed async workflow for prompt: {prompt}")
    return response
