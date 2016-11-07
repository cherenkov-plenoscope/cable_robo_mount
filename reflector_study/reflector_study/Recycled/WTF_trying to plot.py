"""
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot([0,0,0], [1,2,1],"b")
plt.show()
"""



#plot bars
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
start_position = np.zeros((2700,3))
end_position = np.zeros((2700,3))
start_position_xyz = np.zeros((2700,3))
end_position_xyz = np.zeros((2700,3))
l = np.zeros([2700])
m = np.zeros([2700])
n = np.zeros([2700])
for i in range (0,2700):
    try:
        l[i] = int(bars[i,0,0])
        m[i] = int(bars[i,0,1])
        n[i] = int(bars[i,0,2])
        start_position[i] = final_nodes[int(l[i]), int(m[i]), int(n[i])]
        start_position_xyz[i] = final_nodes[int(start_position[i,0]), int(start_position[i,1]), int(start_position[i,2])]

        l[i] = int(bars[i,1,0])
        m[i] = int(bars[i,1,1])
        n[i] = int(bars[i,1,2])
        end_position[i] = final_nodes[int(l[i]), int(m[i]), int(n[i])]
        end_position_xyz[i] = final_nodes[int(end_position[i,0]), int(end_position[i,1]), int(end_position[i,2])]
    except IndexError:
        pass

        ax.set_title('Nodes in addressing coordinates. Note the axis!')
        ax.set_xlabel('x Axis')
        ax.set_ylabel('y Axis')
        ax.set_zlabel('z Axis')

        ax.set_xlim(0, 15)
        ax.set_ylim(0, 15)
        ax.set_zlim(0, 2)

        ax.view_init(elev=0, azim=0)              # elevation and angle
        ax.dist=12                                  # distance

        ax.plot(
            [start_position_xyz[0], end_position_xyz[0]],
            [start_position_xyz[1], end_position_xyz[1]],
            [start_position_xyz[2], end_position_xyz[2]],'b')
plt.show()
