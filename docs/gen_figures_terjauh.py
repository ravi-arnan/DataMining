"""Generate figure for the 'titik terjauh' K-Means analysis (laporan v2).
Output: figures/km_terjauh.png  (centroid awal DALAM vs LUAR layer, side by side)
Run:  python gen_figures_terjauh.py
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, 'figures')

Age = [41, 47, 33, 29, 47, 40, 38, 42, 26, 47]
Income = [19, 100, 57, 19, 253, 81, 56, 64, 18, 115]
X = np.array(list(zip(Age, Income)), dtype=float)
label = [f'P{i+1}' for i in range(len(X))]


def euclid(a, b):
    return np.sqrt(np.sum((np.array(a) - np.array(b)) ** 2))


def kmeans_manual(X, init, max_iter=20):
    c = np.array(init, dtype=float)
    for _ in range(max_iter):
        lab = np.array([int(np.argmin([euclid(x, ci) for ci in c])) for x in X])
        nc = np.array([X[lab == k].mean(axis=0) if (lab == k).any() else c[k]
                       for k in range(len(c))])
        if np.allclose(nc, c):
            break
        c = nc
    return c, lab


mean = X.mean(axis=0)
jd = np.sqrt(((X - mean) ** 2).sum(axis=1))
i_far, i_cen = int(jd.argmax()), int(jd.argmin())
C2 = X[1]  # P2, jangkar tetap
initD, initL = [X[i_cen], C2], [X[i_far], C2]
cD, lD = kmeans_manual(X, initD)
cL, lL = kmeans_manual(X, initL)

mask = np.arange(len(X)) != i_far
lo, hi = X[mask].min(axis=0), X[mask].max(axis=0)
pad = (hi - lo) * 0.12
lo, hi = lo - pad, hi + pad

fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
warna = ['tomato', 'steelblue']
for ax, (judul, lab, cen, init) in zip(axes, [
        ('(a) DALAM layer - awal C1=P6 (sentral)', lD, cD, initD),
        ('(b) LUAR layer - awal C1=P5 (terjauh)', lL, cL, initL)]):
    ax.add_patch(plt.Rectangle((lo[0], lo[1]), hi[0]-lo[0], hi[1]-lo[1],
                 fill=False, ls='--', ec='gray', lw=1.5))
    ax.text(lo[0], hi[1], ' layer', va='bottom', ha='left', fontsize=8, color='gray')
    for k in range(2):
        pts = X[lab == k]
        ax.scatter(pts[:, 0], pts[:, 1], c=warna[k], s=90, edgecolors='k',
                   linewidths=0.6, label=f'Klaster {k+1}')
    ax.scatter([c[0] for c in init], [c[1] for c in init], marker='*', s=240,
               c='gold', edgecolors='k', label='Centroid awal', zorder=5)
    ax.scatter(cen[:, 0], cen[:, 1], marker='X', s=170, c='black',
               label='Centroid akhir', zorder=5)
    for i, x in enumerate(X):
        ax.annotate(label[i], (x[0], x[1]), textcoords='offset points',
                    xytext=(5, 3), fontsize=7.5)
    ax.set_xlabel('Age'); ax.set_ylabel('Income'); ax.set_title(judul, fontsize=9)
    ax.legend(fontsize=7, loc='upper left'); ax.grid(alpha=0.3)
plt.tight_layout()
out = os.path.join(FIG, 'km_terjauh.png')
plt.savefig(out, dpi=150, bbox_inches='tight')
print('saved:', out, '| DALAM', np.bincount(lD).tolist(), '| LUAR', np.bincount(lL).tolist())
