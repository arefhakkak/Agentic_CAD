# scrape_docs_ultramin.py
from __future__ import annotations
import re, argparse, logging, time, json, sqlite3
from urllib.parse import urljoin, urlparse, urlunparse, urldefrag
from typing import List, Tuple, Set
import requests
from bs4 import BeautifulSoup
from schema_ultra_combo import init_db

log = logging.getLogger("scrape_docs_ultramin")
UA = {"User-Agent": "Mozilla/5.0 (ultramin-scraper/1.0)"}

FACTORY_RX = re.compile(r'\b(HybridShapeFactory|ShapeFactory|SurfaceFactory|Sketch\w+|HybridShape\w+|Part)\b')
METHOD_RX  = re.compile(r'\bAddNew[A-Za-z0-9_]+\b')

def split_camel(s: str) -> List[str]:
    return [p.lower() for p in re.findall(r'[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|\d+', s or "") if p]

def normalize_key(factory: str, method: str) -> str:
    return f"{(factory or '').strip()}.{(method or '').strip()}".lower()

def action_from_method(method: str) -> str:
    # AddNewPlaneOffset -> create_plane_offset ; AddNewLinePtDir -> create_line_pt_dir
    m = method or ""
    m = re.sub(r'^(Add|AddNew)', '', m, flags=re.I)
    toks = split_camel(m)
    return "create_" + "_".join(toks)

def tokens_for(factory: str, method: str) -> List[str]:
    toks = set(split_camel(factory) + split_camel(method))
    toks.discard("add"); toks.discard("new")
    return sorted(toks)

def _norm_url(u: str) -> str:
    u, _ = urldefrag(u)
    p = urlparse(u)
    return urlunparse((p.scheme, p.netloc, p.path, "", "", ""))

def discover_links(master_url: str, session: requests.Session, limit: int = 600) -> List[str]:
    base = urlparse(master_url)
    seen: Set[Tuple[str,str,str]] = set()
    out: List[str] = []
    q = [_norm_url(master_url)]
    log.info("Start crawl: %s (limit=%d)", master_url, limit)
    while q and len(out) < limit:
        url = q.pop(0)
        p = urlparse(url)
        key = (p.scheme, p.netloc, p.path)
        if key in seen:
            continue
        seen.add(key)
        try:
            r = session.get(url, headers=UA, timeout=25)
            r.raise_for_status()
        except Exception as e:
            log.warning("Fetch failed: %s (%s)", url, e)
            continue
        out.append(url)
        soup = BeautifulSoup(r.text, "lxml")
        for a in soup.find_all("a", href=True):
            nxt = urljoin(url, a["href"])
            nxtn = _norm_url(nxt)
            pp = urlparse(nxtn)
            if pp.netloc != base.netloc: continue
            if "/online/interfaces/" not in pp.path: continue
            if (pp.scheme, pp.netloc, pp.path) not in seen:
                q.append(nxtn)
    log.info("Discovered %d unique pages", len(out))
    return out

def scrape_methods_from_page(url: str, html: str) -> List[Tuple[str,str,str]]:
    soup = BeautifulSoup(html, "lxml")
    factories = set(FACTORY_RX.findall(html))
    for hx in soup.find_all(["h1","h2","h3","title"]):
        m = FACTORY_RX.search(hx.get_text(" ", strip=True) or "")
        if m: factories.add(m.group(1))

    methods: set[str] = set()
    for a in soup.find_all("a"):
        for attr in ("name","id","href"):
            v = a.get(attr)
            if v and METHOD_RX.search(v):
                methods.add(METHOD_RX.search(v).group(0))
    text_candidates = [tag.get_text(" ", strip=True) for tag in soup.find_all(["code","pre","tt"])]
    text_candidates.append(soup.get_text(" ", strip=True))
    for txt in text_candidates:
        methods |= set(METHOD_RX.findall(txt))

    if not methods:
        return []
    if not factories:
        factories = {"HybridShapeFactory"}
    return [(f, m, url) for f in factories for m in methods]

def insert_docs(conn: sqlite3.Connection, items: List[Tuple[str,str,str]]):
    cur = conn.cursor()
    rows = []
    for factory, method, doc_url in items:
        key = normalize_key(factory, method)
        action = action_from_method(method)
        tokens = tokens_for(factory, method)
        rows.append((key, factory, method, action, doc_url, json.dumps(tokens, ensure_ascii=False)))
    cur.executemany("""
        INSERT OR IGNORE INTO doc_functions_ultramin
        (function_key, api_factory, api_method, action_label, doc_url, tokens_json)
        VALUES (?,?,?,?,?,?);
    """, rows)
    conn.commit()
    return len(rows)

def scrape(master_url: str, db_path: str, overwrite_docs: bool=False, link_limit: int=600) -> int:
    conn = init_db(db_path, overwrite=False)
    if overwrite_docs:
        conn.execute("DELETE FROM doc_functions_ultramin;"); conn.commit()
    session = requests.Session()
    links = discover_links(master_url, session, limit=link_limit)
    total_new = 0
    for i, url in enumerate(links, start=1):
        try:
            r = session.get(url, headers=UA, timeout=25); r.raise_for_status()
            triples = scrape_methods_from_page(url, r.text)
            if triples:
                total_new += insert_docs(conn, triples)
            if i % 25 == 0:
                log.debug("Progress: %d/%d pages", i, len(links))
        except Exception as e:
            log.warning("Parse failed: %s (%s)", url, e)
        time.sleep(0.02)
    conn.close()
    return total_new

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--master", required=True, help="e.g., http://catiadoc.free.fr/online/interfaces/CAAMasterIdx.htm")
    ap.add_argument("--overwrite-docs", action="store_true")
    ap.add_argument("--link-limit", type=int, default=600)
    ap.add_argument("--log-level", default="INFO")
    args = ap.parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO),
                        format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
    n = scrape(args.master, args.db, overwrite_docs=args.overwrite_docs, link_limit=args.link_limit)
    log.info("Scraped (attempted inserts) ~%d", n)

if __name__ == "__main__":
    main()
