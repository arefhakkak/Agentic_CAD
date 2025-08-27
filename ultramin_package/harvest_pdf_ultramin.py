# harvest_pdf_ultramin.py
from __future__ import annotations
import re, json, argparse, sqlite3, logging
from typing import List, Dict, Any
from schema_ultra_combo import init_db

log = logging.getLogger("harvest_pdf_ultramin")

def extract_pdf_text_pages(pdf_path: str) -> List[str]:
    pages = []
    try:
        import pypdf
        reader = pypdf.PdfReader(pdf_path)
        for p in reader.pages:
            pages.append(p.extract_text() or "")
        if pages: return pages
    except Exception as e:
        log.debug("pypdf failed: %s", e)
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(pdf_path)
        for p in reader.pages:
            try: pages.append(p.extract_text() or "")
            except Exception: pages.append("")
        return pages
    except Exception as e:
        log.error("PyPDF2 failed: %s", e)
        return []

def parse_mm(text: str) -> List[float]:
    return [float(x) for x in re.findall(r'(-?\d+(?:\.\d+)?)\s*mm\b', text, flags=re.I)]

def parse_deg(text: str) -> List[float]:
    return [float(x) for x in re.findall(r'(-?\d+(?:\.\d+)?)\s*deg\b', text, flags=re.I)]

def compact_params(d: Dict[str, Any]) -> Dict[str, Any]:
    return {k:v for k,v in d.items() if v not in (None, "", [], {})}

