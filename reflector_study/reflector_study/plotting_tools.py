from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

def plot_scatter(lattice_grid_x, lattice_grid_y, lattice_grid_z):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.set_title('Nodes in addressing coordinates. Note the axis!')
    ax.set_xlabel('x Axis')
    ax.set_ylabel('y Axis')
    ax.set_zlabel('z Axis')

    ax.set_xlim(-17, 17)
    ax.set_ylim(-17, 17)
    ax.set_zlim(-3, 1)

    ax.view_init(elev=12, azim=40)              # elevation and angle
    ax.dist=12                                  # distance

    ax.scatter(lattice_grid_x, lattice_grid_y, lattice_grid_z, c = "red" , marker = "o")         #color = "red" etc marker is the symbol
    #ax.plot_wireframe(lattice_grid_x, lattice_grid_y, lattice_grid_z)
    plt.show()

def plot_wireframe(lattice_grid_x, lattice_grid_y, lattice_grid_z):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.set_title('Nodes in addressing coordinates. Note the axis!')
    ax.set_xlabel('x Axis')
    ax.set_ylabel('y Axis')
    ax.set_zlabel('z Axis')

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_zlim(0, 3)

    ax.view_init(elev=12, azim=40)              # elevation and angle
    ax.dist=12                                  # distance

    ax.plot_wireframe(lattice_grid_x, lattice_grid_y, lattice_grid_z)
    plt.show()
