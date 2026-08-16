# Here are your Instructions
Here’s a complete README.md you can add to the repository.

````markdown name=README.md url=https://github.com/rahul111152/nasuki-localsubaccountpahse2/blob/main/README.md
# NASUKI — Local Subaccount Phase 2

NASUKI is a small demo app that demonstrates an Emergent keyless Google authentication flow backed by a FastAPI + MongoDB backend and a TypeScript / Expo mobile frontend. The backend exchanges a one-time Emergent `session_id` for a 7‑day session token and stores lite user/session data in MongoDB. The frontend obtains the one‑time `session_id` (web or native) and sends it to the backend.

Quick links
- Backend main: `backend/server.py`
- Frontend root: `frontend/` (Expo + TypeScript)
- Frontend config: `frontend/src/constants/config.ts` (set `EXPO_PUBLIC_BACKEND_URL` here via env)
- Emergent auth helper: `frontend/src/services/auth/emergent-auth.ts`

Table of contents
- What this is
- Requirements
- Environment variables
- Quick start (backend + frontend)
- Frontend: configuring backend URL & auth flow
- API reference
- Testing
- Troubleshooting
- Contributing

What this is
- A FastAPI backend that:
  - Exchanges Emergent one-time `session_id` to a 7-day `session_token` via the Emergent session-data endpoint.
  - Upserts a user in MongoDB and stores user sessions with TTL expiry.
  - Provides simple status-check and auth endpoints under the `/api` prefix.
- A TypeScript / Expo frontend that:
  - Handles Emergent keyless auth flows (web + native).
  - Stores session tokens securely (Keychain / SecureStore) and user profiles in local SQLite.
  - Calls backend endpoints via a single API client (`frontend/src/services/api-client.ts`).

Requirements
- Backend:
  - Python 3.10+
  - MongoDB accessible (local or Atlas)
  - pip
- Frontend:
  - Node.js (LTS), npm or yarn
  - Expo (development) / Expo Dev Client or production build for native Google flow

Environment variables

Backend (.env placed in `backend/` — `server.py` loads ROOT_DIR/'.env'):
- MONGO_URL (required) — MongoDB connection string
- DB_NAME (required) — database name to use
- EMERGENT_AUTH_SESSION_URL (optional) — default:
  `https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data`
- CORS_ORIGINS (optional) — comma-separated list or `*` (defaults to `*`)

Frontend:
- EXPO_PUBLIC_BACKEND_URL — backend base URL used by the frontend (set before running Expo)
  - Example: `EXPO_PUBLIC_BACKEND_URL=http://192.168.1.100:8000`

Quick start

1) Clone the repo
```bash
git clone https://github.com/rahul111152/nasuki-localsubaccountpahse2.git
cd nasuki-localsubaccountpahse2
```

2) Backend (local development)
```bash
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows (PowerShell)

pip install -r backend/requirements.txt

# Create backend/.env (example)
cat > backend/.env <<EOF
MONGO_URL=mongodb://localhost:27017
DB_NAME=nasuki
# Optional overrides:
# EMERGENT_AUTH_SESSION_URL=https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data
# CORS_ORIGINS=*
EOF

# Run
uvicorn backend.server:app --reload --host 0.0.0.0 --port 8000
```
- Health endpoint: `GET http://localhost:8000/api/` → `{"message":"NASUKI API","status":"ok"}`

3) Frontend (Expo)
```bash
cd frontend
npm install           # or yarn install

# Start expo with backend URL set (examples)
EXPO_PUBLIC_BACKEND_URL=http://localhost:8000 npm run start
# For Android emulator (host -> emulator address)
EXPO_PUBLIC_BACKEND_URL=http://10.0.2.2:8000 npm run start
# For physical device, replace with your machine IP:
EXPO_PUBLIC_BACKEND_URL=http://192.168.1.100:8000 npm run start
```
- The frontend reads `process.env.EXPO_PUBLIC_BACKEND_URL` in `frontend/src/constants/config.ts` and composes API calls as `${BACKEND_URL}/api/...`.

Frontend: configuring backend URL & auth flow (details)
- Where to configure backend URL:
  - `frontend/src/constants/config.ts` defines `BACKEND_URL`:
    ```ts
    export const BACKEND_URL = (process.env.EXPO_PUBLIC_BACKEND_URL ?? "").replace(/\/+$/, "");
    ```
  - Set the environment variable `EXPO_PUBLIC_BACKEND_URL` before running Expo so the app uses absolute URLs. If left empty, the client will call relative `/api/*` paths.
