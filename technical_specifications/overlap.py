import numpy as np
import matplotlib.pyplot as plt

def area_overlap_R1_r2_dist(R1, R2, d):

	a = 1/d *np.sqrt(
		(-d+R1+R2)*
		( d-R1+R2)*
		( d+R1-R1)*
		( d+R1+R2)
	)

	s1 = (a+2.0*R1)/2.0
	s2 = (a+2.0*R2)/2.0

	return R1**2.0*np.arcsin(a/(2.0*R1)) + R2**2.0*np.arcsin(a/(2.0*R2)) - np.sqrt(s1*(s1-a)*(s1-R1)**2.0) - np.sqrt(s2*(s2-a)*(s2-R2)**2.0)

def offset(beta):
	return 1.5*np.tan(np.deg2rad(beta))

beta = np.linspace(0,45,100)
plt.plot(beta, area_overlap_R1_r2_dist(1,1,2*offset(beta)) / np.pi)
plt.xlabel("image sensor misalignment beta [deg]")
plt.ylabel("effective aperture area visible to image sensor [1]")
plt.show()