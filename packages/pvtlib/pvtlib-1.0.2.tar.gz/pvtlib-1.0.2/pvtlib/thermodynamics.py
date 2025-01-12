"""MIT License

Copyright (c) 2025 Christian Hågenvik

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

def energy_rate_balance(h_in, h_out, massflow, vel_in, vel_out):
    '''
    Energy rate balance over control volume

    Parameters
    ----------
    h_in : float
        Enthalpy in [kJ/kg]
    h_out : float
        Enthalpy out [kJ/kg]
    massflow : float
        Mass flow [kg/s]
    vel_in : float
        Velocity in [m/s]
    vel_out : float
        Velocity out [m/s]

    Returns
    -------
    energy_rate_change : float
        Energy rate change [kW]

    '''
    
    energy_rate_in = massflow*(h_in*1000 + ((vel_in**2)/2))/1000
    energy_rate_out = massflow*(h_out*1000 + ((vel_out**2)/2))/1000
        
    energy_rate_change = energy_rate_in - energy_rate_out
    
    return energy_rate_change
                            

def energy_rate_difference(energy_rate_A, energy_rate_B):
    '''
    Difference in energy rate between A and B, absolute values
    
    Parameters
    ----------
    energy_rate_A : float
        Energy rate A [kW]
    energy_rate_B : float
        Energy rate B [kW]

    Returns
    -------
    energy_rate_difference : float
        Difference between energy rate A and B [kW]

    '''
    
    energy_rate_difference = abs(energy_rate_A) - abs(energy_rate_B)
    
    return energy_rate_difference

def energy_rate_diffperc(energy_rate_A, energy_rate_B):
    '''
    Diff percent in energy rate between A and B, absolute values

    Parameters
    ----------
    energy_rate_A : float
        Energy rate A [kW]
    energy_rate_B : float
        Energy rate B [kW]

    Returns
    -------
    energy_rate_diffperc : float
        Difference percentage between energy rate A and B [%]

    '''
    
    energy_rate_diffperc = 100*(abs(energy_rate_A) - abs(energy_rate_B))/((abs(energy_rate_A) + abs(energy_rate_B))/2)
    
    return energy_rate_diffperc