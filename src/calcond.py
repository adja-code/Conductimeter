
import numpy as np
import matplotlib.pyplot as plt

cNa = 5.008 #mS m2 mol-1
cCl = 7.631

mNaCl = 58.44 # g /mol

M = np.arange(6)*0.1 # g/l
C = M/mNaCl * 1000 # mol/m3



cond = (cNa+cCl)*C/100 # mS/cm

for m,s in zip(M,cond):
    print( m,s*1000)

fig, ax = plt.subplots(1)
ax.loglog(C/1000,cond,'o--', color='C0')


Mbig = np.arange(11)*5 # g/l
Cbig = Mbig/mNaCl * 1000 #mol/l

condBig = ( (cNa+cCl)*Cbig/1000 * (1 - np.sqrt(Cbig/1000) ) ) 

for m,s in zip(Mbig,condBig):
    print( m,s)

ax.loglog(Cbig/1000, condBig,'o--', color='C0')
ax.set_xlabel("Concentration NaCl ($mol/l$)")
ax.set_ylabel("Conductivité en $mS/cm$")

plt.show()



