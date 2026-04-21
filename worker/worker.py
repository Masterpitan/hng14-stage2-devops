import redis
import time
import os
import signal
from dotenv import load_dotenv

load_dotenv()

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    password=os.getenv("REDIS_PASSWORD")
)

running = True


def handle_shutdown(sig, frame):
    global running
    running = False


signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)


def process_job(job_id):
    print(f"Processing job {job_id}")
    time.sleep(2)
    r.hset(f"job:{job_id}", "status", "completed")
    print(f"Done: {job_id}")


if __name__ == "__main__":
    while running:
        try:
            job = r.brpop("job", timeout=5)
            if job:
                _, job_id = job
                process_job(job_id.decode())
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(2)
