# Persiapan Tanya-Jawab — Tugas 3: Agglomerative Hierarchical Clustering

Daftar pertanyaan yang mungkin ditanyakan dosen beserta jawaban model.
Angka di sini sesuai hasil notebook `Tugas3_Agglomerative.ipynb`.
Untuk pertanyaan konsep dasar (data mining, supervised vs unsupervised, beda klasifikasi), lihat `Tugas3_Fundamental_QnA.md`.

**Dataset:** 10 mahasiswa, 2 fitur numerik (skala 0–10)

| Mhs | Tugas | Ujian |
|-----|-------|-------|
| A | 1 | 2 |
| B | 2 | 2 |
| C | 2 | 3 |
| D | 5 | 5 |
| E | 6 | 5 |
| F | 5 | 6 |
| G | 9 | 9 |
| H | 9 | 8 |
| I | 8 | 9 |
| J | 10 | 10 |

**Hasil akhir:** 3 klaster → `{A, B, C}` (nilai rendah), `{D, E, F}` (nilai menengah), `{G, H, I, J}` (nilai tinggi)

---

## A. Konsep Dasar

**1. Apa itu Agglomerative Hierarchical Clustering?**
Metode clustering *bottom-up* (AGNES): setiap data mulai sebagai klaster sendiri, lalu dua klaster terdekat digabung berulang kali sampai tersisa satu klaster. Riwayat penggabungan digambarkan sebagai dendrogram.

**2. Apa beda Agglomerative dengan Divisive?**
Agglomerative = bottom-up (gabung dari banyak ke satu). Divisive (DIANA) = top-down (belah dari satu ke banyak). Notebook ini pakai agglomerative.

**3. Kenapa pakai hierarchical, bukan K-Means?**
Hierarchical **tidak perlu menentukan K di awal** — K dipilih setelah melihat dendrogram. Juga menampilkan struktur bertingkat dan hasilnya deterministik (tidak bergantung inisialisasi acak seperti K-Means).

**4. Apa kelebihan & kekurangan hierarchical clustering?**
Kelebihan: tidak perlu K di awal, hasil deterministik, dendrogram informatif. Kekurangan: mahal untuk data besar (≈O(n² log n)), penggabungan **tidak bisa dibatalkan** (greedy), dan sensitif terhadap outlier/noise (terutama single linkage).

---

## B. Dataset & Fitur

**5. Apa saja fiturnya?**
Dua fitur numerik: **Tugas** dan **Ujian**, keduanya skala 0–10. Kolom **Mhs** (A–J) hanya label/ID, **tidak** ikut dihitung. Di kode: `X = data[['Tugas','Ujian']].values`.

**6. Kenapa cuma 2 fitur?**
Pilihan didaktik, bukan batasan algoritma. Dengan 2 fitur, langkah algoritma bisa ditelusuri manual dan klaster bisa divisualisasi di scatter plot 2D. Metodenya tetap berlaku untuk fitur berapa pun.

**7. Datanya dari mana / apakah data nyata?**
Data sintetik (dummy) yang diketik langsung di notebook, bukan file eksternal. Sengaja dibuat agar membentuk tiga kelompok jelas (rendah, menengah, tinggi) sehingga cocok untuk demonstrasi.

**8. Kenapa 10 data?**
Cukup kecil untuk ditelusuri manual setiap iterasi (10 data = **9 kali penggabungan**), tapi cukup besar untuk memunculkan lebih dari dua kelompok sehingga penentuan jumlah klaster jadi menarik.

**9. Kalau fiturnya banyak, apa yang berubah?**
Rumus jarak Euclidean tetap, hanya menjumlah semua dimensi: √(Σᵢ(Δxᵢ)²). Tambahan: bila skala antar fitur berbeda jauh, **harus distandarisasi dulu** (mis. z-score) agar tidak ada fitur yang mendominasi.

---

## C. Jarak (Distance)

**10. Kenapa pakai jarak Euclidean?**
Cocok untuk data numerik kontinu, dan paling intuitif (jarak garis lurus antar titik). Rumus 2D: d = √[(x₁−x₂)² + (y₁−y₂)²].

**11. Kenapa data tidak dinormalisasi/distandarisasi?**
Karena kedua fitur (Tugas & Ujian) **sudah satu skala 0–10**, jadi tidak ada fitur yang mendominasi jarak. Normalisasi diperlukan hanya kalau skala fitur berbeda jauh.

