# run_all_ultramin.py
from __future__ import annotations
import argparse, logging
from schema_ultra_combo import init_db
from scrape_docs_ultramin import scrape as scrape_docs
from harvest_pdf_ultramin import harvest as harvest_pdf

def main():
    ap = argparse.ArgumentParser(description="Ultra-minimal DB: scrape CAADoc and/or harvest PDF into separate tables")
    ap.add_argument("--db", required=True)
    ap.add_argument("--master", help="CAADoc Master Index URL (e.g., http://catiadoc.free.fr/online/interfaces/CAAMasterIdx.htm)")
    ap.add_argument("--pdf", help="Path to instructions PDF")
    ap.add_argument("--overwrite-db", action="store_true")
    ap.add_argument("--overwrite-docs", action="store_true", help="Clear doc_functions_ultramin before scraping")
    ap.add_argument("--log-level", default="INFO")
    ap.add_argument("--link-limit", type=int, default=600)
    args = ap.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO),
                        format="%(asctime)s %(levelname)s [%(name)s] %(message)s")

    init_db(args.db, overwrite=args.overwrite_db)

    if args.master:
        n = scrape_docs(args.master, args.db, overwrite_docs=args.overwrite_docs, link_limit=args.link_limit)
        logging.getLogger("run_all_ultramin").info("Scrape inserted (attempted) ~%d doc methods", n)
    if args.pdf:
        out = harvest_pdf(args.pdf, args.db, overwrite=False)
        logging.getLogger("run_all_ultramin").info("PDF harvested -> %s", out)

    if not args.master and not args.pdf:
        print("Nothing to do. Provide --master and/or --pdf.")

if __name__ == "__main__":
    main()
