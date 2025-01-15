import math
def in2m(inch):
    '''
    Converts inches to meteres
    '''
    return inch*0.0254

def m2in(m):
    '''
    Converts meters to inches
    '''
    return m/0.0254

def pa2psi(pa):
    '''
    Converts Pascals to PSI
    '''
    return pa/6895

def psi2pa(psi):
    '''
    Converts PSI to Pascals
    '''
    return psi*6895

def ft2m(ft):
    '''
    Converts feet to meters
    '''
    return ft*0.3048

def m2ft(m):
    '''
    Converts meters to feet
    '''
    return m/0.3048

def rad2deg(rad):
    '''
    Converts radians to degrees
    '''
    return rad*180/math.pi