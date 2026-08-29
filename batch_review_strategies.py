"""批量审查 600+ 聚宽策略：按年份目录遍历，每个策略按文件名命名并测试，逐策略生成 Markdown 报告。

用法:
    python -X utf8 batch_review_strategies.py                  # 全部年份
    python -X utf8 batch_review_strategies.py -Year 2020       # 只测某一年
    python -X utf8 batch_review_strategies.py -Server https://1.2.3.4 -NoVerify
    python -X utf8 batch_review_strategies.py -Limit 5         # 每年只测前 5 个（试跑）
"""
import argparse
import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.request

SRC = r"F:\BaiduNetdiskDownload\玄水润泽量化开发600+策略持续更新\2020年至2026年聚宽600+条策略"
OUT_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "strategy_reports")

BASE = "http://127.0.0.1:18080"
NO_VERIFY = False
MAX_DIFF = 800 * 1024  # 小于服务端 1 MiB 上限

# 文件名开头常见序号前缀，例如 "01 " "1." "10." "100 " "0." 等
_NUM_PREFIX = re.compile(r"^\s*\d{1,3}[\s.、\-_]*\s*")


def strategy_name_from_filename(fname: str) -> str:
    base = os.path.splitext(fname)[0]
    base = _NUM_PREFIX.sub("", base).strip()
    base = base.replace("-Clone", "").replace("_Clone", "").strip(" -_")
    return base or os.path.splitext(fname)[0]


def decode_text(raw: bytes) -> str:
    for enc in ("utf-8", "gb18030", "gbk"):
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw.decode("utf-8", errors="replace")


def to_diff(name: str, code: str) -> str:
    lines = code.splitlines()
    header = (
        "diff --git a/%s b/%s\n" % (name, name)
        + "new file mode 100644\n"
        + "--- /dev/null\n"
        + "+++ b/%s\n" % name
        + "@@ -0,0 +1,%d @@\n" % len(lines)
    )
    return header + "".join("+" + l + "\n" for l in lines)