- How auth flow is wired:
  - `frontend/src/services/auth/emergent-auth.ts` handles getting a one-time `session_id`:
    - Web: `EmergentAuth.beginWebRedirect()` navigates to Emergent auth and returns with `session_id` in URL → use `EmergentAuth.readWebCallback()` on page load to extract it.
    - Native: `EmergentAuth.openNativeAuth()` opens an in-app browser and returns a `session_id` via redirect / deep link.
  - `frontend/src/services/auth-service.ts`:
    - `signInWithGoogle()` triggers EmergentAuth and then calls `completeGoogleSession(sessionId)`.
    - `completeGoogleSession(sessionId)` calls `api.createSession(sessionId)` which posts to `${BACKEND_URL}/api/auth/session`.
    - On success the code:
      - Stores `session_token` in secure storage (never in SQLite or logs).
      - Upserts user in local SQLite and activates user.
    - `restoreSession()` uses `api.me(token)` to validate/refresh the session on startup.
- Web callback handling suggestion:
  - On app start (root component) check:
    ```ts
    import { EmergentAuth } from "@/src/services/auth/emergent-auth";
    import { AuthService } from "@/src/services/auth-service";

    const sessionId = EmergentAuth.readWebCallback();
    if (sessionId) {
      EmergentAuth.clearWebCallback();
      await AuthService.completeGoogleSession(sessionId);
      // navigate to app home
    }
    ```
  - This extracts `session_id` from the URL hash or query and exchanges it with the backend.

API reference (main endpoints)
- POST /api/auth/session
  - Body: `{ "session_id": "<one-time-id>" }`
  - Response: `{ "session_token": "<token>", "user": { user fields } }`
- GET /api/auth/me
  - Header: `Authorization: Bearer <session_token>`
  - Response: public user
- POST /api/auth/logout
  - Header: `Authorization: Bearer <session_token>`
  - Response: `{ ok: true }`
- GET /api/ (health)
- POST /api/status, GET /api/status — small status-check endpoints

Testing
- Backend tests configured via `backend/pytest.ini`. Run from repo root:
```bash
pip install -r backend/requirements.txt
pytest
```
- Frontend tests depend on project config; consult `frontend/package.json` scripts.

Troubleshooting
- If frontend returns network errors:
  - Ensure `EXPO_PUBLIC_BACKEND_URL` is set to an address reachable from your device/emulator.
  - Use `10.0.2.2` for Android emulator to reach host machine `localhost`.
  - For physical devices, use the host machine IP on the same LAN.
- If auth exchange fails with 502:
  - Backend couldn't reach Emergent endpoint. Check `EMERGENT_AUTH_SESSION_URL` and network egress.
- If `api.me` returns 401:
  - Session token expired or invalid — user must re-authenticate.
- If Mongo errors on startup:
  - Confirm `MONGO_URL` and `DB_NAME` in `backend/.env` and that Mongo is running/accessible.

Security notes
- Session tokens are stored in secure storage only (`STORAGE_KEYS.sessionToken`).
- Tokens are never logged and never saved to SQLite/AsyncStorage.
- Demo login exists for development only and is gated by `AUTH.devAuthEnabled`.

Where to look next in the code
- Backend:
  - `backend/server.py` — main FastAPI app, routes, Mongo indexes.
  - `backend/requirements.txt` — dependencies.
- Frontend:
  - `frontend/src/constants/config.ts` — BACKEND_URL and storage keys.
  - `frontend/src/services/api-client.ts` — how requests are composed.
  - `frontend/src/services/auth-service.ts` — session lifecycle and storage.
  - `frontend/src/services/auth/emergent-auth.ts` — obtaining `session_id` on web/native.

Contributing
- Open issues and PRs are welcome. If you add features:
  - Keep session tokens in secure storage only.
  - Preserve local profile data across sign-out as per design.

License
- (Add your preferred license here)

If you’d like, I can:
- commit this README.md to the repository on a branch,
- add a small `README` section in `frontend/README.md` showing the exact Expo commands for your machine IP,
- or add the web-callback snippet to the app root for you — tell me which you'd prefer.
