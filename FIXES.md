# FIXES.md

All bugs found in the starter repository, documented with file, original line number, problem, and fix applied.

---

## api/main.py

**Bug 1 — Hardcoded Redis host**
- Original line 8: `r = redis.Redis(host="localhost", port=6379)`
- Problem: `localhost` hardcodes the Redis host. Inside a container or multi-host environment this fails because Redis runs as a separate service, not on localhost.
- Fix (line 12): Changed to `host=os.getenv("REDIS_HOST", "localhost")`.

**Bug 2 — Hardcoded Redis port**
- Original line 8: `port=6379` hardcoded inline
- Problem: Port is not configurable without changing source code.
- Fix (line 14): Changed to `port=int(os.getenv("REDIS_PORT", 6379))`.

**Bug 3 — Redis password never loaded or used**
- Original line 8: No `password` argument passed to `redis.Redis()`
- Problem: The `.env` file defined `REDIS_PASSWORD` but it was never read or passed to the Redis client, meaning Redis ran without authentication despite a password being set.
- Fix (line 15): Added `password=os.getenv("REDIS_PASSWORD")`.

**Bug 4 — `.env` file never loaded**
- Original: No `load_dotenv()` call anywhere in the file
- Problem: Even if `os.getenv()` calls were present, the `.env` file would never be read without `python-dotenv` being invoked.
- Fix (lines 6, 8): Added `from dotenv import load_dotenv` and `load_dotenv()` before the Redis client is initialised.

**Bug 5 — Missing 404 status on job not found**
- Original line 20: `return {"error": "not found"}` returned with implicit `200 OK`
- Problem: Returning a `200` response with an error body is incorrect HTTP semantics. Clients and proxies treat it as a success.
- Fix (line 31): Changed to `return JSONResponse(status_code=404, content={"error": "not found"})`. Added `from fastapi.responses import JSONResponse` import on line 2.

---

## api/requirements.txt

**Bug 6 — Missing `python-dotenv` dependency**
- Original: only `fastapi`, `uvicorn`, `redis` listed
- Problem: `load_dotenv()` requires `python-dotenv`. Without it the package import fails and the API crashes on startup.
- Fix: Added `python-dotenv` on line 4.

---

## api/.env

**Bug 7 — Real password committed to source control**
- Original line 1: `REDIS_PASSWORD=supersecretpassword123`
- Problem: A real credential was committed to the repository. Anyone with read access to the repo has the password.
- Fix: Replaced with `REDIS_PASSWORD=your_redis_password_here`. A `.env.example` file was also created with all required variables so contributors know what to set.

**Bug 8 — Missing `REDIS_HOST` and `REDIS_PORT` variables**
- Original: Only `REDIS_PASSWORD` and `APP_ENV` were defined
- Problem: The fixed application reads `REDIS_HOST` and `REDIS_PORT` from the environment. Without them defined, the defaults (`localhost`, `6379`) are used, which breaks in containers.
- Fix: Added `REDIS_HOST=redis` on line 1 and `REDIS_PORT=6379` on line 2.

---

## worker/worker.py

**Bug 9 — Hardcoded Redis host**
- Original line 6: `r = redis.Redis(host="localhost", port=6379)`
- Problem: Same as api/main.py — `localhost` does not resolve to the Redis container.
- Fix (line 10): Changed to `host=os.getenv("REDIS_HOST", "localhost")`.

**Bug 10 — Hardcoded Redis port**
- Original line 6: `port=6379` hardcoded
- Fix (line 11): Changed to `port=int(os.getenv("REDIS_PORT", 6379))`.

**Bug 11 — Redis password never loaded or used**
- Original line 6: No `password` argument, no `load_dotenv()`
- Problem: Worker connects to Redis without authentication, which will be rejected if Redis requires a password.
- Fix (lines 5, 7, 12): Added `from dotenv import load_dotenv`, `load_dotenv()`, and `password=os.getenv("REDIS_PASSWORD")`.

**Bug 12 — `signal` imported but never used**
- Original line 4: `import signal` present but no signal handlers were registered anywhere
- Problem: The import was dead code — no graceful shutdown was implemented despite the intent being there.
- Fix (lines 18–24): Wired up `handle_shutdown` as a handler for both `SIGTERM` and `SIGINT`, setting `running = False` to allow the loop to exit cleanly.

