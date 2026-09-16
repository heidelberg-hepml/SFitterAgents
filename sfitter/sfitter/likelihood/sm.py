import numpy as np

mh = 125
gf = 1.16637e-5
vbfwcontr = 0.738831#14471844461912
vbfzcontr = 1 - vbfwcontr

# Get value from indextable
sm_values = {
    "csgf": 34016.6,
    "csvbf": 4320.54827,
    "cswh": 1604.63665,
    "cszh": 859.749204,
    "cstth": 401.220588,
    "csTEVgf": 949.3,
    "csTEVvbf": 65.328,
    "csTEVwh": 129.50,
    "csTEVzh": 78.5,
    "csTEVtth": 0.0,
    "cs7gf": 15310,
    "cs7vbf": 1211,
    "cs7wh": 572.9,
    "cs7zh": 315.8,
    "cs7tth": 86.34,
    "cs8gf": 19520.0,
    "cs8vbf": 1559.0,
    "cs8wh": 696.6,
    "cs8zh": 394.3,
    "cs8tth": 130.2,
    "cs13gf": 48580,
    "cs13vbf": 3782,
    "cs13wh": 1373,
    "cs13zh": 883.9,
    "cs13tth": 507.1,
    "cs13bbh": 552.9,
    "cs14gf": 49470,
    "cs14vbf": 4233,
    "cs14wh": 1522,
    "cs14zh": 969.0,
    "cs14tth": 611.3,
    "cs14bbh": 552.9,
    "cs27gf": 140310.5161716833,
    "cs27vbf": 12347.09907111596,
    "cs27wh": 3594.562875215168,
    "cs27zh": 2341.994481533261,
    "cs27tth": 3182.348140702267,
    "cssiggf": 1.0,
    "cssigvbf": 1.0,
    "cssigwh": 1.0,
    "cssigzh": 1.0,
    "cssigtth": 1.0,
}


# Get SM values from PDG
brsmg = 0.0763205
brsmw = 0.205089
brsmz = 0.0254848
brsmb = 0.596821
brsmc = 0.0289649
brsms = 0.000224384
brsmtau = 0.0630085
brsmmu = 0.000223027
brsmga = 0.00233182
brsmzga = 0.00153211
gammasmh = 0.00410648

"""
# Standard model values computed as prediction from SFitter
brsmg = 0.07632050311337391
brsmw = 0.2050885526014036
brsmz = 0.02548478820901025
brsmb = 0.596821402211041
brsmc = 0.0289649
brsms = 0.000224384
brsmtau = 0.06300854900275579
brsmmu = 0.0002230269837949041
brsmga = 0.00233181693141019
brsmzga = 0.00153210664402925
gammasmh = 0.004106483142941708
"""
# Get bri, bru from literature? are they always 0?
bri = 0
bru = 0

# SM values currently used in SFitter
xmt = 171.4
xmw = 80.35797
xmz = 91.1876
xmtau = 1.7767
xmb = 4.2
xmmu = 0.10566

g = np.sqrt(gf / (np.sqrt(2.0)) * 8.0 * xmw**2)
vev = 2.0 * xmw / g
sw2 = 0.22341974678898546
cw2 = 1.0 - sw2
alpha = 1/127.938

#alpha = g**2 * sw2 / (4.0 * np.pi)
