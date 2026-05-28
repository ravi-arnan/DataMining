"""Generate semua gambar untuk Laporan UTS Data Mining Kelompok 10."""
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

# ============================================================ K-MEANS (Tugas 2)
np.random.seed(42)
cust = pd.DataFrame({
    'CustID': list(range(1, 11)),
    'Age':    [41, 47, 33, 29, 47, 40, 38, 42, 26, 47],
    'Income': [19, 100, 57, 19, 253, 81, 56, 64, 18, 115],
})
Xc = cust[['Age', 'Income']].values

# Gambar K1 - Sebaran pelanggan
plt.figure(figsize=(7, 5))
plt.scatter(Xc[:, 0], Xc[:, 1], s=130, c='steelblue', edgecolors='k')
for i, row in cust.iterrows():
    plt.annotate(f"P{row['CustID']}", (row['Age'] + 0.4, row['Income'] + 2))
plt.xlabel('Age (tahun)'); plt.ylabel('Income')
plt.title('Sebaran 10 Pelanggan')
plt.grid(alpha=0.3)
plt.tight_layout(); plt.savefig(f'{FIG}/km_scatter.png', dpi=130); plt.close()

# K-Means manual K=2 (centroid awal P1, P2)
def euclid(a, b):
    return np.sqrt(np.sum((np.array(a) - np.array(b)) ** 2))

def kmeans_manual(X, init, max_iter=20):
    cent = np.array(init, dtype=float)
    hist = []
    for it in range(max_iter):
        labels = np.array([int(np.argmin([euclid(x, c) for c in cent])) for x in X])
        hist.append({'iter': it + 1, 'cent': cent.copy(), 'labels': labels.copy()})
        new_cent = np.array([X[labels == k].mean(axis=0) if (labels == k).any() else cent[k]
                             for k in range(len(cent))])
        if np.allclose(new_cent, cent):
            break
        cent = new_cent
    return cent, labels, hist

cent2, lab2, hist2 = kmeans_manual(Xc, [Xc[0], Xc[1]])

# Gambar K2 - Hasil K-Means K=2
plt.figure(figsize=(7, 5))
warna = ['tomato', 'steelblue']
for k in range(2):
    pts = Xc[lab2 == k]
    plt.scatter(pts[:, 0], pts[:, 1], c=warna[k], s=130, edgecolors='k', label=f'Klaster {k+1}')
plt.scatter(cent2[:, 0], cent2[:, 1], marker='X', s=240, c='black', label='Centroid')
plt.xlabel('Age'); plt.ylabel('Income')
plt.title('Hasil K-Means Manual (K=2)')
plt.legend(); plt.grid(alpha=0.3)
plt.tight_layout(); plt.savefig(f'{FIG}/km_k2.png', dpi=130); plt.close()

# Elbow + clusters K=3..6 (standarisasi)
scaler = StandardScaler()
Xcs = scaler.fit_transform(Xc)
hasil = {}
for k in [2, 3, 4, 5, 6]:
    km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(Xcs)
    centers_asli = scaler.inverse_transform(km.cluster_centers_)
    sse_asli = sum(euclid(Xc[i], centers_asli[km.labels_[i]]) ** 2 for i in range(len(Xc)))
    hasil[k] = {'labels': km.labels_, 'centers': centers_asli, 'sse': sse_asli, 'sse_s': km.inertia_}

# Gambar K3 - Elbow
K_range = list(range(1, 8))
sse_list = [KMeans(n_clusters=k, n_init=10, random_state=42).fit(Xcs).inertia_ for k in K_range]
plt.figure(figsize=(8, 5))
plt.plot(K_range, sse_list, 'o-', linewidth=2, markersize=10, color='darkorange')
plt.xlabel('Jumlah Klaster (K)'); plt.ylabel('SSE / Inertia (data ter-standarisasi)')
plt.title('Elbow Method')
plt.grid(alpha=0.3)
for k, s in zip(K_range, sse_list):
    plt.annotate(f'{s:.2f}', (k, s), textcoords='offset points', xytext=(0, 10), ha='center')
plt.tight_layout(); plt.savefig(f'{FIG}/km_elbow.png', dpi=130); plt.close()

