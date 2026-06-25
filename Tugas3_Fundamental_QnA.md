# Persiapan FUNDAMENTAL — Klasterisasi / Agglomerative Clustering

Lembar konsep dasar yang biasa **dikejar dosen** saat menguji pemahaman, bukan sekadar angka hasil.
Untuk detail angka notebook, lihat `Tugas3_Persiapan_QnA.md`.

> **Kelompok 10 masuk kategori: KLASTERISASI (Clustering).** Tugas spesifiknya: **Agglomerative Hierarchical Clustering**.

---

## A. Fundamental Data Mining (paling sering ditanya di awal)

**1. Apa itu data mining?**
Proses menggali **pola, pengetahuan, atau informasi berguna** yang sebelumnya tidak diketahui dari data berukuran besar. Sering disebut bagian dari proses **KDD (Knowledge Discovery in Databases)**.

**2. Sebutkan tugas/kategori utama data mining.**
Lima yang umum diajarkan:
1. **Estimasi** — menebak nilai numerik kontinu (mis. estimasi gaji). *Output: angka.*
2. **Prediksi / Forecasting** — estimasi untuk nilai **di masa depan** (mis. ramalan penjualan).
3. **Klasifikasi** — menempatkan data ke **kelas/label yang sudah ada** (mis. spam / bukan spam).
4. **Klasterisasi (Clustering)** — mengelompokkan data **tanpa label** menjadi kelompok mirip. ← **tugas kita**
5. **Asosiasi** — menemukan aturan "jika A maka B" (mis. market basket / Apriori).

**3. Di kategori mana tugas kita, dan kenapa?**
**Klasterisasi.** Karena Agglomerative mengelompokkan mahasiswa berdasarkan kemiripan nilai **tanpa label/kelas yang ditentukan sebelumnya** — komputer sendiri yang menemukan kelompoknya.

---

## B. Supervised vs Unsupervised (pertanyaan kunci)

**4. Clustering itu supervised atau unsupervised?**
**Unsupervised learning** — data **tidak punya label/target**. Algoritma mencari struktur sendiri.

**5. Apa beda supervised dan unsupervised?**
- **Supervised:** ada label/jawaban benar saat melatih (klasifikasi, regresi/estimasi). Tujuannya memetakan input → output yang diketahui.
- **Unsupervised:** tidak ada label (clustering, asosiasi). Tujuannya menemukan pola/struktur tersembunyi.

**6. Apa beda CLUSTERING vs KLASIFIKASI?** *(sangat sering ditanya)*
| | Klasifikasi | Klasterisasi |
|---|---|---|
| Label | **Sudah ada** (data berlabel) | **Tidak ada** |
| Jenis | Supervised | Unsupervised |
| Tujuan | Menempatkan data baru ke kelas yang sudah didefinisikan | Menemukan kelompok alami dari data |
| Contoh | Email → spam/bukan | Kelompokkan pelanggan jadi segmen yang belum diketahui |

Kalimat aman: *"Klasifikasi tahu dulu kelasnya lalu menggolongkan; clustering tidak tahu kelasnya, justru kelas/kelompoknya yang dicari."*

---

## C. Fundamental Clustering

**7. Apa itu clustering / klaster?**
**Klaster** = kumpulan objek yang **mirip satu sama lain** (dalam satu kelompok) dan **berbeda** dengan objek di kelompok lain. **Clustering** = proses membentuk klaster itu.

**8. Apa ciri clustering yang baik?**
- **Kohesi tinggi (intra-cluster):** anggota dalam satu klaster sangat mirip (jarak kecil).
- **Separasi tinggi (inter-cluster):** antar klaster berbeda jelas (jarak besar).
- Ringkas: **maksimalkan kemiripan dalam klaster, minimalkan kemiripan antar klaster.**

**9. Apa saja jenis metode clustering?**
- **Partitional** — bagi data jadi K kelompok sekaligus, mis. **K-Means**.
- **Hierarchical** — bangun hirarki bertingkat, mis. **Agglomerative (bottom-up)** & **Divisive (top-down)**. ← kita di sini
- **Density-based** — berdasarkan kepadatan, mis. **DBSCAN** (bisa temukan bentuk tak beraturan & outlier).
- **Model-based** — asumsi distribusi, mis. **Gaussian Mixture Model**.

**10. Contoh penerapan clustering di dunia nyata?**
Segmentasi pelanggan, pengelompokan dokumen/berita, deteksi anomali, kompresi gambar, pengelompokan pasien/penyakit.

---

## D. Fundamental Jarak & Kemiripan

