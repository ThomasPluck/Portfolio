#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 30 00:58:08 2018

@author: thomas
"""

import numpy as np
import matplotlib.pyplot as plt
from math import exp

def abs1(x):
    return (x.real**2+x.imag**2)**0.5

def abs2(x):
    return x.real**2+x.imag**2

def LeysKlein(z,t,m):
    
    flag = 0.
    lz = z+1;llz = z-1
    a = t.real;b = t.imag
    
    if z.imag < 0 or z.imag > 2:
        return flag
    
    for i in range(50):
        while z.real > m/2-(b/a)*z.imag:
            z -= m
        while z.real < -m/2-(b/a)*z.imag:
            z += m
            
        if z.imag >= a*0.5+((2.*a-1.95)/4.)*cmp(-z.real+b*0.5,0)*\
        (1.-exp(-(1-(1.95-a)*15.)*abs1(z.real+b*0.5))):
            z = (1j)/(t+(1j*z))
        else:
            z = (t*z-1j)/(-1j*z)
        if abs2(z-llz) < 1e-6:
            break
        if z.imag < 0 or z.imag > a*m/2:
            flag = 1.
            break
        llz=lz;lz=z
    return flag
    

n = 500
t = 2
m = 2

c = np.arange(-2,2,4./n)
c = np.tile(c,(n,1))
c = c+np.flip((c*1j).T,axis=0)

vLK = np.vectorize(LeysKlein)

if __name__ == "__main__":
    c = vLK(c,t,m)
    c = c.reshape((n,n))
    #c = canny(c)
    #for i in range(n):
    #    print(i)
    #    for j in range(n):
    #        z = (-2+(i/(n/4.)))+(-2+(j/(n/4.)))*1j
    #        back = np.array(map(LeysKlein,back))

plt.imshow(c)