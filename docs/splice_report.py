"""Splice subbab 4.4 (_sec44.pdf) into the clean report PDF after the
Agglomerative section, then renumber footers and patch the TOC / Daftar
Gambar / Daftar Tabel. Original PDF is left untouched; writes a new file."""
import re
import fitz

BASE = "/home/ravi/Downloads/Kelompok_10_Agglomerative Clustering.pdf"
SEC = "/home/ravi/Projects/DataMining/docs/_sec44.pdf"
OUT = "/home/ravi/Downloads/Kelompok_10_Agglomerative Clustering_TitikTerjauh.pdf"
TNR = "/home/ravi/.local/share/fonts/tnr/TimesNewRoman.ttf"
TNRB = "/home/ravi/.local/share/fonts/tnr/TimesNewRoman-Bold.ttf"

font = fitz.Font(fontfile=TNR)
fontB = fitz.Font(fontfile=TNRB)
RIGHT = 510.0            # right edge for TOC page numbers
LEADER_GAP = 3.0

def rows_of(page):
    """Return list of (text, first_span, last_span, lines...) grouped per visual line."""
    out = []
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            sp = [s for s in l["spans"] if s["text"].strip()]
            if sp:
                out.append(sp)
    return out

def find_row(page, prefix):
    for sp in rows_of(page):
        txt = "".join(s["text"] for s in sp)
        if txt.strip().startswith(prefix):
            return sp, txt
    return None, None

def trailing_int(txt):
    m = re.findall(r"(\d+)\s*$", txt.strip())
    return int(m[0]) if m else None

def draw_toc_row(page, fnt, is_bold, num, num_x, title, title_x, page_str, baseline_y):
    """Draw a TOC row: number, title, dotted leader, right-aligned page number."""
    fobj = fontB if is_bold else font
    fname = "tnrb" if is_bold else "tnr"
    ffile = TNRB if is_bold else TNR
    if num:
        page.insert_text((num_x, baseline_y), num, fontfile=ffile, fontname=fname, fontsize=12)
    page.insert_text((title_x, baseline_y), title, fontfile=ffile, fontname=fname, fontsize=12)
    title_end = title_x + fobj.text_length(title, 12)
    num_w = fobj.text_length(page_str, 12)
    page.insert_text((RIGHT - num_w, baseline_y), page_str, fontfile=ffile, fontname=fname, fontsize=12)
    # dotted leader (same weight as the row)
    dot_w = fobj.text_length(".", 12)
    start = title_end + LEADER_GAP
    end = RIGHT - num_w - LEADER_GAP
    ndots = max(0, int((end - start) / dot_w))
    if ndots:
        page.insert_text((end - ndots * dot_w, baseline_y), "." * ndots,
                         fontfile=ffile, fontname=fname, fontsize=12)

def set_footer(page, num_str, old_bbox=None):
    if old_bbox is not None:  # redact old number out of the text layer
        r = fitz.Rect(old_bbox)
        r.x0 -= 3; r.x1 += 3; r.y0 -= 2; r.y1 += 2
        page.add_redact_annot(r, fill=(1, 1, 1))
        page.apply_redactions()
    w = font.text_length(num_str, 12)
    page.insert_text(((page.rect.width - w) / 2, 792.7), num_str,
                     fontfile=TNR, fontname="tnr", fontsize=12)

# ============================================================ build
doc = fitz.open(BASE)

# --- capture TOC anchors BEFORE insertion (indices for TOC pages unchanged) ---
toc = doc[2]  # Daftar Isi page 2
sp_434, _ = find_row(toc, "4.3.4")
sp_babV, txt_babV = find_row(toc, "BAB V")
sp_51, _ = find_row(toc, "5.1")
sp_52, _ = find_row(toc, "5.2")

def page_of(page, keyword):
    for ln in page.get_text().split("\n"):
        if keyword in ln:
            return trailing_int(ln)
    return None

base_babV = page_of(toc, "BAB V PENUTUP")
base_51 = page_of(toc, "Kesimpulan")
base_52 = page_of(toc, "Saran")
y_434 = sp_434[0]["origin"][1]
y_babV = sp_babV[0]["origin"][1]
pitch_isi = y_babV - y_434
print("TOC pages:", base_babV, base_51, base_52, "| pitch", round(pitch_isi, 1))

dg = doc[3]  # Daftar Gambar
sp_g9, _ = find_row(dg, "Gambar 4.9")
y_g9 = sp_g9[0]["origin"][1]
sp_g8, _ = find_row(dg, "Gambar 4.8")   # for pitch (single-line neighbor)
sp_g7, _ = find_row(dg, "Gambar 4.7")
pitch_dg = sp_g8[0]["origin"][1] - sp_g7[0]["origin"][1]

dt = doc[5]  # Daftar Tabel
sp_t12, _ = find_row(dt, "Tabel 4.12")
y_t12 = sp_t12[0]["origin"][1]
sp_t11, _ = find_row(dt, "Tabel 4.11")
sp_t10, _ = find_row(dt, "Tabel 4.10")
pitch_dt = sp_t11[0]["origin"][1] - sp_t10[0]["origin"][1]

# --- 1) insert the 2 section-4.4 pages after 0-idx 32 (before BAB V at 33) ---
sec = fitz.open(SEC)
doc.insert_pdf(sec, from_page=0, to_page=1, start_at=33)
sec.close()
# now: 33,34 = new 4.4 pages; 35,36,37 = old BAB V.. (printed 28,29,30 -> 30,31,32)