**12. Apa itu matriks jarak (distance matrix)?**
Matriks simetris n×n berisi jarak antar semua pasangan titik. Dipakai sebagai titik awal proses penggabungan. Di kode dihitung dengan `pdist` lalu `squareform`.

**13. Pasangan terdekat di data ini yang mana?**
Ada beberapa pasangan berjarak **1.0** (seri): **A–B, B–C, D–E, D–F, G–H, G–I**. Penggabungan-penggabungan pertama terjadi di antara pasangan-pasangan terdekat ini di tiap kelompok.

---

## D. Linkage (Metode Penggabungan)

**14. Apa itu linkage?**
Aturan untuk mengukur jarak antar **klaster** (bukan antar titik). Menentukan pasangan klaster mana yang digabung tiap langkah.

**15. Jelaskan single / complete / average / Ward.**
- **Single (MIN):** jarak antar klaster = pasangan titik **terdekat**. Rawan *chaining effect*.
- **Complete (MAX):** pakai pasangan **terjauh**. Menghasilkan klaster kompak.
- **Average (UPGMA):** rata-rata jarak semua pasangan antar klaster.
- **Ward:** gabung pasangan yang menambah **SSE** (sum of squared error) paling kecil. Cenderung klaster seukuran.

**16. Apa itu chaining effect?**
Kelemahan single linkage: klaster bisa memanjang seperti rantai karena hanya melihat titik terdekat, sehingga dua kelompok berbeda bisa "tersambung" lewat satu titik perantara.

**17. Apa itu rumus Lance–Williams?**
Rumus rekursif umum untuk memperbarui jarak setelah penggabungan. Semua linkage (single, complete, average, Ward) hanyalah kasus khusus dengan koefisien (αᵢ, αⱼ, β, γ) yang berbeda.

**18. Metode mana yang dipakai di analisis utama?**
Single linkage untuk perhitungan manual dan dendrogram utama; keempat metode dibandingkan dan dievaluasi CPCC-nya di bagian perbandingan.

---

## E. Dendrogram

**19. Apa itu dendrogram dan cara membacanya?**
Diagram pohon riwayat penggabungan. Sumbu-Y = jarak saat dua klaster digabung. Makin tinggi garis penggabungan, makin berbeda kelompok yang digabung.

**20. Bagaimana menentukan jumlah klaster dari dendrogram?**
Tarik garis horizontal pada ketinggian tertentu; jumlah cabang yang terpotong = jumlah klaster. Idealnya potong pada celah (gap) tinggi terbesar.

---

## F. Penentuan Jumlah Klaster (K)

**21. K = 3 ditentukan dari mana?** *(pertanyaan kunci)*
Bukan ditetapkan sembarangan, tapi muncul dari sinyal yang sejalan:
1. **Gap tinggi merge terbesar.** Tinggi penggabungan single linkage berurutan: enam kali **1.0**, lalu **1.4142**, **3.6056**, **4.2426**. Lompatan terbesar = **+2.1913** (dari 1.4142 ke 3.6056). Memotong tepat sebelum lompatan itu menyisakan **3 klaster**.
2. **Silhouette tertinggi di k=3** = **0.7367** (lihat bagian validasi), lebih tinggi dari k=2 (0.6264) dan k=4 (0.5727).
3. **Visual dendrogram:** garis potong melewati gap terbesar dan memotong tepat 3 cabang.

**22. Bukankah ada banyak tinggi merge yang seri (enam kali 1.0)?**
Ya, di bagian bawah dendrogram ada penggabungan seri (jarak 1.0) karena tiap kelompok punya beberapa pasangan sama dekat. Namun seri itu **tidak memengaruhi jumlah klaster akhir**, karena garis potong berada **di atasnya** (pada gap besar 2.1913). Yang menentukan partisi adalah penggabungan tinggi, bukan yang di dasar.

**23. Kenapa tidak berhenti di 2 klaster saja?**
Gap terbesar (2.1913) memberi 3 klaster, dan silhouette k=3 (0.7367) > k=2 (0.6264). Jadi data memang lebih wajar dibagi menjadi tiga kelompok: nilai rendah, menengah, dan tinggi.

---

## G. Validasi Klaster

