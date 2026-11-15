# -*- coding: utf-8 -*-
"""Minimal fal.ai client: upload / run (queue + poll) / fetch.
Key: env FAL_KEY, else FAL_KEY=... in the file named by env ENV_FILE, else ./.env. Never printed."""
import json, mimetypes, os, re, time, urllib.error, urllib.request


def key():
    if os.environ.get("FAL_KEY"):
        return os.environ["FAL_KEY"].strip()
    for p in (os.environ.get("ENV_FILE"), os.path.join(os.getcwd(), ".env")):
        if p and os.path.exists(p):
            for line in open(p, encoding="utf-8"):
                m = re.match(r"\s*FAL_KEY\s*=\s*(.+)", line)
                if m:
                    return m.group(1).strip().strip('"').strip("'")
    raise SystemExit("FAL_KEY not found (set the env var, or ENV_FILE=path/to/.env)")


K = key()
H = {"Authorization": f"Key {K}", "Content-Type": "application/json"}


def _req(url, data=None, headers=None, method=None, raw=False, timeout=180):
    body = None if data is None else (data if raw else json.dumps(data).encode())
    r = urllib.request.Request(url, data=body, headers=headers or H, method=method)
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            c = resp.read()
            return json.loads(c) if c[:1] in (b"{", b"[") else c
    except urllib.error.HTTPError as e:
        raise SystemExit(f"HTTP {e.code} {url}\n{e.read().decode()[:800]}")


def upload(path):
    ct = mimetypes.guess_type(path)[0] or "application/octet-stream"
    init = _req("https://rest.alpha.fal.ai/storage/upload/initiate?storage_type=fal-cdn-v3",
                {"content_type": ct, "file_name": os.path.basename(path)})
    _req(init["upload_url"], data=open(path, "rb").read(), headers={"Content-Type": ct}, method="PUT", raw=True, timeout=600)
    return init["file_url"]


def run(endpoint, payload, poll=3, timeout=900):
    sub = _req(f"https://queue.fal.run/{endpoint}", payload)
    t0, auth = time.time(), {"Authorization": f"Key {K}"}
    while True:
        st = _req(sub["status_url"], headers=auth)
        s = st.get("status")
        if s == "COMPLETED":
            return _req(sub["response_url"], headers=auth)
        if s in ("FAILED", "CANCELLED"):
            raise SystemExit(f"{s}: {json.dumps(st)[:800]}")
        if time.time() - t0 > timeout:
            raise SystemExit("timeout waiting for " + str(sub.get("request_id")))
        time.sleep(poll)


def fetch(url, dst):
    with urllib.request.urlopen(url, timeout=600) as r, open(dst, "wb") as f:
        f.write(r.read())
    return dst
