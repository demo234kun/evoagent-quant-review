"""Run the quant code review on REAL 2026 JoinQuant strategies via the live API."""
import argparse
import json
import os
import ssl
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:18080"
NO_VERIFY = False
SRC_DIR = r"F:\BaiduNetdiskDownload\玄水润泽量化开发600+策略持续更新\2020年至2026年聚宽600+条策略"
# resolve the 2026 subfolder by name match (avoid retyping CJK literal)
_base = SRC_DIR
_sub = None
for d in os.listdir(_base):
    if "2026" in d:
        _sub = os.path.join(_base, d)
        break

SELECT = None  # None => run every non-empty file in the 2026 folder


def to_diff(name, code):
    lines = code.splitlines()
    header = (
        "diff --git a/%s b/%s\n" % (name, name)
        + "new file mode 100644\n"
        + "--- /dev/null\n"
        + "+++ b/%s\n" % name
        + "@@ -0,0 +1,%d @@\n" % len(lines)
    )
    return header + "".join("+" + l + "\n" for l in lines)


def post(path, payload, token, timeout=120):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(BASE + path, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    ctx = ssl._create_unverified_context() if NO_VERIFY else None
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def main():
    ap = argparse.ArgumentParser(
        description="Run the quant code review on real 2026 JoinQuant strategies via the live API.")
    ap.add_argument("-Server", default="http://127.0.0.1:18080",
                    help="API base url, e.g. https://1.2.3.4 or http://127.0.0.1:18080")
    ap.add_argument("-NoVerify", action="store_true",
                    help="Skip TLS verification (use for the VPS self-signed Caddy cert)")
    ap.add_argument("-Password", default="evoagent-local-admin",
                    help="admin password on the target server (match its EVOAGENT_ADMIN_PASSWORD)")
    args = ap.parse_args()
    global BASE, NO_VERIFY
    BASE = args.Server.rstrip("/")
    NO_VERIFY = args.NoVerify
    if BASE.startswith("https") and not NO_VERIFY:
        print("WARNING: https server without -NoVerify; self-signed certs will fail. "
              "Add -NoVerify for the VPS Caddy cert.")

    files = [f for f in os.listdir(_sub) if f.endswith(".txt")]
    files.sort()
    print("2026 strategy files found:", len(files), "in", _sub)

    status, body = post("/v1/auth/login", {
        "username": "admin", "password": args.Password}, None)
    token = body.get("access_token", "")
    print("LOGIN", status, "token_len=", len(token))

    chosen = files if SELECT is None else [files[i] for i in SELECT if i < len(files)]
    for fname in chosen:
        fpath = os.path.join(_sub, fname)
        if os.path.getsize(fpath) == 0:
            print("\n[%s] EMPTY -> skipped" % fname)
            continue
        with open(fpath, "r", encoding="utf-8", errors="replace") as fh:
            code = fh.read()
        diff = to_diff(fname.replace(".txt", ".py"), code)
        status, body = post("/v1/reviews", {
            "repository": "quant/2026",
            "diff": diff,
            "mode": "rules-only",
        }, token)
        print("\n[%s]  status=%s  bytes=%d" % (fname, status, len(code)))
        if status != 201:
            print("   ERROR:", json.dumps(body, ensure_ascii=False)[:300])
            continue
        findings = body.get("report", {}).get("findings", [])
        print("   findings=%d" % len(findings))
        sev_count = {}
        for f in findings:
            sev_count[f.get("severity", "?")] = sev_count.get(f.get("severity", "?"), 0) + 1
            print("     [%s] %s  (%s:%s)  %s" % (
                f.get("severity", "?"), f.get("rule_id", "?"),
                f.get("path", "?"), f.get("line", "?"),
                (f.get("title", "") or "")[:40]))
        print("   by-severity:", sev_count)


if __name__ == "__main__":
    main()
