"""Render rumus matematis sebagai PNG (matplotlib mathtext) + simpan lebar natural per rumus."""
import os
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image, ImageChops


def autocrop(path, pad_px=20):
    """Crop pixel transparan/putih di pinggir PNG (matplotlib bbox tight kadang tidak crop)."""
    im = Image.open(path).convert('RGBA')
    bg = Image.new('RGBA', im.size, (0, 0, 0, 0))
    diff = ImageChops.difference(im, bg)
    bbox = diff.getbbox()
    if bbox:
        l, t, r, b = bbox
        l = max(0, l - pad_px); t = max(0, t - pad_px)
        r = min(im.size[0], r + pad_px); b = min(im.size[1], b + pad_px)
        im.crop((l, t, r, b)).save(path)
    return Image.open(path).size

FIG = os.path.join(os.path.dirname(__file__), 'figures')
os.makedirs(FIG, exist_ok=True)

FONTSIZE = 12
DPI = 220
PAGE_TEXT_WIDTH_CM = 13.5  # batas max embed (page 21cm - L4 - R3 - sedikit margin)


def render(name, expr, fontsize=FONTSIZE, dpi=DPI):
    fig = plt.figure(figsize=(12, 1.2))
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis('off')
    ax.text(0.5, 0.5, expr, ha='center', va='center', fontsize=fontsize)
    path = os.path.join(FIG, f'eq_{name}.png')
    fig.savefig(path, dpi=dpi, transparent=True)
    plt.close(fig)
    px = autocrop(path)[0]
    cm = px / dpi * 2.54
    return min(cm, PAGE_TEXT_WIDTH_CM)


EQ = {
    'apr_support':    r'$\mathrm{Support}(X) = \dfrac{\mathrm{freq}(X)}{N}$',
    'apr_confidence': r'$\mathrm{Confidence}(A \rightarrow B) = \dfrac{\mathrm{Support}(A \cup B)}{\mathrm{Support}(A)}$',
    'apr_final':      r'$\mathrm{Final}(A \rightarrow B) = \mathrm{Support}(A \rightarrow B) \times \mathrm{Confidence}(A \rightarrow B)$',
    'km_euclidean':   r'$d(x_i,\ c_k) = \sqrt{\sum_{j=1}^{m}(x_{ij} - c_{kj})^2}$',
    'km_assign':      r'$C(x_i) = \arg\min_{k \in \{1,\dots,K\}}\ d(x_i,\ c_k)$',
    'km_centroid':    r'$c_k = \dfrac{1}{|C_k|}\sum_{x \in C_k} x$',
    'km_sse':         r'$\mathrm{SSE} = \sum_{k=1}^{K}\sum_{x \in C_k}\|x - c_k\|^{2}$',
    'ag_euclidean':   r'$d(p,\ q) = \sqrt{\sum_{i=1}^{m}(p_i - q_i)^2}$',
    'ag_matriks':     r'$D \in \mathbb{R}^{n \times n},\quad D_{ij} = d(x_i,\ x_j),\quad D_{ii} = 0$',
    'ag_single':      r'$d_{\mathrm{single}}(C_i,\ C_j) = \min_{x \in C_i,\ y \in C_j}\ d(x,\ y)$',
    'ag_complete':    r'$d_{\mathrm{complete}}(C_i,\ C_j) = \max_{x \in C_i,\ y \in C_j}\ d(x,\ y)$',
    'ag_average':     r'$d_{\mathrm{average}}(C_i,\ C_j) = \dfrac{1}{|C_i|\,|C_j|}\sum_{x \in C_i}\sum_{y \in C_j} d(x,\ y)$',
    'ag_argmin':      r'$(i^{*},\ j^{*}) = \arg\min_{i \neq j}\ D_{ij}$',
    'ag_update':      r'$d(C_i \cup C_j,\ C_k) = \min\,\left(d(C_i,\ C_k),\ d(C_j,\ C_k)\right)$',
    'ag_gap':         r'$k^{*} = n - \arg\max_{i}\,\left(h_{i+1} - h_i\right) - 1$',
}

widths = {}
for name, expr in EQ.items():
    widths[name] = round(render(name, expr), 2)

with open(os.path.join(FIG, 'eq_widths.json'), 'w') as f:
    json.dump(widths, f, indent=2)

print(f'Saved {len(EQ)} equations + widths to {FIG}')
print('Sample widths (cm):', {k: widths[k] for k in list(widths)[:4]})