**Bug 13 — Bare `while True` loop at module level with no shutdown path**
- Original lines 14–18: `while True:` loop runs unconditionally at import time with no way to stop it
- Problem: The worker cannot be stopped gracefully. It also runs if the file is imported rather than executed directly.
- Fix (lines 33–42): Wrapped the loop in `if __name__ == "__main__":` and replaced `while True` with `while running`, controlled by the signal handlers.

**Bug 14 — No error handling in the worker loop**
- Original lines 14–18: No `try/except` around the Redis call or job processing
- Problem: Any Redis connection error or exception in `process_job` would crash the worker process permanently with no recovery.
- Fix (lines 35–42): Wrapped the loop body in `try/except Exception`, prints the error, and sleeps 2 seconds before retrying.

---

## worker/requirements.txt

**Bug 15 — `redis` dependency unpinned**
- Original line 1: `redis` with no version constraint
- Problem: A future breaking release of the `redis` package could be installed, causing silent or hard-to-debug failures.
- Fix: Pinned to `redis==5.0.1` on line 1.

**Bug 16 — Missing `python-dotenv` dependency**
- Original: only `redis` listed
- Problem: `load_dotenv()` requires `python-dotenv`. Without it the worker crashes on startup.
- Fix: Added `python-dotenv==1.0.0` on line 2.

---

## frontend/app.js

**Bug 17 — Hardcoded `API_URL`**
- Original line 6: `const API_URL = "http://localhost:8000";`
- Problem: `localhost` does not resolve to the API container. The frontend will fail to reach the API in any containerised deployment.
- Fix (line 8): Changed to `const API_URL = process.env.API_URL || "http://localhost:8000";`.

**Bug 18 — No CSRF protection on state-changing routes**
- Original lines 10–11: `app.use(express.json())` and `app.use(express.static(...))` with no CSRF middleware
- Problem: The `/submit` POST route accepts requests from any origin with no token validation, making it vulnerable to cross-site request forgery (CWE-352).
- Fix (lines 4–5, 12–13, 16–18): Added `csurf` and `cookie-parser` middleware. Added a `GET /csrf-token` endpoint so the frontend can fetch a token before submitting.

**Bug 19 — SSRF via unvalidated `req.params.id` (CWE-918)**
- Original lines 21–22: `axios.get(\`${API_URL}/jobs/${req.params.id}\`)` with no validation
- Problem: Any string passed as `:id` is interpolated directly into the upstream URL. An attacker could craft a value that causes the server to make requests to internal services.
- Fix (lines 9, 31–33): Added `JOB_ID_REGEX = /^[0-9a-f-]{36}$/` and a validation check that returns `400` if the ID does not match a valid UUID format.

---

## frontend/package.json

**Bug 20 — Missing `csurf` and `cookie-parser` dependencies**
- Original: only `express` and `axios` listed
- Problem: `app.js` requires `csurf` and `cookie-parser`. Without them declared, `npm install` will not install them and the app crashes on startup.
- Fix: Added `"csurf": "^1.11.0"` and `"cookie-parser": "^1.4.6"` to `dependencies`.

---

## frontend/views/index.html

**Bug 21 — No CSRF token fetched or sent with POST requests**
- Original lines 21–26: `submitJob()` called `fetch('/submit', { method: 'POST' })` with no token
- Problem: With CSRF protection enabled on the server, POST requests without a valid token are rejected with `403`.
- Fix (lines 21–31): Added `csrfToken` variable and `init()` function that fetches `/csrf-token` on page load, then passes the token as a `CSRF-Token` header in `submitJob`.

**Bug 22 — No error handling in `submitJob` or `pollJob`**
- Original lines 21–35: Both functions had no `try/catch`. Network errors or API errors would throw unhandled promise rejections with no user feedback.
- Fix (lines 33–57): Wrapped both functions in `try/catch`. Errors are displayed in the `#result` div or rendered inline on the job entry.

---

## Root (missing files)

**Bug 23 — No `.gitignore`**
- Problem: Without a `.gitignore`, the `.env` file, `node_modules/`, and Python cache directories would be committed to the repository, leaking credentials and bloating git history.
- Fix: Created `.gitignore` covering `.env`, `node_modules/`, `__pycache__/`, `*.pyc`, `*.pyo`, `.pytest_cache/`, `.coverage`, and `htmlcov/`.

**Bug 24 — No `.env.example`**
- Problem: No reference file existed to tell contributors which environment variables are required. The only `.env` had a real password in it.
- Fix: Created `.env.example` at the repo root with all required variables (`REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`, `APP_ENV`, `API_URL`) set to safe placeholder values.
