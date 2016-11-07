import numpy as np

def generate_bars(i_radius, j_radius, k_radius, focal_length):
    bars = []
    for n in range(2*i_radius+1):
        for m in range(2*j_radius+1):
            for o in range(k_radius):
                #From the i,j,k coordinates the final results go to cartesian
                nodes[n, m, o] = hcp_parabolic_to_cartesian(
                    i=n-i_radius,
                    j=m-j_radius,
                    k=-o,
                    scale=1,
                    focal_length=focal_length
                )

                # Bars in between layers
                bars.append(np.array([[n, m, o],[n,  m,  o+1]]))
                bars.append(np.array([[n, m, o],[n,  m+1,o+1]]))
                bars.append(np.array([[n, m, o],[n+1,m,  o+1]]))
                bars.append(np.array([[n, m, o],[n+1,m+1,o+1]]))

                # Bars on layer
                bars.append(np.array([[n, m, o],[n,  m+1,o]]))
                bars.append(np.array([[n, m, o],[n+1,m,  o]]))


    bars = np.array(bars)


    return {'nodes': nodes, 'bars': bars}
