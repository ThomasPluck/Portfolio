#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 13:42:42 2018

@author: thomas
"""

import numpy as np

from repetend import no_repet, look, check

import matplotlib.pyplot as plt


def arr2limit(arr,sink=True):
    
    if arr.dtype != 'complex_':
        arr = arr.astype('complex128')
    
    a = arr[0,0]
    b = arr[0,1]
    c = arr[1,0]
    d = arr[1,1]
    
    if c == 0:
        fps = (b/(d-a),np.inf)
                
    elif d-a == 0:
        fps = (np.inf,np.inf)
        
    else:
        fps = (((a-d)+((d-a)**2+4*b*c)**0.5)/(2*c),
               ((a-d)-((d-a)**2+4*b*c)**0.5)/(2*c))

    k = (a/c-fps[0])/(a/c-fps[1])
    
    if sink:
        if k > 1:
            return fps[1]
        else:
            return fps[0]
    else:
        if k > 1:
            return fps[0]
        else:
            return fps[1]

t = 1/2 #(2**0.3)*np.exp(np.pi*(1./3)*1j)
        
f = (np.array([[t,1],[1,0]]),'f')
g = (np.array([[1,2],[0,1]]),'g')
F = (np.linalg.inv(f[0]),'F')
G = (np.linalg.inv(g[0]),'G')

print(arr2limit(f[0]),abs(arr2limit(f[0])))
    
def find_limit_set(f,g,depth):
    arr_list = [f,g]
    temp = []
    
    for i in range(depth):
        keys = [a[1] for a in arr_list]
        for a in arr_list:
            for b in arr_list:
                if not no_repet(a[1]+b[1]) and not look(keys,a[1]+b[1]):
                    temp.append((np.matmul(a[0],b[0]),a[1]+b[1]))
        
        #code to remove *all* cyclic permutations. Not necessary since
        #commutative composition is rare
        
        #temp_keys = [te[1] for te in temp]
        #temp_id = [temp_keys.index(c) for c in check(temp_keys)]
        
        for i in temp:
            arr_list.append(i)
            
        temp = []
        #temp_keys = []
        #temp_id = []
    
    limits = []
    
    for a in arr_list:
        limits.append(arr2limit(a[0]))
        
    #test = arr_list[[np.allclose(a[0],np.array([[1,0],[0,1]])) for a in arr_list].index(True)]
        
    return np.array(limits)

if __name__ == "__main__":
    
    fig = plt.figure()
    plt.axis('equal')
    
    limits = find_limit_set(f,g,4)
    plt.scatter(limits.real,
                limits.imag,
                color='red',
                marker='o',
                lw=0,
                s=72./fig.dpi)
    
    limits = find_limit_set(F,G,4)
    plt.scatter(limits.real,
                limits.imag,
                color='blue',
                marker='o',
                lw=0,
                s=72./fig.dpi)