# --- 2) footer renumbering ---
def footer_span(page):
    h = page.rect.height
    for sp in rows_of(page):
        for s in sp:
            if s["origin"][1] > h - 70 and s["text"].strip().isdigit():
                return s
    return None

set_footer(doc[33], "28")   # inserted 4.4 p1
set_footer(doc[34], "29")   # inserted 4.4 p2
for idx, newnum in [(35, "30"), (36, "31"), (37, "32")]:
    fs = footer_span(doc[idx])
    set_footer(doc[idx], newnum, old_bbox=fs["bbox"] if fs else None)

# --- 3) Daftar Isi: insert 4.4 row + shift BAB V/5.1/5.2 down & +2 pages ---
toc = doc[2]
# redact the old BAB V / 5.1 / 5.2 block out of the text layer, then redraw
toc.add_redact_annot(fitz.Rect(113.0, y_babV - 11, RIGHT + 4, sp_52[0]["origin"][1] + 4),
                     fill=(1, 1, 1))
toc.apply_redactions()
draw_toc_row(toc, font, False, "4.4", 125.4,
             "Analisis Pengaruh Centroid Awal terhadap Outlier", 157.4, "28", y_babV)
draw_toc_row(toc, fontB, False, None, None, "BAB V PENUTUP", 113.4, str(base_babV + 2), y_babV + pitch_isi)
draw_toc_row(toc, font, False, "5.1", 125.4, "Kesimpulan", 157.4, str(base_51 + 2), y_babV + 2 * pitch_isi)
draw_toc_row(toc, font, False, "5.2", 125.4, "Saran", 157.4, str(base_52 + 2), y_babV + 3 * pitch_isi)

# --- 4) Daftar Gambar: append Gambar 4.10 (page 29) — entries are BOLD here ---
draw_toc_row(doc[3], fontB, True, None, None,
             "Gambar 4.10 Perbandingan Centroid Awal di Dalam vs di Luar Layer", 113.4,
             "29", y_g9 + pitch_dg)

# --- 5) Daftar Tabel: append Tabel 4.13 (page 28) — entries are BOLD here ---
draw_toc_row(doc[5], fontB, True, None, None,
             "Tabel 4.13 Perbandingan Centroid Awal di Dalam vs di Luar Layer", 113.4,
             "28", y_t12 + pitch_dt)

# --- 5b) ratakan judul heading (x.y / x.y.z) ke indent body (sejajar) ---
# Base menaruh judul heading di x=149.4, padahal indent paragraf body di x=141.9,
# sehingga judul sub-bab tidak sejajar dengan awal paragraf. Geser judul ke 141.9.
TITLE_X = 141.9
HEAD_RE = re.compile(r"^\d\.\d(?:\.\d)?(?!\d)")

def fix_heading_indent(doc, target_x=TITLE_X):
    fixed = 0
    for i in range(6, doc.page_count):          # lewati cover + daftar isi/gambar/tabel
        pg = doc[i]
        d = pg.get_text("dict")
        words = pg.get_text("words")
        jobs = []
        for b in d["blocks"]:
            for l in b.get("lines", []):
                sp = [s for s in l["spans"] if s["text"].strip()]
                if not sp or "Bold" not in sp[0]["font"]:
                    continue
                linetext = "".join(s["text"] for s in sp).strip()
                if not HEAD_RE.match(linetext):
                    continue
                ly = sp[0]["bbox"][1]
                lw = sorted([w for w in words if abs(w[1] - ly) < 3], key=lambda w: w[0])
                title_words = [w for w in lw if not re.fullmatch(r"\d\.\d(?:\.\d)?", w[4])]
                if not title_words:
                    continue
                cur_x = title_words[0][0]
                if abs(cur_x - target_x) < 0.6:
                    continue                     # sudah sejajar
                title_text = " ".join(w[4] for w in title_words)
                line_x1 = max(w[2] for w in lw)
                baseline = sp[0]["origin"][1]
                pg.add_redact_annot(fitz.Rect(cur_x - 2, ly - 2, line_x1 + 2, sp[0]["bbox"][3] + 2),
                                    fill=(1, 1, 1))
                jobs.append((title_text, baseline))
        if jobs:
            pg.apply_redactions()
            for title_text, baseline in jobs:
                pg.insert_text((target_x, baseline), title_text,
                               fontfile=TNRB, fontname="tnrb", fontsize=12)
            fixed += len(jobs)
    return fixed

print("headings re-aligned:", fix_heading_indent(doc))

# --- 6) bersihkan token 'ZT051' yang bocor & TERLIHAT di Daftar Isi (bawaan base) ---
# Redak token + leader lama pada baris itu, lalu gambar ulang leader titik yang menyatu.
zt = doc[2].search_for("ZT051")
if zt:
    r = zt[0]
    num_x0 = RIGHT - font.text_length("18", 12)   # '18' rata kanan ke 510
    doc[2].add_redact_annot(fitz.Rect(r.x0 - 1, r.y0 - 2, num_x0 - 2, r.y1 + 2), fill=(1, 1, 1))
    doc[2].apply_redactions()
    dot_w = font.text_length(".", 12)
    end = num_x0 - LEADER_GAP
    n = max(0, int((end - r.x0) / dot_w))
    if n:
        doc[2].insert_text((end - n * dot_w, r.y1 - 2.5), "." * n,
                           fontfile=TNR, fontname="tnr", fontsize=12)
print("cleaned visible ZT051 tokens:", len(zt))

doc.save(OUT, garbage=4, deflate=True)
print("saved:", OUT, "| total pages:", doc.page_count)
