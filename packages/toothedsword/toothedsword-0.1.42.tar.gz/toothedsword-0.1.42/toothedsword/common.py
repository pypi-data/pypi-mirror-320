
import sys
import os
import re
import glob
import json
import numpy as np
import math


def llr2xyz(lon, lat, R=6371):
    pi = 3.141592654
    r = R*np.cos(lat/180*math.pi)
    z = R*np.sin(lat/180*math.pi)
    x = r*np.cos(lon/180*math.pi)
    y = r*np.sin(lon/180*math.pi)
    return x,y,z


def Rotate(a, theta, x, y, z):
    '''对坐标进行旋转操作'''

    theta = theta/180*math.pi

    if a == 1:
        rotate = np.array([[1, 0, 0], [0, np.cos(theta), -np.sin(theta)], [0, np.sin(theta), np.cos(theta)]])
    elif a == 2:
        rotate = np.array([[np.cos(theta), 0, np.sin(theta)], [0, 1, 0], [-np.sin(theta), 0, np.cos(theta)]])
    elif a == 3:
        rotate = np.array([[np.cos(theta), -np.sin(theta), 0], [np.sin(theta), np.cos(theta), 0], [0, 0, 1]])

    temp = np.dot(rotate,np.vstack((x.flatten(), y.flatten(), z.flatten())))
    xn = temp[0,:].reshape(x.shape)
    yn = temp[1,:].reshape(x.shape)
    zn = temp[2,:].reshape(x.shape)
    return xn, yn, zn


def local_xyz2lonlat(xj_1, yj_1, zj_1, lon0, lat0, alt0=0):

    xj = xj_1.flatten()
    yj = yj_1.flatten()
    zj = zj_1.flatten()

    x0, y0, z0 = llr2xyz(0, 0, R=6371)
    x = zj+x0+alt0
    y = xj
    z = yj

    x, y, z = Rotate(2, 0-lat0, x, y, z)
    x, y, z = Rotate(3, lon0, x, y, z)
    alt = np.sqrt(x**2+y**2+z**2) - 6371

    lon = np.arctan2(y,x)
    lat = np.arctan2(z,np.sqrt(x**2 + y**2))
    lon = lon / np.pi * 180
    lat = lat / np.pi * 180
    return lon.reshape(xj_1.shape),\
            lat.reshape(xj_1.shape),\
            alt.reshape(xj_1.shape),\


def get_range_id(lon, lat, z, i, j, k, xlim, ylim, zlim):
    id =\
         (lon.flatten()[i] >= xlim[0]) &\
         (lon.flatten()[j] >= xlim[0]) &\
         (lon.flatten()[k] >= xlim[0]) &\
         (lon.flatten()[i] <= xlim[1]) &\
         (lon.flatten()[j] <= xlim[1]) &\
         (lon.flatten()[k] <= xlim[1]) &\
         (lat.flatten()[i] >= ylim[0]) &\
         (lat.flatten()[j] >= ylim[0]) &\
         (lat.flatten()[k] >= ylim[0]) &\
         (lat.flatten()[i] <= ylim[1]) &\
         (lat.flatten()[j] <= ylim[1]) &\
         (lat.flatten()[k] <= ylim[1]) &\
         (z.flatten()[i] >= zlim[0]) &\
         (z.flatten()[j] >= zlim[0]) &\
         (z.flatten()[k] >= zlim[0]) &\
         (z.flatten()[i] <= zlim[1]) &\
         (z.flatten()[j] <= zlim[1]) &\
         (z.flatten()[k] <= zlim[1])
    return id


def triangle_area_3d(x1, x2, x3, y1, y2, y3, z1, z2, z3):
    
    # 计算每个三角形的顶点坐标
    A = np.column_stack((x1, y1, z1))
    B = np.column_stack((x2, y2, z2))
    C = np.column_stack((x3, y3, z3))

    # 计算向量 AB 和 AC
    AB = B - A
    AC = C - A

    # 计算叉积
    cross_product = np.cross(AB, AC)

    # 计算每个三角形的面积
    areas = 0.5 * np.linalg.norm(cross_product, axis=1)
    return areas


def area_by_xyz(x1, y1, x2, y2, x3, y3):
    return 0.5 * np.abs(x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))

