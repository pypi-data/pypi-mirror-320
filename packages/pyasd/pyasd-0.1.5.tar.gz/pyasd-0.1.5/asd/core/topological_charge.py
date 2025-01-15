#!/usr/bin/env python

#=========================================================
#
# This script is part of the pyasd package
# Copyright @ Shunhong Zhang 2022 - 2025
#
# Redistribution and use in source and binary forms, 
# with or without modification, are permitted provided 
# that the MIT license is consented and obeyed
# A copy of the license is available in the home directory
#
#=========================================================



#=============================================
#
# calculation of topological charge
# of classic spin systems
# Shunhong Zhang
# Last modified: Mar 11 2022
#
#=============================================

import numpy as np
import pickle
from asd.core.spin_configurations import check_sp_lat_norm


def verbose_collinear_error(n1,n2,n3):
    print ('\nErr from calc_solid_angle: ')
    print ('two spins in a triangle are anti-parallel')
    print ('This might happen if you are calculating an antiferromagnet')
    print ('Or a Skyrmion/Bimeron with very small size')
    print ('In these cases this function cannot be applied, Sorry!\n')
    print ('Try using solid_angle_method = 2')
    print (('n1 = ['+'{:10.5f} '*len(n1)+']').format(*tuple(n1)))
    print (('n2 = ['+'{:10.5f} '*len(n2)+']').format(*tuple(n2)))
    print (('n3 = ['+'{:10.5f} '*len(n3)+']').format(*tuple(n3)))

 
# n1, n2, and n3 are 3x1 vectors
# see Phys. Rev. B 99, 224414 (2019)
# for the defination of solid angle
def calc_solid_angle_1(n1,n2,n3):
    n1 /= np.linalg.norm(n1)
    n2 /= np.linalg.norm(n2)
    n3 /= np.linalg.norm(n3)
    dps = np.array([np.dot(n1,n2),np.dot(n2,n3),np.dot(n3,n1)])
    if np.min(abs(1+dps))<1e-5: 
        verbose_collinear_error(n1,n2,n3)
        exit()
    cc  = (1+np.sum(dps))/np.sqrt(2*np.prod(1+dps))
    if 1<abs(cc)<1+1e-4: cc = np.sign(cc)   # tolerance to "-1" and "1"
    ang = 2*np.arccos(cc)
    y = np.linalg.det([n1,n2,n3])
    ang = np.sign(y)*abs(ang)
    return ang


# Using the solid angle formula by Oosterom and Strackee 
# https://en.wikipedia.org/wiki/Solid_angle#Tetrahedron
def calc_solid_angle_2(n1,n2,n3):
    n1 /= np.linalg.norm(n1)
    n2 /= np.linalg.norm(n2)
    n3 /= np.linalg.norm(n3)
    dps = np.array([np.dot(n1,n2),np.dot(n2,n3),np.dot(n3,n1)])
    y = np.linalg.det([n1,n2,n3])
    x  = 1+np.sum(dps)
    ang = 2*np.angle(x+1.j*y)
    return ang


# sites_cart are site positions in Cartesian coordinates
def get_tri_simplices(sites_cart):
    from scipy.spatial import Delaunay
    all_sites=sites_cart.reshape(-1,sites_cart.shape[-1])
    assert len(all_sites)>=3, 'calc_topo_chg: at least three sites needed!'
    tri_simplices=Delaunay(all_sites).simplices
    return tri_simplices


def calc_topo_chg(spins,sites=None,tri_simplices=None,pbc=[0,0,0],spatial_resolved=False,solid_angle_method=2):
    check_sp_lat_norm(spins)
    all_spins=spins.reshape(-1,3)
    if tri_simplices is None and sites is not None: 
        n1 = np.prod(spins.shape[:-1])
        n2 = np.prod(sites.shape[:-1])
        assert n1==n2,'No. of spins {} and sites {} inconsistent!'.format(n1,n2)
        tri_simplices = get_tri_simplices(sites[...,:2])
    assert solid_angle_method in [1,2], 'valid value for solid_angle_method: 1 or 2'
    if solid_angle_method==1:   Q_distri = np.array([calc_solid_angle_1(*tuple(all_spins[idx])) for idx in tri_simplices])
    if solid_angle_method==2:   Q_distri = np.array([calc_solid_angle_2(*tuple(all_spins[idx])) for idx in tri_simplices])
    Q = np.sum(Q_distri)/4/np.pi
    if spatial_resolved: return tri_simplices,Q_distri,Q
    else: return Q