**11. Bagaimana komputer mengukur "mirip"?**
Lewat **jarak (distance)**. Makin **kecil** jarak → makin **mirip**. Jadi kemiripan diukur sebagai kebalikan dari jarak.

**12. Sebutkan ukuran jarak yang umum.**
- **Euclidean** — garis lurus: √Σ(xᵢ−yᵢ)². ← yang kita pakai
- **Manhattan (city block)** — Σ|xᵢ−yᵢ|.
- **Cosine similarity** — sudut antar vektor (sering untuk teks).
- **Minkowski** — bentuk umum (Euclidean & Manhattan adalah kasus khususnya).

**13. Kenapa data kadang harus distandarisasi/normalisasi dulu?**
Kalau skala fitur beda jauh (mis. umur 0–80 vs penghasilan jutaan), fitur berskala besar akan **mendominasi** jarak. Standarisasi (z-score) atau normalisasi (0–1) menyetarakan kontribusi tiap fitur.
*(Catatan untuk data kita: fitur Tugas & Ujian sudah satu skala 0–10, jadi tidak perlu distandarisasi.)*

---

## E. Fundamental Agglomerative (inti tugas)

**14. Jelaskan Agglomerative secara singkat.**
Clustering **hierarki bottom-up (AGNES)**: tiap data mulai sebagai klaster sendiri → gabung **dua klaster terdekat** → perbarui jarak → ulangi sampai tersisa **satu klaster**. Riwayatnya = **dendrogram**.

**15. Langkah algoritmanya?**
1. Tiap titik = 1 klaster (n klaster).
2. Hitung **matriks jarak** antar klaster.
3. Gabung **dua klaster terdekat**.
4. **Perbarui** matriks jarak (pakai aturan linkage).
5. Ulangi 2–4 sampai jadi 1 klaster.
6. **Potong dendrogram** untuk menentukan jumlah klaster akhir.

**16. Apa itu LINKAGE dan jenisnya?**
Aturan mengukur jarak antar **klaster** (bukan antar titik):
- **Single (MIN):** pasangan titik terdekat — rawan *chaining*.
- **Complete (MAX):** pasangan terjauh — klaster kompak.
- **Average:** rata-rata semua pasangan.
- **Ward:** minimalkan kenaikan SSE — klaster seukuran.

**17. Apa itu dendrogram & cara membacanya?**
Diagram pohon riwayat penggabungan. **Sumbu-Y = jarak saat dua klaster digabung.** Makin tinggi garis gabung, makin beda kelompok yang disatukan. Jumlah klaster ditentukan dengan **memotong garis horizontal** — jumlah cabang terpotong = jumlah klaster, idealnya potong di **gap (lompatan) terbesar**.

**18. Bagaimana menentukan jumlah klaster (K)?**
Bukan ditetapkan asal — lihat **gap tinggi merge terbesar** di dendrogram, didukung skor validasi (silhouette). Untuk data kita, gap terbesar memberi **3 klaster** (nilai rendah / menengah / tinggi).

---

## F. Fundamental Validasi

**19. Bagaimana tahu hasil clustering bagus, padahal tak ada label?**
Pakai **validasi internal** (tanpa label):
- **Silhouette Coefficient** — seberapa cocok titik dengan klasternya (rentang −1..1, makin tinggi makin baik).
- **SSE / inertia** — total jarak ke pusat klaster (dipakai Elbow di K-Means).
- **CPCC** — khusus hierarki: kesetiaan dendrogram terhadap jarak asli.

**20. Agglomerative vs K-Means — bedanya fundamental?**
- K-Means: **harus tentukan K di awal**, hasil **bisa berubah** karena pusat awal acak, cepat untuk data besar.
- Agglomerative: **tidak perlu K di awal** (lihat dendrogram dulu), hasil **deterministik**, tapi **mahal** untuk data besar (±O(n²)) dan penggabungan **tidak bisa dibatalkan**.

---

## G. Pertanyaan Pembuka Khas Dosen (jawab pendek & percaya diri)

- **"Tugasmu masuk kategori data mining yang mana?"** → Klasterisasi (clustering).
- **"Itu supervised atau unsupervised?"** → Unsupervised — datanya tidak berlabel.
- **"Bedanya dengan klasifikasi apa?"** → Klasifikasi kelasnya sudah ada; clustering kelasnya dicari.
- **"Bagaimana mesin tahu dua data mirip?"** → Lewat jarak; makin kecil jarak makin mirip (kami pakai Euclidean).
- **"Kenapa pilih hierarchical?"** → Tidak perlu menentukan jumlah klaster di awal & hasilnya deterministik.
- **"Hasil akhirnya berapa klaster dan kenapa?"** → 3 klaster, dari gap terbesar di dendrogram + didukung silhouette.
