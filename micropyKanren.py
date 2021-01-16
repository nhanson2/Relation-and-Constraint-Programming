#!/usr/bin/env python3

import typing
from typing import Callable, Any, List

class Var:
    '''
    Racket like variable
    '''
    def __init__(self, name: Any) -> None:
        self.val = name
    def __repr__(self) -> str:
        return f'#({str(self.val)})'
    def __eq__(self, other: Any) -> bool:
        return isVar(other) and self.val == other.val
    
def isEmptyList(x: Any) -> bool:
    '''
    Checks if an object is a list, and if it is empty
    '''
    return isinstance(x, list) and not len(x)

def isVar(obj: Any) -> bool:
    '''
    Checks if object is an instance of the variable class
    '''
    return isinstance(obj, Var)

def assp(pred: Callable, ls: List) -> Any:
    '''
    Applies a function to the element
    of the list
    '''
    for pair in ls:
        if pred(pair[0]):
            return pair
    return False

def walk(u: Var, s: List) -> Var:
    '''
    Takes a var and a subset and returns a term
    '''
    pr = isVar(u) and assp(lambda v: u==v, s)
    return walk(pr[1], s) if pr else u

# extend substitution
def ext_s(x: Var, v: Var, s: List) -> Any:
    '''
    Extends the substitution s with (x, v)
    '''
    if occurs(x, v, s):
        return False
    else:
        return [(x, v)] + s

def car(x: List) -> List:
    '''
    Returns the first object in a list/pair
    '''
    return x[0]

def cdr(x: List) -> List:
    '''
    Returns the back half of the list/pair
    '''
    return x[1:]

def occurs(x: Var, v: Any, s: List) -> bool:
    
    if not isinstance(v, list):
        return x == v
    if len(v) > 0:
        return occurs(x, walk(car(v), s), s) or occurs(x, walk(cdr(v), s), s)
    else:
        False

def mk_equals(u: Any, v: Any) -> Callable:
    '''
    Equivalent of == in racket, finds equivalent relationships
    '''
    def res(sc: List) -> List:
        s = unify(u, v, sc[0])
        return [(s, sc[1])] if s else []
    return res

def unify(u: Var, v: Var, s: List) -> Any:
    '''
    Takes two terms and a substitution and returns a substitution showing how to make
    u and v equal with respect to all the equation we already have in the substitution.
    Returns False if the two cannot be made equal
    '''
    u = walk(u, s)
    v = walk(v, s)
    if isVar(u) and isVar(v) and u==v:
        return s
    elif isVar(u):
        return ext_s(u, v, s)
    elif isVar(v):
        return ext_s(v, u, s)
    elif isinstance(u, list) and isinstance(v, list):
        # can be faster, no need for recursion here
        s = unify(u[0], v[0], s)
        return s and unify(u[1:], u[1:], s)
    else:
        return u == v and s
    
def call_fresh(func: Callable) -> Callable:
    '''
    Eats a function and returns a function that eats a variable, and increments the variable counter
    '''
    def res(sc: List) -> Callable:
        first, second = sc
        rator = func(Var(second))
        rand = (first, second +1)
        return rator(rand)
    return res

def disj(g1: Callable, g2: Callable) -> Callable:
    '''
    Eats two goals and returns a goal
    '''
    return lambda sc: mplus(g1(sc), g2(sc))

def conj(g1: Callable, g2: Callable) -> Callable:
    '''
    Eats two goals and returns a goal
    '''
    return lambda sc: bind(g1(sc), g2)

def mplus(a: Any, b: Any) -> Any:
    '''
    Helper function to combine goals from disjunction
    '''
    if isEmptyList(a):
        return b
    elif callable(a):
        return lambda : mplus(b, a())
    else:
        return [car(a)] + mplus(cdr(a), b) 
    
def bind(x: Any, g: Any) -> Any:
    '''
    Helper function to combine goals from conjunction
    '''
    if isEmptyList(x):
        return []
    elif callable(x):
        return lambda : bind(x(), g)
    else:
        return mplus(g(car(x)), bind(cdr(x), g))