RULES = [
    dict(
        key="create_plane_offset",
        rx=re.compile(r'\boffset\s+plane\b', re.I),
        parse=lambda s: dict(reference_plane=re.search(r'\b(xy|yz|zx)\s*plane|Plane\.\d+', s, flags=re.I).group(0)) if re.search(r'\b(xy|yz|zx)\s*plane|Plane\.\d+', s, flags=re.I) else {},
        more=lambda s: dict(offset_mm=parse_mm(s)[0] if parse_mm(s) else None),
        produces=lambda s: re.findall(r'Plane\.\d+', s),
    ),
    dict(
        key="create_point_on_plane",
        rx=re.compile(r'\bpoint\b.*\bon\b.*\bplane', re.I),
        parse=lambda s: dict(plane=re.search(r'(?:xy|yz|zx)\s*plane|Plane\.\d+', s, flags=re.I).group(0)) if re.search(r'(?:xy|yz|zx)\s*plane|Plane\.\d+', s, flags=re.I) else {},
        more=lambda s: dict(H=float(re.search(r'\bH\b.*?(\-?\d+(?:\.\d+)?)', s, flags=re.I).group(1))) if re.search(r'\bH\b.*?\-?\d+(?:\.\d+)?', s, flags=re.I) else {} | \
                       dict(V=float(re.search(r'\bV\b.*?(\-?\d+(?:\.\d+)?)', s, flags=re.I).group(1))) if re.search(r'\bV\b.*?\-?\d+(?:\.\d+)?', s, flags=re.I) else {},
        produces=lambda s: re.findall(r'Point\.\d+', s),
    ),
    dict(
        key="create_point_coord_with_reference",
        rx=re.compile(r'\bpoint\b.*\bcoordinate', re.I),
        parse=lambda s: dict(x=float(re.search(r'\bx\s*value\s*of\s*(\-?\d+(?:\.\d+)?)', s, flags=re.I).group(1))) if re.search(r'\bx\s*value\s*of\s*(\-?\d+(?:\.\d+)?)', s, flags=re.I) else {},
        more=lambda s: dict(reference=re.search(r'Point\.\d+', s).group(0)) if re.search(r'Point\.\d+', s) else {},
        produces=lambda s: re.findall(r'Point\.\d+', s),
    ),
    dict(
        key="create_spline_through_points",
        rx=re.compile(r'\bcreate\b.*\bspline\b.*\bthrough\b', re.I),
        parse=lambda s: dict(points=re.findall(r'Point\.\d+', s, flags=re.I)),
        more=lambda s: {},
        produces=lambda s: re.findall(r'Spline\.\d+', s),
    ),
    dict(
        key="set_tangency_axis",
        rx=re.compile(r'\baxis tangency\b', re.I),
        parse=lambda s: dict(axis=re.search(r'\b([XYZ])\s*axis', s, flags=re.I).group(1)+" axis" if re.search(r'\b([XYZ])\s*axis', s, flags=re.I) else None,
                             point=re.search(r'Point\.\d+', s).group(0) if re.search(r'Point\.\d+', s) else None),
        more=lambda s: {},
        produces=lambda s: [],
    ),
    dict(
        key="set_parameter",
        rx=re.compile(r'\b(change|modify)\b.*\bparameter\b', re.I),
        parse=lambda s: dict(target=re.search(r'(Spline\.\d+|Plane\.\d+|Point\.\d+|Line\.\d+|Tension\.\d+)', s).group(0)) if re.search(r'(Spline\.\d+|Plane\.\d+|Point\.\d+|Line\.\d+|Tension\.\d+)', s) else {},
        more=lambda s: dict(name="Tension", value=float(re.search(r'(\-?\d+(?:\.\d+)?)', s).group(1))) if "tension" in s.lower() and re.search(r'(\-?\d+(?:\.\d+)?)', s) else \
                       (dict(name="Offset", value=float(re.search(r'(\-?\d+(?:\.\d+)?)\s*mm', s, flags=re.I).group(1))) if "offset" in s.lower() and re.search(r'(\-?\d+(?:\.\d+)?)\s*mm', s, flags=re.I) else
                        (dict(name="H", value=float(re.search(r'\bH\b.*?(\-?\d+(?:\.\d+)?)', s, flags=re.I).group(1))) if re.search(r'\bH\b.*?\-?\d+(?:\.\d+)?', s, flags=re.I) else {})),
        produces=lambda s: [],
    ),
    dict(
        key="create_line_point_direction",
        rx=re.compile(r'\bline\b.*\bPoint-?Direction\b', re.I),
        parse=lambda s: dict(point=re.search(r'Point\.\d+', s).group(0) if re.search(r'Point\.\d+', s) else None,
                             direction=re.search(r'(?:xy|yz|zx)\s*plane|Plane\.\d+|Line\.\d+', s, flags=re.I).group(0) if re.search(r'(?:xy|yz|zx)\s*plane|Plane\.\d+|Line\.\d+', s, flags=re.I) else None),
        more=lambda s: {},
        produces=lambda s: re.findall(r'Line\.\d+', s),
    ),
    dict(
        key="create_line_angle_normal",
        rx=re.compile(r'\bline\b.*\bangle/normal\b|\bangle\b.*\bnormal\b', re.I),
        parse=lambda s: dict(point=re.search(r'Point\.\d+', s).group(0) if re.search(r'Point\.\d+', s) else None,
                             support=re.search(r'(?:xy|yz|zx)\s*plane|Plane\.\d+', s, flags=re.I).group(0) if re.search(r'(?:xy|yz|zx)\s*plane|Plane\.\d+', s, flags=re.I) else None,
                             curve=re.search(r'Line\.\d+|Spline\.\d+', s).group(0) if re.search(r'Line\.\d+|Spline\.\d+', s) else None,
                             angle_deg=parse_deg(s)[0] if parse_deg(s) else None),
        more=lambda s: {},
        produces=lambda s: re.findall(r'Line\.\d+', s),
    ),
    dict(
        key="extrude_surface",
        rx=re.compile(r'\bextrude\s+surface\b', re.I),
        parse=lambda s: dict(profile=re.search(r'Spline\.\d+', s).group(0) if re.search(r'Spline\.\d+', s) else None,
                             direction=re.search(r'Line\.\d+|(?:xy|yz|zx)\s*plane', s, flags=re.I).group(0) if re.search(r'Line\.\d+|(?:xy|yz|zx)\s*plane', s, flags=re.I) else None),
        more=lambda s: {},
        produces=lambda s: re.findall(r'Extrude\.\d+', s),
    ),
    dict(
        key="multi_section_surface",
        rx=re.compile(r'\bmulti-?section[s]?\s+surface\b', re.I),
        parse=lambda s: dict(sections=re.findall(r'Spline\.\d+', s), guides=re.findall(r'Spline\.\d+', s)),
        more=lambda s: dict(tangent_surfaces=re.findall(r'Extrude\.\d+', s)),
        produces=lambda s: re.findall(r'Multi-?sections? Surface\.\d+', s, flags=re.I),
    ),
    dict(
        key="symmetry",
        rx=re.compile(r'\bsymmetry\b', re.I),
        parse=lambda s: dict(elements=re.findall(r'(?:Multi-?sections? Surface\.\d+|Extrude\.\d+|Join\.\d+|ThickSurface\.\d+)', s, flags=re.I)),
        more=lambda s: dict(reference=re.search(r'(?:xy|yz|zx)\s*plane|Plane\.\d+', s, flags=re.I).group(0) if re.search(r'(?:xy|yz|zx)\s*plane|Plane\.\d+', s, flags=re.I) else None),
        produces=lambda s: [],
    ),
    dict(
        key="delete",
        rx=re.compile(r'\bdelete\b', re.I),
        parse=lambda s: dict(target=re.search(r'[A-Za-z]+(?:\s*Output)?\.\d+', s).group(0) if re.search(r'[A-Za-z]+(?:\s*Output)?\.\d+', s) else None),
        more=lambda s: {},
        produces=lambda s: [],
    ),
    dict(
        key="join",
        rx=re.compile(r'\bjoin\b', re.I),
        parse=lambda s: dict(elements=re.findall(r'(?:Multi-?sections? Surface\.\d+|Extrude\.\d+)', s, flags=re.I)),
        more=lambda s: {},
        produces=lambda s: re.findall(r'Join\.\d+', s),
    ),
    dict(
        key="thick_surface",
        rx=re.compile(r'\bthick\s+surface\b', re.I),
        parse=lambda s: dict(object=re.search(r'Join\.\d+|Surface\.\d+', s).group(0) if re.search(r'Join\.\d+|Surface\.\d+', s) else None,
                             thickness_mm=parse_mm(s)[0] if parse_mm(s) else None),
        more=lambda s: {},
        produces=lambda s: re.findall(r'ThickSurface\.\d+', s),
    ),
]