# Gambar K4 - K-Means K=3..6 (2x2 grid)
fig, axs = plt.subplots(2, 2, figsize=(12, 9))
for ax, k in zip(axs.flatten(), [3, 4, 5, 6]):
    labels = hasil[k]['labels']; centers = hasil[k]['centers']
    cmap = plt.get_cmap('tab10')
    for c in range(k):
        pts = Xc[labels == c]
        ax.scatter(pts[:, 0], pts[:, 1], color=cmap(c), s=110, edgecolors='k', label=f'C{c+1}')
    ax.scatter(centers[:, 0], centers[:, 1], marker='X', c='black', s=200)
    ax.set_title(f'K = {k}    SSE = {hasil[k]["sse"]:.2f}')
    ax.set_xlabel('Age'); ax.set_ylabel('Income')
    ax.grid(alpha=0.3); ax.legend(fontsize=8)
plt.tight_layout(); plt.savefig(f'{FIG}/km_k36.png', dpi=120); plt.close()

# ============================================================ AGGLOMERATIVE (Tugas 3)
data = pd.DataFrame({
    'Mhs':   ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'],
    'Tugas': [1, 2, 2, 5, 6, 5, 9, 9, 8, 10],
    'Ujian': [2, 2, 3, 5, 5, 6, 9, 8, 9, 10],
})
X = data[['Tugas', 'Ujian']].values
names = data['Mhs'].values
Z = linkage(X, method='single', metric='euclidean')
gaps = np.diff(Z[:, 2]); i_max = int(np.argmax(gaps))
optimal_k = len(X) - (i_max + 1)
cut_height = (Z[i_max, 2] + Z[i_max + 1, 2]) / 2
labels = fcluster(Z, t=optimal_k, criterion='maxclust')

# Gambar A1 - Sebaran mahasiswa
plt.figure(figsize=(7, 5.5))
plt.scatter(X[:, 0], X[:, 1], s=170, c='steelblue', edgecolors='k')
for i, nm in enumerate(names):
    plt.annotate(nm, (X[i, 0] + 0.15, X[i, 1] + 0.15), fontsize=12, fontweight='bold')
plt.xlabel('Nilai Tugas'); plt.ylabel('Nilai Ujian')
plt.title('Sebaran 10 Mahasiswa')
plt.grid(alpha=0.3); plt.xlim(0, 11); plt.ylim(0, 11)
plt.tight_layout(); plt.savefig(f'{FIG}/ag_scatter.png', dpi=130); plt.close()

# Gambar A2 - Dendrogram
plt.figure(figsize=(9, 5))
dendrogram(Z, labels=names, leaf_font_size=12, color_threshold=cut_height)
plt.axhline(y=cut_height, color='red', linestyle='--', alpha=0.7,
            label=f'Potong di {cut_height:.2f} -> {optimal_k} klaster')
plt.title('Dendrogram Agglomerative Single Linkage')
plt.xlabel('Mahasiswa'); plt.ylabel('Jarak Merge (height)')
plt.legend(); plt.grid(axis='y', alpha=0.3)
plt.tight_layout(); plt.savefig(f'{FIG}/ag_dendrogram.png', dpi=130); plt.close()

# Gambar A3 - Hasil 3 klaster
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
plt.tight_layout(); plt.savefig(f'{FIG}/ag_hasil.png', dpi=130); plt.close()

# Gambar A4 - Potong 2/3/4
fig, axs = plt.subplots(1, 3, figsize=(14, 4.5))
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
plt.tight_layout(); plt.savefig(f'{FIG}/ag_potong.png', dpi=120); plt.close()

# Gambar A5 - Perbandingan 4 linkage
metode = ['single', 'complete', 'average', 'ward']
fig, axs = plt.subplots(2, 2, figsize=(12, 8))
for ax, m in zip(axs.flatten(), metode):
    Zm = linkage(X, method=m, metric='euclidean')
    dendrogram(Zm, labels=names, ax=ax, leaf_font_size=11)
    ax.set_title(f"Linkage = '{m}'"); ax.set_ylabel('Jarak Merge')
    ax.grid(axis='y', alpha=0.3)
plt.tight_layout(); plt.savefig(f'{FIG}/ag_linkage.png', dpi=120); plt.close()

print('Saved figures to', FIG)
print('K-Means K=2 final centroid:', np.round(cent2, 2).tolist())
print('Agglomerative optimal_k:', optimal_k, 'cut_height:', round(cut_height, 3))
