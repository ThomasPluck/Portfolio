#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 31 02:22:47 2018

@author: Thomas Pluck

@description: Adaptation of Leys Escape-Time Algorithm http://www.josleys.com/article_show.php?id=221
for use in calculating the limit sets of semigroups.z
"""

import numpy as np
import matplotlib.pyplot as plt
import collections

#Fast abs
def abs1(x):
    return (x.real**2+x.imag**2)**0.5

#Fast abs squared
def abs2(x):
    return x.real**2+x.imag**2

#Flatten nested list
def flatten(l):
    for el in l:
        if isinstance(el, collections.Iterable) and not isinstance(el, basestring):
            for sub in flatten(el):
                yield sub
        else:
            yield el

#Main modified Leys Algorithm
def LeysKlein(z,la,mu):
    
    #Set flag, iterables, band boundaries
    flag = 0.
    lz = z+1;llz = z-1
    a = la.real;b = la.imag
    
    #If outside of precalculated band boundaries of limit set - reject
    if z.imag < 0 or z.imag > a:
        return flag
    
    temp = z
    
    
    for i in range(50):
        #Translate complex number to "main limit strip" of band
        while temp.real < -mu/2-(b/a)*z.imag:
            temp += mu
            
        # Apply loxodromic transform
        temp = (1j)/(la+(1j*temp))
        
        #If convergence below eps - abort, raise no flag
        if abs2(temp-llz) < 1e-6:
            break
        
        #If outside band - consider escaped
        if temp.imag < 0 or temp.imag > a:
            flag += 1.
            break
        
        llz=lz;lz=temp

    #Reset iterables
    lz = z+1;llz = z-1
    temp = z
    
    #Retest for backwards limit set    
    for i in range(50):
        
        #Translate to main limit strip of band
        while temp.real > mu/2-(b/a)*z.imag:
            temp -= mu
        
        #Apply inverse loxodrome
        temp = (la*temp-1j)/(-1j*temp)
        
        #If convergence below eps - abort raise no flag
        if abs2(temp-llz) < 1e-6:
            break
        
        #If outside band - consider escaped - add to flag
        if temp.imag < 0 or temp.imag > a:
            flag += 2.
            break
        llz=lz;lz=temp
        
    return flag

#Parameters
n = 300
la = 1.95+0.07j
mu = 2

#Set complex numbers to have escape-time measured
c = np.arange(-2,2,4./n)
c = np.tile(c,(n,1))
c = c+np.flip((c*1j).T,axis=0)

#Vectorize LeysKlein algorithm
vLK = np.vectorize(LeysKlein)

#Apply LeysKlein and display
if __name__ == "__main__":
    c = vLK(c,la,mu)
    c = c.reshape((n,n))
    plt.imshow(c)   