**24. Apa itu CPCC (Cophenetic Correlation Coefficient)?**
Korelasi antara jarak asli antar titik (dari `pdist`) dengan jarak kofenetik (tinggi penggabungan di dendrogram). Mengukur seberapa setia dendrogram terhadap struktur jarak asli. Rentang −1..1; makin mendekati 1 makin baik.

**25. Berapa nilai CPCC-nya?**
single **0.7945**, complete **0.8094**, **average 0.8164** (tertinggi), ward **0.8123**. Semuanya tinggi (>0.79), artinya dendrogram cukup setia terhadap struktur jarak asli di semua linkage.

**26. CPCC average paling tinggi, kenapa pakai single?** *(pertanyaan jebakan)*
Selisihnya kecil (0.7945 vs 0.8164, beda ≈0.02). Single dipilih untuk **demonstrasi penurunan manual** karena rumus update-nya paling sederhana (ambil minimum). Hasil pengelompokan inti (rendah/menengah/tinggi) tetap konsisten antar metode, jadi kesimpulan tidak berubah.

**27. Apa itu Silhouette Coefficient?**
Mengukur seberapa cocok titik dengan klasternya: s = (b−a)/max(a,b), di mana a = rata-rata jarak ke anggota klaster sendiri, b = rata-rata jarak ke klaster tetangga terdekat. Rentang −1..1.

**28. Berapa nilai silhouette-nya & artinya?**
k=2 → 0.6264; **k=3 → 0.7367 (tertinggi)**; k=4 → 0.5727. Nilai 0.71–1.0 = "strong structure" (Rousseeuw 1987); k=3 mendekati itu dan jadi pilihan terbaik.

**29. Beda CPCC dan silhouette?**
CPCC menilai kualitas **dendrogram** (kesesuaian dengan jarak asli). Silhouette menilai kualitas **partisi** (pemisahan antar klaster setelah dipotong). Keduanya saling melengkapi.

---

## H. Implementasi / Kode

**30. Library apa yang dipakai?**
`numpy`, `pandas`, `matplotlib`; `scipy.cluster.hierarchy` (`linkage`, `dendrogram`, `fcluster`, `cophenet`) dan `scipy.spatial.distance` (`pdist`, `squareform`); `sklearn` (`AgglomerativeClustering`, `silhouette_score`).

**31. Kenapa ada perhitungan manual padahal SciPy bisa langsung?**
Untuk membuktikan pemahaman algoritma, bukan sekadar memanggil library. Hasil manual lalu **diverifikasi** identik dengan output SciPy.

**32. Fungsi `linkage`, `fcluster`, `cophenet` untuk apa?**
- `linkage` → menghasilkan matriks penggabungan Z.
- `fcluster` → memotong dendrogram menjadi label klaster.
- `cophenet` → menghitung jarak kofenetik & CPCC.

---

## I. Hasil & Interpretasi

**33. Apa makna 3 klaster yang terbentuk?**
- `{A, B, C}` = mahasiswa **nilai rendah** (Tugas & Ujian 1–3).
- `{D, E, F}` = mahasiswa **nilai menengah** (sekitar 5–6).
- `{G, H, I, J}` = mahasiswa **nilai tinggi** (8–10).
Pemisahan jelas sesuai sebaran data.

**34. Apakah hasilnya bisa dipercaya?**
Untuk demonstrasi ya — didukung CPCC ≈ 0.79–0.82 dan silhouette 0.7367 di k=3. Untuk kesimpulan dunia nyata perlu data lebih besar dan representatif.

---

## J. Pertanyaan Jebakan (Ringkas)

- **"Tugasmu masuk kategori DM yang mana?"** → Klasterisasi (clustering), unsupervised.
- **"Kenapa tidak normalisasi?"** → fitur sudah satu skala 0–10.
- **"Kenapa single linkage padahal CPCC average lebih tinggi?"** → beda kecil (~0.02); single dipakai karena update manualnya paling sederhana, partisi inti sama.
- **"Kenapa cuma 10 data / 2 fitur?"** → pilihan didaktik agar bisa dihitung manual & divisualisasi.
- **"Kenapa 3 klaster, bukan 2?"** → gap merge terbesar (2.1913) + silhouette tertinggi di k=3.
- **"Hierarchical vs K-Means mana lebih baik?"** → tidak ada yang mutlak lebih baik; hierarchical unggul karena tak perlu K di awal & menampilkan struktur bertingkat.