def post(path, payload, token, timeout=180):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(BASE + path, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    ctx = ssl._create_unverified_context() if NO_VERIFY else None
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as exc:
        try:
            return exc.code, json.loads(exc.read())
        except Exception:
            return exc.code, {"error": "http %d" % exc.code}
    except Exception as exc:
        return 0, {"error": str(exc)}


def get(path, token, timeout=60):
    req = urllib.request.Request(BASE + path, method="GET")
    req.add_header("Authorization", "Bearer " + token)
    ctx = ssl._create_unverified_context() if NO_VERIFY else None
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return r.status, r.read()


def main():
    ap = argparse.ArgumentParser(description="Batch review JoinQuant strategies by year folder.")
    ap.add_argument("-Server", default="http://127.0.0.1:18080", help="API base url")
    ap.add_argument("-NoVerify", action="store_true", help="Skip TLS verification (VPS self-signed)")
    ap.add_argument("-Password", default="evoagent-local-admin", help="admin password")
    ap.add_argument("-Year", default=None, help="only test this year folder keyword, e.g. 2020")
    ap.add_argument("-Limit", type=int, default=None, help="only first N files per year (trial run)")
    ap.add_argument("-SkipExisting", action="store_true", help="skip strategies that already have a report")
    args = ap.parse_args()
    global BASE
    global NO_VERIFY
    BASE = args.Server.rstrip("/")
    NO_VERIFY = args.NoVerify

    dirs = sorted(os.listdir(SRC))
    year_dirs = [(d, os.path.join(SRC, d)) for d in dirs if os.path.isdir(os.path.join(SRC, d))]
    if args.Year:
        year_dirs = [(d, p) for d, p in year_dirs if args.Year in d]
    if not year_dirs:
        print("no year dirs matched:", args.Year)
        sys.exit(1)

    status, body = post("/v1/auth/login", {
        "username": "admin", "password": args.Password}, None)
    token = body.get("access_token", "")
    if not token:
        print("LOGIN FAILED", status, body)
        sys.exit(2)
    print("LOGIN ok, years:", len(year_dirs))

    os.makedirs(OUT_ROOT, exist_ok=True)
    summary_rows = []  # (year, strategy, findings, high, medium, low)
    all_rule_counts = {}

    for dirname, dirpath in year_dirs:
        year = dirname.split("年")[0].strip()  # "2020" / "聚宽2025" -> "聚宽2025"
        repo_year = year if year.startswith("聚宽") else "聚宽" + year
        files = sorted(
            f for f in os.listdir(dirpath)
            if f.endswith((".txt", ".py")) and os.path.getsize(os.path.join(dirpath, f)) > 0
        )
        if args.Limit:
            files = files[: args.Limit]
        year_out = os.path.join(OUT_ROOT, dirname)
        os.makedirs(year_out, exist_ok=True)

        for fname in files:
            strategy = strategy_name_from_filename(fname)
            repo = "%s/%s" % (repo_year, strategy)
            out_md = os.path.join(year_out, strategy + ".md")
            if args.SkipExisting and os.path.exists(out_md) and os.path.getsize(out_md) > 0:
                print("skip existing:", repo)
                continue

            raw = open(os.path.join(dirpath, fname), "rb").read()
            if len(raw) > MAX_DIFF:
                print("skip too large:", fname, len(raw))
                continue
            code = decode_text(raw)
            diff = to_diff(strategy + ".py", code)

            st, body = post("/v1/reviews", {
                "repository": repo, "diff": diff, "mode": "rules-only",
            }, token)
            if st != 201:
                print("[%s] ERROR %s: %s" % (repo, st, json.dumps(body, ensure_ascii=False)[:200]))
                continue
            report = body.get("report") or {}
            findings = report.get("findings") or []

            # 每个策略单独生成 Markdown 报告
            st2, md_bytes = get("/v1/tasks/%s/report" % body.get("task_id"), token)
            if st2 == 200:
                with open(out_md, "w", encoding="utf-8") as fh:
                    fh.write(md_bytes.decode("utf-8", errors="replace"))
            else:
                md_text = json.dumps(report, ensure_ascii=False, indent=2)
                with open(out_md, "w", encoding="utf-8") as fh:
                    fh.write("# %s\n\n%s" % (repo, md_text))

            high = sum(1 for f in findings if f.get("severity") == "high" or f.get("severity") == "critical")
            medium = sum(1 for f in findings if f.get("severity") == "medium")
            low = sum(1 for f in findings if f.get("severity") == "low")
            summary_rows.append((dirname, strategy, len(findings), high, medium, low))
            for f in findings:
                rid = f.get("rule_id", "?")
                all_rule_counts[rid] = all_rule_counts.get(rid, 0) + 1
            print("[%s/%s] %-40s findings=%-3d high=%d med=%d low=%d" % (
                dirname[:6], fname[:20], strategy[:38], len(findings), high, medium, low))
        print("--- done year:", dirname, "total files:", len(files))

    # 汇总表
    summary_path = os.path.join(OUT_ROOT, "_summary.md")
    with open(summary_path, "w", encoding="utf-8") as fh:
        fh.write("# 策略审查汇总\n\n")
        fh.write("| 年份 | 策略 | 问题数 | 高/中/低 |\n|---|---|---|---|\n")
        for year, strategy, total, high, medium, low in summary_rows:
            fh.write("| %s | %s | %d | %d/%d/%d |\n" % (year, strategy, total, high, medium, low))
        fh.write("\n## 规则命中分布\n\n")
        for rid, cnt in sorted(all_rule_counts.items(), key=lambda kv: -kv[1]):
            fh.write("- `%s`: %d\n" % (rid, cnt))
    print("\nSUMMARY:", summary_path)
    print("TOTAL strategies:", len(summary_rows), "TOTAL findings:", sum(r[2] for r in summary_rows))


if __name__ == "__main__":
    main()
