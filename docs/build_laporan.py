"""Laporan Tugas Akhir Data Mining - Metode Agglomerative Clustering (Kelompok 10).
Format mengikuti template Kelompok 3 (ID3). Daftar Isi/Tabel/Gambar/Kode dibuat
manual lewat dua tahap (passA -> deteksi nomor halaman -> passB).

Pakai:  python build_laporan.py passA   (lalu konversi PDF)
        python build_laporan.py passB   (baca PDF passA, tulis docx final)
"""
import os
import sys
import subprocess
import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import (WD_ALIGN_PARAGRAPH, WD_LINE_SPACING,
                            WD_TAB_ALIGNMENT, WD_TAB_LEADER)
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, 'figures')
TMP_DOCX = os.path.join(HERE, '_passA.docx')
TMP_PDF = os.path.join(HERE, '_passA.pdf')
OUT_DOCX = os.path.join(HERE, 'Laporan_Kelompok10_Agglomerative.docx')

FONT = 'Times New Roman'
MONO = 'Courier New'

# ============================================================ DATA
data = pd.DataFrame({
    'Mhs':   ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'],
    'Tugas': [1, 2, 2, 5, 6, 5, 9, 9, 8, 10],
    'Ujian': [2, 2, 3, 5, 5, 6, 9, 8, 9, 10],
})
X = data[['Tugas', 'Ujian']].values
names = data['Mhs'].values
dist_mat = squareform(pdist(X))


def trace_single(X, names):
    clusters = [[n] for n in names]
    M = squareform(pdist(X)).astype(float)
    np.fill_diagonal(M, np.inf)
    rows = []
    while len(clusters) > 1:
        i, j = np.unravel_index(np.argmin(M), M.shape)
        if i > j:
            i, j = j, i
        a = '{' + ','.join(clusters[i]) + '}'
        b = '{' + ','.join(clusters[j]) + '}'
        d = M[i, j]
        new = np.minimum(M[i, :], M[j, :]); new[i] = np.inf
        M[i, :] = new; M[:, i] = new
        M = np.delete(M, j, 0); M = np.delete(M, j, 1)
        clusters[i] = clusters[i] + clusters[j]; del clusters[j]
        rows.append((len(rows) + 1, a, b, round(float(d), 3), len(clusters)))
    return rows


merge_rows = trace_single(X, names)

# ============================================================ STYLE HELPERS

def set_base_style(doc):
    st = doc.styles['Normal']
    st.font.name = FONT; st.font.size = Pt(12); st.font.color.rgb = RGBColor(0, 0, 0)
    rf = st.element.get_or_add_rPr().get_or_add_rFonts()
    for a in ('w:ascii', 'w:hAnsi', 'w:cs', 'w:eastAsia'):
        rf.set(qn(a), FONT)
    pf = st.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE; pf.space_after = Pt(0)


def style_heading(doc, name, size):
    st = doc.styles[name]
    st.font.name = FONT; st.font.size = Pt(size); st.font.bold = True
    st.font.color.rgb = RGBColor(0, 0, 0)
    rf = st.element.get_or_add_rPr().get_or_add_rFonts()
    for a in ('w:ascii', 'w:hAnsi', 'w:cs', 'w:eastAsia'):
        rf.set(qn(a), FONT)
    st.paragraph_format.space_before = Pt(12); st.paragraph_format.space_after = Pt(6)
    st.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    st.paragraph_format.keep_with_next = True


def add_token(p, token):
    r = p.add_run(' ' + token)
    r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF); r.font.size = Pt(1); r.font.name = FONT


def body(doc, text, indent=True, justify=True):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    if justify:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if indent:
        p.paragraph_format.first_line_indent = Cm(1.0)
    p.add_run(text)
    return p


def numbered(doc, n, text):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.left_indent = Cm(1.0)
    p.paragraph_format.first_line_indent = Cm(-1.0)
    p.add_run(f'{n}.\t{text}')
    return p


def plain_center(doc, text, bold=False, size=12, sb=0, sa=0):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(sb); p.paragraph_format.space_after = Pt(sa)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    r = p.add_run(text); r.bold = bold; r.font.size = Pt(size)
    return p


# heading helpers that also register TOC entries + invisible token
def bab(doc, reg, roman, title):
    tok = f'ZT{len(reg):03d}'
    p1 = doc.add_heading(level=1); p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p1.add_run(f'BAB {roman}')
    p2 = doc.add_heading(level=1); p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p2.add_run(title); add_token(p2, tok)
    reg.append(dict(cat='toc', level=0, label=f'BAB {roman} {title}', token=tok))


def h2num(doc, reg, num, title):
    tok = f'ZT{len(reg):03d}'
    p = doc.add_heading(level=2); p.add_run(f'{num}\t{title}'); add_token(p, tok)
    reg.append(dict(cat='toc', level=1, label=f'{num} {title}', token=tok))


def h3num(doc, reg, num, title):
    tok = f'ZT{len(reg):03d}'
    p = doc.add_heading(level=3); p.add_run(f'{num}\t{title}'); add_token(p, tok)
    reg.append(dict(cat='toc', level=2, label=f'{num} {title}', token=tok))


def special_heading(doc, reg, title):
    tok = f'ZT{len(reg):03d}'
    p = plain_center(doc, title, bold=True, sa=12); add_token(p, tok)
    reg.append(dict(cat='toc', level=0, label=title, token=tok))


def caption(doc, reg, cat, label):
    tok = f'Z{cat[0].upper()}{len(reg):03d}'
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(label); r.bold = True; r.font.size = Pt(11); r.font.name = FONT
    add_token(p, tok)
    reg.append(dict(cat=cat, level=0, label=label, token=tok))


def add_image(doc, fname, width_cm):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.add_run().add_picture(os.path.join(FIG, fname), width=Cm(width_cm))


# tables
def set_cell_bg(cell, color):
    shd = OxmlElement('w:shd'); shd.set(qn('w:val'), 'clear'); shd.set(qn('w:fill'), color)
    cell._tc.get_or_add_tcPr().append(shd)


