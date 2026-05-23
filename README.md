# IEA — Image Encryption Application

A secure online image chat application built for a university cybersecurity
project. Users send each other images that are encrypted end-to-end using a
**from-scratch DES** cipher for the image and **from-scratch RSA** for key
exchange and digital signatures. The server never stores raw images or raw
symmetric keys.

> **Note:** DES is implemented per project requirements. AES is recommended for
> production use.

> **Performance:** DES uses fast integer-based bitwise operations with
> precomputed permutation and S-box/P lookup tables. Images are compressed to
> ≤ 80 KB in the browser before sending, so encryption and decryption each take
> well under a second. The DES and RSA work runs in a thread pool so the server
> never blocks while processing.

---

## How it works (security flow)

Each user has a **persistent RSA keypair**, generated once at registration (or
on first login) and stored in the `users` table. Persistent keys are what make
**offline messaging** possible — a sender can always encrypt to a recipient's
public key, and the recipient can decrypt later with their private key even
across logouts and re-logins. The live private key is also held in memory for
the session (`SESSION_KEYS`), and each login still records a session in
`active_sessions` for online-status tracking.

> **Security trade-off:** storing the private key server-side (in the DB) is a
> deliberate simplification so offline async delivery works for this class
> demo. In production the private key should never be stored in plaintext — it
> would be unlocked client-side or derived from the user's password, and the
> server would only ever hold public keys.

**Sending an image (A → B):**
1. Generate a random 8-byte DES key (`secrets.token_bytes(8)`).
2. Encrypt the image bytes with DES.
3. Encrypt the DES key with **receiver B's RSA public key**.
4. Sign the DES key with **sender A's RSA private key**.
5. Store `encrypted_image`, `encrypted_des_key`, `signature` (all bytes) in the
   `messages` table. **This always happens, online or offline** — sending is
   never gated on the recipient being connected.
6. Notify B over WebSocket *if* B is connected; otherwise the message simply
   waits in the database until B next opens the conversation.

**Receiving (B):**
1. Decrypt the DES key with B's private key.
2. Verify the signature with A's public key → confirms the key came from A,
   unmodified. The result is shown in the UI (✓ valid / ✗ invalid).
3. Decrypt the image with DES and display it.

Because keypairs are persistent, B does **not** need to be online when A sends —
B simply decrypts the waiting message the next time they open the conversation.

---

## Project structure

```
backend/
  main.py          FastAPI app: all routes, admin, WebSocket, seeding
  des.py           From-scratch DES (+ encrypt_bytes / decrypt_bytes)
  rsa.py           From-scratch RSA (Miller-Rabin, sign/verify, hex serde)
  models.py        SQLAlchemy models
  database.py      DB connection (PostgreSQL, SQLite fallback)
  auth.py          bcrypt + session tokens + in-memory private keys
  ws_manager.py    WebSocket connection tracking
  requirements.txt
frontend/
  index.html       Login + register
  chat.html        Chat interface
  admin.html       Sysadmin panel
  style.css        Dark theme
  app.js           apiFetch helper
render.yaml        Render deployment (web service + PostgreSQL)
README.md
```

No `cryptography`, no PyCryptodome, no `hazmat`. DES and RSA are written from
scratch using only Python's standard library.

---

## Run locally

### Option A — quick start (SQLite, no PostgreSQL needed)

If `DATABASE_URL` is not set, the app falls back to a local SQLite file
(`backend/iea_local.db`), which is perfect for development and grading.

```bash
cd "security project"
python3 -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt

# Run from the repo root:
uvicorn backend.main:app --reload --port 8000
```

Open <http://localhost:8000> in your browser.

### Option B — with local PostgreSQL

1. Install and start PostgreSQL, then create a database:
   ```bash
   createdb iea
   ```
2. Export the connection URL and run:
   ```bash
   export DATABASE_URL="postgresql://localhost:5432/iea"
   export SECRET_KEY="any-random-string"
   uvicorn backend.main:app --reload --port 8000
   ```

On first startup the app creates all tables and **seeds demo users**:

| Username | Password   | Role  |
|----------|------------|-------|
| admin    | admin123   | admin |
| alice    | alice123   | user  |
| bob      | bob123     | user  |

---

## Deploy to Render (step by step)

1. Push this repository to GitHub.
2. In the Render dashboard, click **New → Blueprint** and select your repo.
   Render reads `render.yaml` and provisions:
   - a **web service** (`iea-backend`) running the FastAPI app, and
   - a **PostgreSQL database** (`iea-db`).
3. `render.yaml` wires `DATABASE_URL` from the database automatically and
   generates a `SECRET_KEY`. No manual env vars are required.
4. Click **Apply**. Wait for the build (`pip install -r backend/requirements.txt`)
   and the start command (`uvicorn backend.main:app --host 0.0.0.0 --port $PORT`)
   to finish.
5. Open the service URL. The demo users are seeded on first boot.

> The free PostgreSQL plan and free web service are sufficient for a class demo.
> Note that the free web instance sleeps when idle and clears in-memory RSA
> private keys on restart (users simply log in again to get fresh keys).

---

## Test the full security flow

1. Open the app URL in **two different browsers** (or one normal + one private
   window) so each has its own session.
2. Log in as **alice** in one and **bob** in the other. (You can also test
   offline delivery: send to bob while bob is logged out, then log bob in — the
   waiting image appears in the conversation.)
3. As **alice**, click **bob** in the sidebar (green dot = online), choose an
   image, and click **Send**. Alice sees “Image sent”.
4. As **bob**, the conversation refreshes via WebSocket. Click **View Image** on
   the received message:
   - The image appears.
   - **✓ Delivered** is the user-facing confirmation that the underlying RSA
     signature over the DES key verified (the key came from alice, untampered).

> **Note on user-facing language:** the chat UI deliberately avoids technical
> terms (encrypt, signature, key, …). Behind the friendly labels — "Send",
> "View Image", "✓ Delivered" — the full DES + RSA encryption, signing and
> verification described above is running. The sysadmin panel keeps technical
> terms since it is an internal monitoring tool.
5. Log in as **admin** to open the sysadmin panel and inspect:
   - **Users** — accounts and online status.
   - **Messages** — metadata only (no decryption).
   - **Audit Log** — LOGIN / LOGOUT / MESSAGE_SENT / MESSAGE_RECEIVED /
     KEY_ROTATION events.
   - **Active Sessions** — who is currently logged in.

### Verifying tamper detection (optional)
Because the signature is over the DES key, any modification to `encrypted_des_key`
or `signature` in the database will cause **✗ Signature Invalid** to show on
decrypt — demonstrating RSA signature verification working as intended.
