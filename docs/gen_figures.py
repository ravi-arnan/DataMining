"""Generate semua gambar untuk Laporan Agglomerative Clustering (Kelompok 10)."""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

FIG = os.path.join(os.path.dirname(__file__), 'figures')
os.makedirs(FIG, exist_ok=True)

# ---------- Data Tugas 3: 10 mahasiswa ----------
data = pd.DataFrame({
    'Mhs':   ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'],
    'Tugas': [1, 2, 2, 5, 6, 5, 9, 9, 8, 10],
    'Ujian': [2, 2, 3, 5, 5, 6, 9, 8, 9, 10],
})
X = data[['Tugas', 'Ujian']].values
names = data['Mhs'].values
Z = linkage(X, method='single', metric='euclidean')
gaps = np.diff(Z[:, 2])
i_max = int(np.argmax(gaps))
optimal_k = len(X) - (i_max + 1)
cut_height = (Z[i_max, 2] + Z[i_max + 1, 2]) / 2
labels = fcluster(Z, t=optimal_k, criterion='maxclust')

# Gambar 3.1 - Sebaran data
plt.figure(figsize=(7, 5.5))
plt.scatter(X[:, 0], X[:, 1], s=170, c='steelblue', edgecolors='k')
for i, nm in enumerate(names):
    plt.annotate(nm, (X[i, 0] + 0.15, X[i, 1] + 0.15), fontsize=12, fontweight='bold')
plt.xlabel('Nilai Tugas'); plt.ylabel('Nilai Ujian')
plt.title('Sebaran 10 Mahasiswa')
plt.grid(alpha=0.3); plt.xlim(0, 11); plt.ylim(0, 11)
plt.tight_layout(); plt.savefig(f'{FIG}/fig31_scatter.png', dpi=130); plt.close()

# Gambar 3.2 - Dendrogram + garis potong
plt.figure(figsize=(9, 5))
dendrogram(Z, labels=names, leaf_font_size=12, color_threshold=cut_height)
plt.axhline(y=cut_height, color='red', linestyle='--', alpha=0.7,
            label=f'Potong di {cut_height:.2f} -> {optimal_k} klaster')
plt.title('Dendrogram - Agglomerative Single Linkage')
plt.xlabel('Mahasiswa'); plt.ylabel('Jarak Merge (height)')
plt.legend(); plt.grid(axis='y', alpha=0.3)
plt.tight_layout(); plt.savefig(f'{FIG}/fig32_dendrogram.png', dpi=130); plt.close()

# Gambar 3.3 - Hasil 3 klaster
plt.figure(figsize=(7, 5.5))
cmap = plt.get_cmap('tab10')
for k in np.unique(labels):
    pts = X[labels == k]
    plt.scatter(pts[:, 0], pts[:, 1], color=cmap(k - 1), s=190, edgecolors='k', label=f'Klaster {k}')
for i, nm in enumerate(names):
    plt.annotate(nm, (X[i, 0] + 0.15, X[i, 1] + 0.15), fontsize=12, fontweight='bold')
plt.xlabel('Nilai Tugas'); plt.ylabel('Nilai Ujian')
plt.title(f'Hasil Agglomerative Single Linkage ({optimal_k} Klaster)')
plt.legend(); plt.grid(alpha=0.3); plt.xlim(0, 11); plt.ylim(0, 11)
plt.tight_layout(); plt.savefig(f'{FIG}/fig33_hasil.png', dpi=130); plt.close()

# Gambar 3.4 - Perbandingan potong 2/3/4
fig, axs = plt.subplots(1, 3, figsize=(14, 4.3))
for ax, k in zip(axs, [2, 3, 4]):
    lab = fcluster(Z, t=k, criterion='maxclust')
    for c in np.unique(lab):
        pts = X[lab == c]
        ax.scatter(pts[:, 0], pts[:, 1], color=cmap(c - 1), s=130, edgecolors='k', label=f'K{c}')
    for i, nm in enumerate(names):
        ax.annotate(nm, (X[i, 0] + 0.15, X[i, 1] + 0.15), fontsize=10, fontweight='bold')
    ax.set_title(f'Dipotong jadi {k} klaster')
    ax.set_xlabel('Tugas'); ax.set_ylabel('Ujian')
    ax.grid(alpha=0.3); ax.legend(fontsize=8); ax.set_xlim(0, 11); ax.set_ylim(0, 11)
plt.tight_layout(); plt.savefig(f'{FIG}/fig34_potong.png', dpi=130); plt.close()

# Gambar 3.5 - Perbandingan 4 metode linkage
metode = ['single', 'complete', 'average', 'ward']
fig, axs = plt.subplots(2, 2, figsize=(12, 8))
for ax, m in zip(axs.flatten(), metode):
    Zm = linkage(X, method=m, metric='euclidean')
    dendrogram(Zm, labels=names, ax=ax, leaf_font_size=11)
    ax.set_title(f"Linkage = '{m}'"); ax.set_ylabel('Jarak Merge')
    ax.grid(axis='y', alpha=0.3)
plt.tight_layout(); plt.savefig(f'{FIG}/fig35_linkage.png', dpi=120); plt.close()

# Gambar 3.6 - K-Means Elbow (data pelanggan Tugas 2, untuk pembanding)
cust = pd.DataFrame({
    'Age':    [41, 47, 33, 29, 47, 40, 38, 42, 26, 47],
    'Income': [19, 100, 57, 19, 253, 81, 56, 64, 18, 115],
})
Xc = StandardScaler().fit_transform(cust.values)
sse = []
Ks = list(range(1, 8))
for k in Ks:
    sse.append(KMeans(n_clusters=k, n_init=10, random_state=42).fit(Xc).inertia_)
plt.figure(figsize=(8, 5))
plt.plot(Ks, sse, 'o-', linewidth=2, markersize=10, color='darkorange')
plt.xlabel('Jumlah Klaster (K)'); plt.ylabel('SSE / Inertia')
plt.title('Elbow Method - K-Means (Pembanding, Tugas 2)')
plt.grid(alpha=0.3)
for k, s in zip(Ks, sse):
    plt.annotate(f'{s:.2f}', (k, s), textcoords='offset points', xytext=(0, 10), ha='center')
plt.tight_layout(); plt.savefig(f'{FIG}/fig36_kmeans_elbow.png', dpi=130); plt.close()

# Simpan nilai-nilai kunci untuk dipakai narasi laporan
summary = {
    'heights': np.round(Z[:, 2], 3).tolist(),
    'gaps': np.round(gaps, 3).tolist(),
    'gap_terbesar': round(float(gaps[i_max]), 3),
    'cut_height': round(float(cut_height), 3),
    'optimal_k': int(optimal_k),
    'labels': labels.tolist(),
}
print(summary)
print('Figures saved to', FIG)