def set_table_borders(tbl):
    borders = OxmlElement('w:tblBorders')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        e = OxmlElement(f'w:{edge}')
        e.set(qn('w:val'), 'single'); e.set(qn('w:sz'), '4')
        e.set(qn('w:space'), '0'); e.set(qn('w:color'), '000000')
        borders.append(e)
    tbl._tbl.tblPr.append(borders)


def cell(c, text, bold=False, size=10, left=False):
    c.text = ''
    p = c.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT if left else WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(str(text)); r.bold = bold; r.font.name = FONT; r.font.size = Pt(size)


def code_box(doc, code_text):
    tbl = doc.add_table(rows=1, cols=1); tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl)
    c = tbl.cell(0, 0); c.text = ''
    first = True
    for line in code_text.split('\n'):
        p = c.paragraphs[0] if first else c.add_paragraph(); first = False
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(line if line else ' '); r.font.name = MONO; r.font.size = Pt(8.5)


# page numbering
def page_footer(section, fmt, start):
    sectPr = section._sectPr
    pg = sectPr.find(qn('w:pgNumType'))
    if pg is None:
        pg = OxmlElement('w:pgNumType'); sectPr.append(pg)
    pg.set(qn('w:fmt'), fmt); pg.set(qn('w:start'), str(start))
    section.footer.is_linked_to_previous = False
    p = section.footer.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    fld = OxmlElement('w:fldSimple'); fld.set(qn('w:instr'), ' PAGE ')
    r = OxmlElement('w:r')
    rpr = OxmlElement('w:rPr')
    rf = OxmlElement('w:rFonts'); rf.set(qn('w:ascii'), FONT); rf.set(qn('w:hAnsi'), FONT)
    col = OxmlElement('w:color'); col.set(qn('w:val'), '000000')
    sz = OxmlElement('w:sz'); sz.set(qn('w:val'), '24')
    u = OxmlElement('w:u'); u.set(qn('w:val'), 'none')
    for el in (rf, col, sz, u):
        rpr.append(el)
    t = OxmlElement('w:t'); t.text = '1'
    r.append(rpr); r.append(t); fld.append(r)
    p._p.append(fld)


