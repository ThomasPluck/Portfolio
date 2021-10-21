#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  4 20:53:48 2018

@author: Thomas Pluck
"""

#Identify string cyclic permutation of element in s by p
#look(['abc'],'cab') returns True
#look(['abc'],'acb') returns False

def look(s, p):
    for i in s:
        if len(i) != len(p):
            continue
        np = p
        for k in i:
            if k in np:
                ind = np.index(k)
                np = np[ind:] + np[:ind]
                if np in s:
                    return True
    return False
            
#Returns list of strings with no cyclic permutations  
#check(['abc','cab','bca','acb','cba','bac'])
#returns ['abc','acb']
                
def check(l):
    sets = []
    for i in l:
        if len(sets) == 0:
            sets.append(i)
            continue
        elif look(sets, i) == True:
            pass
        else:
            sets.append(i)
            pass
    return sets

#Identify cyclic repetition in strings
#ie. "abcabc" returns True
#    "cabcab" returns True
#    "abc"    returns False
#    "ababa"  returns False

def no_repet(s):
    prefix=[s[:i+1] for i in range(len(s)/2)]
    for p in prefix:
        for i in range(len(s)/len(p)):
            cand = "".join([p for i in range(len(s)/len(p))])
            if s == cand:
                return True
    return False