def compact_params(d: Dict[str, Any]) -> Dict[str, Any]:
    return {k:v for k,v in d.items() if v not in (None, "", [], {})}

def classify_line(line: str):
    for rule in RULES:
        if rule["rx"].search(line):
            params = {}
            try: params.update(rule["parse"](line) or {})
            except Exception: pass
            try: params.update(rule["more"](line) or {})
            except Exception: pass
            produces = []
            try: produces = rule["produces"](line) or []
            except Exception: pass
            refs = set(re.findall(r'(?:Point|Line|Plane|Spline|Extrude|Join|ThickSurface|Multi-?sections? Surface)\.\d+|(?:xy|yz|zx)\s*plane|[XYZ]\s*axis', line, flags=re.I))
            for p in produces: 
                if p in refs: refs.remove(p)
            return dict(action=rule["key"], params=compact_params(params), produces=produces, references=sorted(refs, key=str.lower))
    return None

def harvest(pdf_path: str, db_path: str, overwrite: bool=False) -> str:
    conn = init_db(db_path, overwrite=overwrite)
    cur = conn.cursor()
    pages = extract_pdf_text_pages(pdf_path)
    text = "\n".join(pages)
    blocks = re.split(r'\bStep\s*(\d+)\b', text, flags=re.I)
    inserts = []
    step_id = 0

    if len(blocks) > 1:
        for i in range(1, len(blocks), 2):
            content = blocks[i+1]
            lines = [ln.strip() for ln in re.split(r'[\n\r]+', content) if len(ln.strip()) > 4]
            if not lines: continue
            chosen = None
            for ln in lines:
                parsed = classify_line(ln)
                if parsed:
                    chosen = (ln, parsed); break
            if not chosen: 
                parsed = dict(action="note", params={}, produces=[], references=[]); chosen = (lines[0], parsed)
            step_id += 1
            ln, parsed = chosen
            inserts.append((
                step_id, parsed["action"], ln,
                json.dumps(parsed["params"], ensure_ascii=False),
                json.dumps(parsed["produces"], ensure_ascii=False),
                json.dumps(parsed["references"], ensure_ascii=False),
                None, None
            ))
    else:
        for ln in [ln.strip() for ln in re.split(r'[\n\r]+', text) if len(ln.strip()) > 4]:
            parsed = classify_line(ln)
            if not parsed: continue
            step_id += 1
            inserts.append((
                step_id, parsed["action"], ln,
                json.dumps(parsed["params"], ensure_ascii=False),
                json.dumps(parsed["produces"], ensure_ascii=False),
                json.dumps(parsed["references"], ensure_ascii=False),
                None, None
            ))

    if inserts:
        cur.executemany("""
            INSERT INTO harvested_steps_ultramin
            (step_id, action_label, description, params_json, produces_json, references_json, code_lang, generated_code)
            VALUES (?,?,?,?,?,?,?,?);
        """, inserts)
        conn.commit()
    conn.close()
    return db_path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--db", required=True)
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--log-level", default="INFO")
    args = ap.parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO),
                        format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
    out = harvest(args.pdf, args.db, overwrite=args.overwrite)
    log.info("Harvested -> %s", out)

if __name__ == "__main__":
    main()
