import numpy as np

from osgeo import gdal


def _linspace(n, x, spacing):
    L = np.linalg.norm(x)
    dx = spacing / L
    sp = np.zeros((n, 2))
    for i in range(n):
        t = i * dx
        sp[i, :] = (1.0 - t) * x[0, :] + t * x[1, :]
    return sp


def extract(n, spacing, name, x):
    ds = gdal.Open(name, gdal.GA_ReadOnly)
    gt = ds.GetGeoTransform()
    b = ds.GetBand()
    z = []
    for xy in _linspace(n, x, spacing):
        px = int((xy[0] - gt[0]) / gt[1])
        py = int((xy[1] - gt[3]) / gt[5])
        z.append(b.ReadAsArray(px, py, 1, 1)[0])
    return np.array(z)