def toc_line(doc, label, page, level=0):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    p.paragraph_format.left_indent = Cm(0.0 if level == 0 else 0.75 * level)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.tab_stops.add_tab_stop(Cm(14.0), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
    r = p.add_run(f'{label}\t{page}')
    if level == 0:
        r.bold = True


# ============================================================ DETECTION
def detect_pages(pdf_path, reg):
    out = subprocess.run(['pdftotext', '-layout', pdf_path, '-'],
                         capture_output=True, text=True).stdout
    pages_text = out.split('\x0c')
    tokpage = {}
    for i, pg in enumerate(pages_text):
        for e in reg:
            if e['token'] in pg and e['token'] not in tokpage:
                tokpage[e['token']] = i
    first_tok = next(e['token'] for e in reg if e['cat'] == 'toc')
    base = tokpage.get(first_tok, 0)
    return {tok: (p - base + 1) for tok, p in tokpage.items()}


# ============================================================ BODY
def build_body(doc, reg):
    # ===== BAB I
    bab(doc, reg, 'I', 'PENDAHULUAN')
    h2num(doc, reg, '1.1', 'Latar Belakang')
    body(doc, 'Perkembangan teknologi informasi menyebabkan jumlah data yang dihasilkan dalam berbagai bidang seperti pendidikan, bisnis, dan industri terus meningkat. Data dalam jumlah besar tersebut dapat menjadi sumber informasi penting apabila diolah dan dianalisis dengan tepat. Namun, banyaknya data yang tersedia sering sulit dianalisis secara manual sehingga diperlukan metode untuk menggali pola dan pengetahuan dari data tersebut.')
    body(doc, 'Salah satu bidang yang digunakan untuk menemukan pola dan pengetahuan dari kumpulan data adalah data mining. Data mining merupakan proses menemukan pola, hubungan, dan informasi penting dari kumpulan data berukuran besar menggunakan metode statistik, machine learning, dan basis data (Larose dan Larose, 2014). Salah satu teknik yang banyak digunakan dalam data mining adalah clustering atau pengelompokan.')
    body(doc, 'Clustering merupakan teknik data mining yang mengelompokkan data berdasarkan kemiripan karakteristik tanpa memerlukan label kelas yang telah ditentukan sebelumnya. Salah satu pendekatan clustering adalah hierarchical clustering yang membentuk hirarki kelompok data. Berbeda dengan K-Means yang membutuhkan jumlah klaster (K) di awal dan DBSCAN yang berbasis kepadatan, hierarchical clustering membentuk struktur klaster bertingkat yang dapat divisualisasikan dalam bentuk dendrogram.')
    body(doc, 'Agglomerative Clustering merupakan salah satu metode hierarchical clustering dengan pendekatan bottom-up. Metode ini bekerja dengan memperlakukan setiap data sebagai satu klaster, kemudian menggabungkan dua klaster terdekat secara bertahap hingga seluruh data tergabung dalam satu klaster. Cara kerja ini membuat Agglomerative Clustering mudah ditelusuri secara manual dan jumlah klaster dapat ditentukan dari data melalui pemotongan dendrogram. Oleh karena itu, penelitian ini dilakukan untuk mempelajari konsep, cara kerja, serta penerapan algoritma Agglomerative Clustering dalam teknik clustering pada data mining.')

    h2num(doc, reg, '1.2', 'Rumusan Masalah')
    body(doc, 'Berdasarkan latar belakang di atas, dapat dirumuskan beberapa masalah penelitian sebagai berikut.', indent=False)
    for i, t in enumerate([
        'Apa yang dimaksud dengan data mining dan teknik clustering.',
        'Bagaimana konsep hierarchical clustering dalam pengelompokan data.',
        'Bagaimana cara kerja algoritma Agglomerative Clustering dalam membentuk klaster.',
        'Bagaimana penerapan matriks jarak, linkage, dan dendrogram dalam menentukan jumlah klaster.'], 1):
        numbered(doc, i, t)

    h2num(doc, reg, '1.3', 'Tujuan Penelitian')
    body(doc, 'Berdasarkan rumusan masalah, tujuan yang ingin dicapai dalam penelitian ini adalah sebagai berikut.', indent=False)
    for i, t in enumerate([
        'Memahami konsep data mining dan teknik clustering.',
        'Mengetahui konsep dan jenis hierarchical clustering.',
        'Mempelajari cara kerja algoritma Agglomerative Clustering dalam proses pengelompokan data.',
        'Memahami penerapan matriks jarak, linkage, dan dendrogram pada Agglomerative Clustering.'], 1):
        numbered(doc, i, t)

    h2num(doc, reg, '1.4', 'Manfaat Penelitian')
    body(doc, 'Manfaat yang diharapkan dari penelitian ini adalah sebagai berikut.', indent=False)
    numbered(doc, 1, 'Manfaat Akademis. Penelitian ini diharapkan dapat menambah wawasan dan pemahaman mengenai penerapan data mining, khususnya teknik clustering menggunakan algoritma Agglomerative.')
    numbered(doc, 2, 'Manfaat Praktis. Penelitian ini diharapkan dapat menjadi referensi dalam penerapan algoritma Agglomerative Clustering untuk proses pengelompokan data pada berbagai permasalahan data mining.')
    numbered(doc, 3, 'Manfaat Bagi Penulis. Penelitian ini dapat meningkatkan pemahaman penulis mengenai konsep data mining, clustering, dan algoritma Agglomerative dalam pengolahan dan analisis data.')

    h2num(doc, reg, '1.5', 'Batasan Masalah')
    body(doc, 'Agar pembahasan lebih terarah, ditetapkan beberapa batasan masalah sebagai berikut.', indent=False)
    for i, t in enumerate([
        'Penelitian berfokus pada penerapan data mining menggunakan teknik clustering.',
        'Algoritma utama yang dibahas adalah Agglomerative Hierarchical Clustering.',
        'Perhitungan manual menggunakan ukuran jarak Euclidean dan metode single linkage.',
        'Dataset yang digunakan berupa data kecil (10 mahasiswa dengan dua atribut) agar setiap langkah dapat ditelusuri secara manual.',
        'Penentuan jumlah klaster dilakukan dengan memotong dendrogram pada lompatan jarak terbesar.',
        'Sebagai pembanding, ditampilkan pula hasil metode K-Means dan Apriori, namun pembahasan utama tetap pada Agglomerative Clustering.'], 1):
        numbered(doc, i, t)

    # ===== BAB II
    doc.add_page_break()
    bab(doc, reg, 'II', 'LANDASAN PUSTAKA')
    h2num(doc, reg, '2.1', 'Teknik Data Mining')
    body(doc, 'Data mining merupakan proses untuk menemukan pola, hubungan, dan kecenderungan yang bermanfaat dari kumpulan data berukuran besar. Menurut Larose dan Larose (2014), data mining digunakan untuk menggali informasi yang sebelumnya tersembunyi di dalam data sehingga dapat diubah menjadi pengetahuan yang berguna dalam pengambilan keputusan. Dalam penerapannya, data mining memiliki beberapa teknik utama, antara lain estimasi, prediksi, klasifikasi, clustering, dan asosiasi.')
    h3num(doc, reg, '2.1.1', 'Estimasi')
    body(doc, 'Estimasi merupakan teknik data mining yang digunakan untuk memperkirakan nilai dari suatu variabel target yang bersifat numerik berdasarkan sejumlah variabel prediktor. Contoh penerapannya adalah memperkirakan pendapatan seseorang berdasarkan usia, pendidikan, dan pengalaman kerja.')
    h3num(doc, reg, '2.1.2', 'Prediksi')
    body(doc, 'Prediksi merupakan teknik data mining yang digunakan untuk memperkirakan kejadian atau nilai yang kemungkinan terjadi pada masa mendatang. Teknik ini mirip dengan estimasi, tetapi lebih menekankan pada aspek waktu, yaitu bagaimana pola data saat ini atau masa lalu dapat digunakan untuk memperkirakan kondisi di masa depan.')
    h3num(doc, reg, '2.1.3', 'Klasifikasi')
    body(doc, 'Klasifikasi merupakan teknik data mining yang bertujuan menempatkan suatu data ke dalam kategori atau kelas tertentu yang telah ditentukan sebelumnya. Model dibangun menggunakan data yang sudah memiliki label kelas, kemudian digunakan untuk mengklasifikasikan data baru. Contoh algoritmanya adalah decision tree, naive Bayes, dan k-nearest neighbor.')
    h3num(doc, reg, '2.1.4', 'Clustering')
    body(doc, 'Clustering merupakan teknik data mining yang digunakan untuk mengelompokkan data berdasarkan kemiripan karakteristik antarobjek. Berbeda dengan klasifikasi, clustering tidak membutuhkan label kelas yang telah ditentukan sebelumnya. Data dikelompokkan secara otomatis ke dalam beberapa cluster, sehingga objek dalam satu cluster memiliki kemiripan yang tinggi, sedangkan objek pada cluster yang berbeda memiliki karakteristik yang lebih berbeda. Agglomerative Clustering yang dibahas dalam laporan ini termasuk dalam teknik clustering.')
    h3num(doc, reg, '2.1.5', 'Asosiasi')
    body(doc, 'Asosiasi merupakan teknik data mining yang digunakan untuk menemukan hubungan atau keterkaitan antaratribut dalam data. Teknik ini sering digunakan dalam market basket analysis untuk mengetahui item apa saja yang sering muncul bersamaan. Hasil teknik asosiasi berbentuk aturan, misalnya jika membeli roti maka cenderung membeli susu, yang umumnya diukur menggunakan nilai support dan confidence. Algoritma Apriori merupakan salah satu algoritma asosiasi yang populer.')

    h2num(doc, reg, '2.2', 'Clustering')
    body(doc, 'Clustering atau analisis klaster adalah proses membagi sekumpulan objek menjadi beberapa kelompok (cluster) sedemikian rupa sehingga objek dalam satu kelompok memiliki kemiripan yang tinggi dan berbeda dengan objek pada kelompok lain. Kemiripan antarobjek umumnya diukur menggunakan jarak, misalnya jarak Euclidean. Secara umum, metode clustering dapat dibagi menjadi dua pendekatan utama.')
    h3num(doc, reg, '2.2.1', 'Partitional Clustering')
    body(doc, 'Partitional clustering membagi data menjadi sejumlah klaster yang tidak saling tumpang tindih, di mana jumlah klaster (K) ditentukan di awal. Contoh paling umum adalah K-Means yang mengelompokkan data berdasarkan jarak terhadap centroid (titik pusat klaster). Kelemahan pendekatan ini adalah pengguna harus menentukan nilai K terlebih dahulu, misalnya dengan bantuan Elbow Method.')
    h3num(doc, reg, '2.2.2', 'Hierarchical Clustering')
    body(doc, 'Hierarchical clustering membentuk hirarki klaster bertingkat tanpa perlu menentukan jumlah klaster di awal. Pendekatan ini dibagi menjadi dua, yaitu agglomerative (bottom-up) yang dimulai dari setiap data sebagai klaster sendiri lalu digabung bertahap, dan divisive (top-down) yang dimulai dari satu klaster besar lalu dipecah bertahap. Hasil hierarchical clustering divisualisasikan dalam bentuk dendrogram, dan jumlah klaster ditentukan dengan memotong dendrogram pada ketinggian tertentu.')

    h2num(doc, reg, '2.3', 'Algoritma Agglomerative Clustering')
    body(doc, 'Agglomerative Hierarchical Clustering merupakan metode clustering hirarki dengan pendekatan bottom-up. Algoritma ini bekerja dengan langkah berikut: (1) setiap data diperlakukan sebagai satu klaster sehingga jumlah klaster awal sama dengan jumlah data; (2) hitung jarak antar semua klaster dalam bentuk matriks jarak; (3) gabungkan dua klaster yang memiliki jarak terdekat; (4) perbarui matriks jarak; dan (5) ulangi langkah 2 sampai 4 hingga seluruh data tergabung menjadi satu klaster. Seluruh proses penggabungan dicatat dan divisualisasikan sebagai dendrogram.')
    h3num(doc, reg, '2.3.1', 'Matriks Jarak (Euclidean Distance)')
    body(doc, 'Matriks jarak merupakan dasar perhitungan pada Agglomerative Clustering. Jarak antar dua titik data dihitung menggunakan jarak Euclidean dengan rumus berikut.', indent=False)
    plain_center(doc, 'd(p, q) = akar( (p1 - q1)^2 + (p2 - q2)^2 )', sb=6, sa=6)
    body(doc, 'dengan p dan q adalah dua titik data, serta indeks 1 dan 2 menyatakan atribut pertama dan kedua. Untuk n data, matriks jarak berukuran n x n, bersifat simetris, dengan nilai diagonal nol. Matriks inilah yang diperbarui pada setiap iterasi penggabungan.')
    h3num(doc, reg, '2.3.2', 'Metode Linkage')
    body(doc, 'Linkage menentukan cara menghitung jarak antar dua klaster yang masing-masing dapat berisi lebih dari satu anggota. Beberapa metode linkage yang umum digunakan dijelaskan sebagai berikut.', indent=False)
    numbered(doc, 1, 'Single linkage: jarak antar klaster diambil dari jarak minimum antar anggotanya. Mudah dihitung manual namun rentan terhadap efek chaining.')
    numbered(doc, 2, 'Complete linkage: jarak antar klaster diambil dari jarak maksimum antar anggotanya, sehingga klaster cenderung lebih kompak.')
    numbered(doc, 3, 'Average linkage: jarak antar klaster dihitung dari rata-rata seluruh pasangan anggota, merupakan kompromi antara single dan complete.')
    numbered(doc, 4, 'Ward linkage: penggabungan dilakukan dengan meminimalkan kenaikan total jarak kuadrat (SSE), sehingga klaster cenderung seimbang.')
    body(doc, 'Pada laporan ini, perhitungan manual menggunakan single linkage karena paling mudah ditelusuri, dengan rumus pembaruan jarak: d(Ci U Cj, Ck) = min( d(Ci, Ck), d(Cj, Ck) ).')
    h3num(doc, reg, '2.3.3', 'Dendrogram dan Penentuan Jumlah Klaster')
    body(doc, 'Dendrogram adalah diagram pohon yang memperlihatkan urutan penggabungan klaster beserta ketinggiannya, di mana ketinggian menyatakan jarak saat dua klaster digabung. Algoritma Agglomerative selalu berjalan sampai seluruh data tergabung menjadi satu klaster, sehingga jumlah klaster final ditentukan dengan memotong dendrogram. Salah satu cara objektif adalah memotong pada lompatan (gap) ketinggian penggabungan terbesar, karena gap tersebut menandakan batas alami antar kelompok data. Dengan demikian, jumlah klaster mengikuti karakteristik data, bukan ditentukan secara paksa di awal seperti pada K-Means.')

    h2num(doc, reg, '2.4', 'Machine Learning')
    body(doc, 'Machine learning merupakan cabang dari kecerdasan buatan (Artificial Intelligence) yang memungkinkan sistem komputer mempelajari pola dari data dan membuat keputusan secara otomatis tanpa harus diprogram secara eksplisit. Berdasarkan metode pembelajarannya, machine learning dibagi menjadi supervised learning, unsupervised learning, dan reinforcement learning.')
    h2num(doc, reg, '2.5', 'Unsupervised Learning')
    body(doc, 'Unsupervised learning merupakan metode machine learning yang menggunakan data tanpa label dalam proses pembelajarannya. Model berusaha menemukan struktur atau pola tersembunyi dalam data tanpa adanya target keluaran yang telah ditentukan. Clustering, termasuk Agglomerative Clustering, merupakan salah satu contoh utama unsupervised learning karena pengelompokan dilakukan murni berdasarkan kemiripan data tanpa label kelas. Beberapa teknik yang termasuk unsupervised learning antara lain:', indent=False)
    for i, t in enumerate(['K-Means Clustering', 'Agglomerative Hierarchical Clustering', 'DBSCAN', 'Association Rule (Apriori)'], 1):
        numbered(doc, i, t)

    # ===== BAB III
    doc.add_page_break()
    bab(doc, reg, 'III', 'HASIL DAN PEMBAHASAN')
    h2num(doc, reg, '3.1', 'Agglomerative Clustering')
    body(doc, 'Pada subbab ini dibahas penerapan algoritma Agglomerative Hierarchical Clustering pada data 10 mahasiswa dengan dua atribut, yaitu Nilai Tugas dan Nilai Ujian. Pembahasan dimulai dari metode, perhitungan matriks jarak dan langkah penggabungan, implementasi kode program, hingga hasil dan analisis jumlah klaster.')
    h3num(doc, reg, '3.1.1', 'Metode')
    body(doc, 'Metode yang digunakan adalah Agglomerative Hierarchical Clustering dengan pendekatan bottom-up dan metode single linkage. Data yang digunakan ditampilkan pada Tabel 3.1. Data sengaja dipilih kecil (10 mahasiswa) agar setiap langkah perhitungan, termasuk matriks jarak pada setiap iterasi, dapat ditelusuri secara manual.')

    caption(doc, reg, 'tbl', 'Tabel 3.1 Data 10 Mahasiswa')
    t1 = doc.add_table(rows=1, cols=3); t1.alignment = WD_TABLE_ALIGNMENT.CENTER; set_table_borders(t1)
    for j, h in enumerate(['Mahasiswa', 'Nilai Tugas', 'Nilai Ujian']):
        cell(t1.rows[0].cells[j], h, bold=True); set_cell_bg(t1.rows[0].cells[j], 'D9D9D9')
    for _, row in data.iterrows():
        cs = t1.add_row().cells
        cell(cs[0], row['Mhs']); cell(cs[1], row['Tugas']); cell(cs[2], row['Ujian'])

    body(doc, 'Langkah pertama adalah menghitung jarak Euclidean antar seluruh pasangan mahasiswa. Karena terdapat 10 data, matriks jarak berukuran 10 x 10 dan bersifat simetris dengan diagonal nol. Matriks jarak awal ditampilkan pada Tabel 3.2 (nilai dibulatkan dua desimal).')
    caption(doc, reg, 'tbl', 'Tabel 3.2 Matriks Jarak Awal Antar Mahasiswa (Euclidean)')
    t2 = doc.add_table(rows=1, cols=11); t2.alignment = WD_TABLE_ALIGNMENT.CENTER; set_table_borders(t2)
    cell(t2.rows[0].cells[0], '', bold=True); set_cell_bg(t2.rows[0].cells[0], 'D9D9D9')
    for j, nm in enumerate(names, 1):
        cell(t2.rows[0].cells[j], nm, bold=True, size=9); set_cell_bg(t2.rows[0].cells[j], 'D9D9D9')
    for i, nm in enumerate(names):
        cs = t2.add_row().cells
        cell(cs[0], nm, bold=True, size=9); set_cell_bg(cs[0], 'D9D9D9')
        for j in range(10):
            cell(cs[j + 1], f'{dist_mat[i, j]:.2f}', size=9)

    body(doc, 'Dari Tabel 3.2 terlihat bahwa jarak terkecil bernilai 1.00 (misalnya pasangan A-B). Pasangan inilah yang digabung pertama kali. Setelah penggabungan, matriks jarak diperbarui menggunakan rumus single linkage, yaitu jarak klaster gabungan ke klaster lain diambil dari nilai minimum. Proses ini diulang hingga seluruh data tergabung. Ringkasan seluruh langkah penggabungan ditampilkan pada Tabel 3.3.')
    caption(doc, reg, 'tbl', 'Tabel 3.3 Ringkasan Iterasi Penggabungan (Single Linkage)')
    t3 = doc.add_table(rows=1, cols=5); t3.alignment = WD_TABLE_ALIGNMENT.CENTER; set_table_borders(t3)
    for j, h in enumerate(['Iterasi', 'Klaster A', 'Klaster B', 'Jarak Merge', 'Sisa Klaster']):
        cell(t3.rows[0].cells[j], h, bold=True); set_cell_bg(t3.rows[0].cells[j], 'D9D9D9')
    for it, a, b, d, sisa in merge_rows:
        cs = t3.add_row().cells
        cell(cs[0], it); cell(cs[1], a, size=9); cell(cs[2], b, size=9)
        cell(cs[3], f'{d:.3f}'); cell(cs[4], sisa)
    body(doc, 'Pada Tabel 3.3 terlihat bahwa enam penggabungan pertama terjadi pada jarak yang kecil (1.00) karena masih menggabungkan data dalam kelompok yang sama. Penggabungan ketujuh terjadi pada jarak 1.414, sedangkan penggabungan kedelapan melonjak ke 3.606. Lonjakan inilah yang menjadi dasar penentuan jumlah klaster pada bagian hasil.')

    h3num(doc, reg, '3.1.2', 'Kode Program')
    body(doc, 'Implementasi algoritma Agglomerative Clustering dilakukan menggunakan bahasa pemrograman Python dengan pustaka numpy, pandas, dan scipy. Kode program menampilkan langkah penggabungan single linkage secara manual, kemudian memverifikasi hasilnya menggunakan fungsi linkage dari scipy serta menentukan jumlah klaster optimal dari lompatan jarak terbesar. Kode program ditampilkan pada Kode Program 3.1.')
    code_text = '''import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, fcluster

# Data 10 mahasiswa: Nilai Tugas dan Nilai Ujian
data = pd.DataFrame({
    'Mhs':   ['A','B','C','D','E','F','G','H','I','J'],
    'Tugas': [1, 2, 2, 5, 6, 5, 9, 9, 8, 10],
    'Ujian': [2, 2, 3, 5, 5, 6, 9, 8, 9, 10],
})
X = data[['Tugas','Ujian']].values
names = data['Mhs'].values

# Agglomerative single linkage manual (tampilkan tiap penggabungan)
def agglomerative_single(X, names):
    clusters = [[n] for n in names]
    M = squareform(pdist(X)).astype(float)
    np.fill_diagonal(M, np.inf)
    while len(clusters) > 1:
        i, j = np.unravel_index(np.argmin(M), M.shape)
        if i > j: i, j = j, i
        print(f'Gabung {clusters[i]} + {clusters[j]}  jarak={M[i,j]:.3f}')
        new = np.minimum(M[i,:], M[j,:]); new[i] = np.inf   # rumus MIN
        M[i,:] = new; M[:,i] = new
        M = np.delete(M, j, 0); M = np.delete(M, j, 1)
        clusters[i] = clusters[i] + clusters[j]; del clusters[j]

agglomerative_single(X, names)

# Verifikasi + penentuan jumlah klaster dari gap terbesar
Z = linkage(X, method='single')
gaps = np.diff(Z[:, 2])
i = int(np.argmax(gaps))
k = len(X) - (i + 1)
print('Jumlah klaster optimal =', k)
print('Label klaster:', fcluster(Z, t=k, criterion='maxclust'))'''
    code_box(doc, code_text)
    caption(doc, reg, 'code', 'Kode Program 3.1 Implementasi Agglomerative Clustering Manual')
    body(doc, 'Fungsi agglomerative_single bekerja dengan menyimpan setiap klaster sebagai daftar anggota, lalu pada setiap iterasi mencari sel matriks dengan jarak minimum menggunakan np.argmin. Dua klaster terdekat digabung, kemudian baris dan kolom matriks diperbarui dengan np.minimum sesuai aturan single linkage, dan klaster yang telah digabung dihapus. Setelah seluruh proses selesai, fungsi linkage dari scipy digunakan untuk memverifikasi hasil, dan jumlah klaster optimal ditentukan dari selisih (gap) ketinggian penggabungan terbesar menggunakan np.diff dan np.argmax.')

    h3num(doc, reg, '3.1.3', 'Hasil')
    body(doc, 'Sebaran data 10 mahasiswa ditampilkan pada Gambar 3.1. Secara visual, data membentuk tiga kelompok, yaitu kelompok nilai rendah (A, B, C), kelompok nilai menengah (D, E, F), dan kelompok nilai tinggi (G, H, I, J).')
    add_image(doc, 'fig31_scatter.png', 11)
    caption(doc, reg, 'fig', 'Gambar 3.1 Sebaran 10 Mahasiswa')
    body(doc, 'Hasil seluruh proses penggabungan divisualisasikan dalam bentuk dendrogram pada Gambar 3.2. Garis putus-putus merah menunjukkan titik potong otomatis pada ketinggian sekitar 2.51.')
    add_image(doc, 'fig32_dendrogram.png', 13)
    caption(doc, reg, 'fig', 'Gambar 3.2 Dendrogram Agglomerative Single Linkage')
    body(doc, 'Penentuan jumlah klaster dilakukan dengan mengamati lompatan ketinggian penggabungan. Urutan ketinggian penggabungan adalah 1.0 (enam kali), 1.414, 3.606, dan 4.243. Lompatan terbesar bernilai 2.191, yaitu antara ketinggian 1.414 dan 3.606. Lompatan ini terjadi ketika algoritma mulai menggabungkan dua kelompok yang berbeda, sehingga titik potong diletakkan tepat di bawahnya. Hasilnya, jumlah klaster optimal adalah tiga klaster, bukan dua. Hal ini menegaskan bahwa algoritma Agglomerative tidak berhenti di dua klaster, melainkan berjalan sampai satu klaster, dan jumlah klaster final ditentukan oleh karakteristik data. Hasil pengelompokan tiga klaster ditampilkan pada Gambar 3.3.')
    add_image(doc, 'fig33_hasil.png', 11)
    caption(doc, reg, 'fig', 'Gambar 3.3 Hasil Pengelompokan Tiga Klaster')
    body(doc, 'Untuk menegaskan bahwa jumlah klaster bergantung pada letak pemotongan dendrogram, dilakukan pemotongan menjadi 2, 3, dan 4 klaster seperti pada Gambar 3.4. Pada pemotongan 2 klaster, kelompok menengah ikut tergabung sehingga kurang sesuai. Pada 3 klaster, ketiga kelompok terpisah dengan bersih dan paling sesuai dengan sebaran data. Pada 4 klaster, salah satu kelompok mulai terpecah (over-segmentasi).')
    add_image(doc, 'fig34_potong.png', 14)
    caption(doc, reg, 'fig', 'Gambar 3.4 Perbandingan Pemotongan Dendrogram menjadi 2, 3, dan 4 Klaster')
    body(doc, 'Selain single linkage, dilakukan pula perbandingan empat metode linkage (single, complete, average, dan ward) seperti pada Gambar 3.5. Karena kelompok data terpisah cukup jelas, keempat metode tetap menghasilkan tiga klaster yang sama, dengan perbedaan terutama pada skala ketinggian penggabungan.')
    add_image(doc, 'fig35_linkage.png', 13)
    caption(doc, reg, 'fig', 'Gambar 3.5 Perbandingan Empat Metode Linkage')

    h2num(doc, reg, '3.2', 'Perbandingan dengan Metode Lain')
    body(doc, 'Sebagai pelengkap, hasil Agglomerative Clustering dibandingkan dengan dua metode lain yang juga dipelajari kelompok, yaitu K-Means (clustering partitional) dan Apriori (association rule). Perbandingan ini bertujuan memperlihatkan posisi Agglomerative Clustering di antara teknik data mining lainnya.')
    h3num(doc, reg, '3.2.1', 'K-Means Clustering')
    body(doc, 'K-Means diterapkan pada data 10 pelanggan dengan atribut Age dan Income. Berbeda dengan Agglomerative, K-Means memerlukan penentuan jumlah klaster (K) di awal. Penentuan K dilakukan dengan Elbow Method, yaitu mengamati titik di mana penurunan SSE mulai melandai, seperti pada Gambar 3.6. Hal ini berbeda dengan Agglomerative yang menentukan jumlah klaster dari dendrogram setelah seluruh proses selesai.')
    add_image(doc, 'fig36_kmeans_elbow.png', 12)
    caption(doc, reg, 'fig', 'Gambar 3.6 Elbow Method pada K-Means (Pembanding)')
    h3num(doc, reg, '3.2.2', 'Apriori (Association Rule)')
    body(doc, 'Apriori merupakan algoritma asosiasi yang menganalisis 10 transaksi dengan lima produk (susu, gula, teh, roti, kopi). Berbeda dengan clustering yang mengelompokkan data, Apriori menemukan aturan keterkaitan antaritem berdasarkan nilai support dan confidence. Beberapa aturan asosiasi terkuat ditampilkan pada Tabel 3.4.')
    caption(doc, reg, 'tbl', 'Tabel 3.4 Contoh Aturan Asosiasi Terkuat (Apriori)')
    t4 = doc.add_table(rows=1, cols=4); t4.alignment = WD_TABLE_ALIGNMENT.CENTER; set_table_borders(t4)
    for j, h in enumerate(['Aturan', 'Support', 'Confidence', 'Final']):
        cell(t4.rows[0].cells[j], h, bold=True); set_cell_bg(t4.rows[0].cells[j], 'D9D9D9')
    for rule in [('teh -> gula', '0.50', '1.00', '0.500'),
                 ('gula -> teh', '0.50', '0.63', '0.313'),
                 ('susu -> gula', '0.40', '0.67', '0.267'),
                 ('roti -> susu', '0.30', '0.75', '0.225'),
                 ('kopi -> susu', '0.30', '0.75', '0.225')]:
        cs = t4.add_row().cells
        for j, v in enumerate(rule):
            cell(cs[j], v)
    body(doc, 'Dari perbandingan tersebut terlihat bahwa ketiga metode memiliki tujuan berbeda. Apriori digunakan untuk menemukan keterkaitan antaritem, K-Means untuk pengelompokan dengan jumlah klaster yang ditentukan di awal, sedangkan Agglomerative Clustering untuk membentuk hirarki klaster lengkap tanpa perlu menentukan jumlah klaster terlebih dahulu.')

    # ===== BAB IV
    doc.add_page_break()
    bab(doc, reg, 'IV', 'PENUTUP')
    h2num(doc, reg, '4.1', 'Kesimpulan')
    body(doc, 'Berdasarkan hasil pembahasan mengenai penerapan algoritma Agglomerative Clustering dalam proses pengelompokan data, dapat ditarik beberapa kesimpulan. Data mining merupakan proses untuk menemukan pola dan pengetahuan yang bermanfaat dari kumpulan data berukuran besar, dengan salah satu tekniknya adalah clustering. Clustering mengelompokkan data berdasarkan kemiripan tanpa memerlukan label kelas.')
    body(doc, 'Agglomerative Hierarchical Clustering bekerja secara bottom-up dengan menggabungkan dua klaster terdekat secara bertahap. Untuk 10 data, proses penggabungan berlangsung sebanyak sembilan iterasi hingga terbentuk satu klaster. Matriks jarak diperbarui pada setiap iterasi menggunakan rumus single linkage, yaitu jarak minimum antar anggota. Jumlah klaster final tidak ditentukan di awal, melainkan dengan memotong dendrogram pada lompatan jarak terbesar. Untuk data yang digunakan, lompatan terbesar menghasilkan tiga klaster yang sesuai dengan sebaran data, yaitu kelompok nilai rendah, menengah, dan tinggi.')
    h3num(doc, reg, '4.1.1', 'Kelebihan Agglomerative Clustering')
    for i, t in enumerate([
        'Tidak memerlukan penentuan jumlah klaster di awal, berbeda dengan K-Means.',
        'Menghasilkan hirarki klaster lengkap yang divisualisasikan dalam dendrogram.',
        'Jumlah klaster dapat ditentukan secara fleksibel dengan memotong dendrogram pada ketinggian tertentu.',
        'Mudah ditelusuri secara manual pada data berukuran kecil sehingga cocok untuk pembelajaran konsep.',
        'Dapat menggunakan berbagai metode linkage (single, complete, average, ward) sesuai karakteristik data.'], 1):
        numbered(doc, i, t)
    h3num(doc, reg, '4.1.2', 'Kekurangan Agglomerative Clustering')
    for i, t in enumerate([
        'Memiliki kompleksitas komputasi yang tinggi sehingga kurang efisien untuk data berukuran sangat besar.',
        'Penggabungan yang sudah dilakukan tidak dapat dibatalkan, sehingga kesalahan pada langkah awal akan terbawa.',
        'Metode single linkage rentan terhadap efek chaining, yaitu klaster dapat memanjang mengikuti rantai titik yang berdekatan.',
        'Penentuan titik potong dendrogram masih bersifat subjektif, meskipun dapat dibantu dengan analisis lompatan jarak terbesar.',
        'Sensitif terhadap perbedaan skala atribut sehingga pada kasus tertentu memerlukan standarisasi data.'], 1):
        numbered(doc, i, t)
    h2num(doc, reg, '4.2', 'Saran')
    body(doc, 'Berdasarkan hasil dan pembahasan, terdapat beberapa saran untuk pengembangan penelitian selanjutnya. Pertama, penelitian dapat dilakukan pada dataset yang lebih besar dan kompleks untuk melihat kinerja Agglomerative Clustering pada data nyata, sekaligus mengevaluasi keterbatasan komputasinya. Kedua, penelitian dapat membandingkan berbagai metode linkage secara lebih mendalam menggunakan ukuran evaluasi klaster seperti Silhouette Score untuk menentukan metode yang paling sesuai. Ketiga, penentuan jumlah klaster dapat dikombinasikan dengan metode evaluasi lain agar lebih objektif. Terakhir, perbandingan kinerja antara Agglomerative Clustering dengan metode clustering lain seperti K-Means dan DBSCAN dapat dilakukan untuk memperkaya analisis dan memberikan pemahaman yang lebih luas mengenai pemilihan metode clustering yang sesuai.')

    # ===== DAFTAR PUSTAKA
    doc.add_page_break()
    special_heading(doc, reg, 'DAFTAR PUSTAKA')
    for r in [
        'Han, J., Kamber, M., & Pei, J. (2012). Data Mining: Concepts and Techniques (3rd ed.). Waltham: Morgan Kaufmann Publishers.',
        'Larose, D. T., & Larose, C. D. (2014). Discovering Knowledge in Data: An Introduction to Data Mining (2nd ed.). New Jersey: John Wiley & Sons Inc.',
        'Tan, P.-N., Steinbach, M., Karpatne, A., & Kumar, V. (2019). Introduction to Data Mining (2nd ed.). New York: Pearson.',
    ]:
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.left_indent = Cm(1.0)
        p.paragraph_format.first_line_indent = Cm(-1.0)
        p.paragraph_format.space_after = Pt(6)
        p.add_run(r)

    # ===== LAMPIRAN
    doc.add_page_break()
    special_heading(doc, reg, 'LAMPIRAN')
    for label, desc, url in [
        ('LAMPIRAN 1.', ' Notebook Agglomerative Clustering (Tugas 3)',
         'https://github.com/ravi-arnan/DataMining/blob/main/Tugas3_Agglomerative.ipynb'),
        ('LAMPIRAN 2.', ' Notebook K-Means Clustering dan Elbow Method (Tugas 2)',
         'https://github.com/ravi-arnan/DataMining/blob/main/Tugas2_KMeans_Elbow.ipynb'),
        ('LAMPIRAN 3.', ' Notebook Algoritma Apriori (Tugas 1)',
         'https://github.com/ravi-arnan/DataMining/blob/main/Tugas1_Apriori.ipynb'),
    ]:
        p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        rr = p.add_run(label); rr.bold = True; p.add_run(desc)
        p2 = doc.add_paragraph(); p2.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        ru = p2.add_run(url); ru.font.color.rgb = RGBColor(0x05, 0x63, 0xC1); ru.underline = True


# ============================================================ FRONT MATTER
def build_cover(doc):
    plain_center(doc, 'LAPORAN TUGAS AKHIR DATA MINING', bold=True, sb=24)
    plain_center(doc, 'METODE AGGLOMERATIVE CLUSTERING', bold=True, sa=18)
    pic = doc.add_paragraph(); pic.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pic.add_run().add_picture(os.path.join(FIG, 'logo_udayana.png'), width=Cm(4.2))
    plain_center(doc, '', sa=12)
    plain_center(doc, 'DOSEN PENGAMPU', bold=True, sb=12)
    plain_center(doc, 'Dr. Eng. I Putu Agung Bayupati, S.T., M.T.', sa=18)
    plain_center(doc, 'DISUSUN OLEH', bold=True, sb=12)
    plain_center(doc, 'KELOMPOK 10', bold=True)
    for nm, nim in [('Ravi Arnan Irianto', '2305551076'),
                    ('Ezza Putra Wibawa', '2305551144'),
                    ('Ketut Riski Prananda', '2005551125')]:
        plain_center(doc, f'{nm}\t\t({nim})')
    plain_center(doc, 'MATA KULIAH', bold=True, sb=18)
    plain_center(doc, 'Data Mining (B)', sa=24)
    plain_center(doc, 'PROGRAM STUDI TEKNOLOGI INFORMASI', bold=True, sb=18)
    plain_center(doc, 'FAKULTAS TEKNIK', bold=True)
    plain_center(doc, 'UNIVERSITAS UDAYANA', bold=True)
    plain_center(doc, 'BALI', bold=True)
    plain_center(doc, '2026', bold=True)


def build_front(doc, reg, pages):
    plain_center(doc, 'DAFTAR ISI', bold=True, sa=12)
    for e in reg:
        if e['cat'] == 'toc':
            toc_line(doc, e['label'], pages.get(e['token'], 0), e['level'])
    doc.add_page_break()
    plain_center(doc, 'DAFTAR TABEL', bold=True, sa=12)
    for e in reg:
        if e['cat'] == 'tbl':
            toc_line(doc, e['label'], pages.get(e['token'], 0), 0)
    doc.add_page_break()
    plain_center(doc, 'DAFTAR GAMBAR', bold=True, sa=12)
    for e in reg:
        if e['cat'] == 'fig':
            toc_line(doc, e['label'], pages.get(e['token'], 0), 0)
    doc.add_page_break()
    plain_center(doc, 'DAFTAR KODE PROGRAM', bold=True, sa=12)
    for e in reg:
        if e['cat'] == 'code':
            toc_line(doc, e['label'], pages.get(e['token'], 0), 0)


# ============================================================ ASSEMBLE
def assemble(pages):
    reg = []
    build_body(Document(), reg)  # dry run to fill registry order/tokens
    doc = Document()
    set_base_style(doc)
    style_heading(doc, 'Heading 1', 14)
    style_heading(doc, 'Heading 2', 12)
    style_heading(doc, 'Heading 3', 12)
    s = doc.sections[0]
    s.top_margin = Cm(3); s.bottom_margin = Cm(3); s.left_margin = Cm(4); s.right_margin = Cm(3)
    s.page_height = Cm(29.7); s.page_width = Cm(21)
    build_cover(doc)
    s.footer.is_linked_to_previous = False  # cover: no page number

    doc.add_section(WD_SECTION.NEW_PAGE)
    s2 = doc.sections[1]
    s2.top_margin = Cm(3); s2.bottom_margin = Cm(3); s2.left_margin = Cm(4); s2.right_margin = Cm(3)
    reg2 = []
    build_body(Document(), reg2)
    build_front(doc, reg2, pages)
    page_footer(s2, 'lowerRoman', 1)

    doc.add_section(WD_SECTION.NEW_PAGE)
    s3 = doc.sections[2]
    s3.top_margin = Cm(3); s3.bottom_margin = Cm(3); s3.left_margin = Cm(4); s3.right_margin = Cm(3)
    page_footer(s3, 'decimal', 1)
    reg3 = []
    build_body(doc, reg3)
    return doc


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'passB'
    if mode == 'passA':
        doc = assemble(pages={})
        doc.save(TMP_DOCX)
        print('passA saved:', TMP_DOCX)
    else:
        reg = []
        build_body(Document(), reg)
        pages = detect_pages(TMP_PDF, reg)
        doc = assemble(pages)
        doc.save(OUT_DOCX)
        print('Final saved:', OUT_DOCX)
        print('Detected pages sample:', {e['label']: pages.get(e['token']) for e in reg[:6]})
