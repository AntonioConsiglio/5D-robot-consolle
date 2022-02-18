import ikpy
import numpy as np
#from ikpy import plot_utils
from ikpy.chain import Chain
from ikpy.link import OriginLink, URDFLink
import matplotlib.pyplot
from mpl_toolkits.mplot3d import Axes3D

'''
    target = it will be a 4x4 matrix, we only need to give the trasport vector, so basically it will be [[1,0,0,x],[0,1,0,y],[0,0,1,z],[0,0,0,1]]

'''

my_arm_chain = Chain(name='arduino_robot',links=[
    OriginLink(),
    URDFLink(
        name="shoulderZ",
        bounds=(0,3.14),
        origin_translation=[0,0,0],
        origin_orientation=[0,0,0],
        rotation=[0,0,1],
    ),
    URDFLink(
        name="shoulderY",
        bounds=(0,3.14),
        origin_translation=[0,0,100],
        origin_orientation=[1.57,0,0],
        rotation=[0,0,1],
    ),
    URDFLink(
        name="elbow",
        bounds=(0,3.14),
        origin_translation=[0,120,0],
        origin_orientation=[0,0,0],
        rotation=[0,0,1],
    ),
    URDFLink(
        name="wristX",
        bounds=(0,3.14),
        origin_translation=[0,80,0],
        origin_orientation=[0,1.57,1.57],
        rotation=[0,0,1]
    ),
    URDFLink(
        name="wristY",
        bounds=(0,3.14),
        origin_translation=[0,0,30], #in metri
        origin_orientation=[-1.57,0,0],
        rotation=[0,0,1],
    ),
    URDFLink(
        name="handTool",
        origin_translation=[0,-80,0],
        origin_orientation=[0,0,0],
        rotation=[0,0,0]
    ),
])

#post = my_arm_chain.forward_kinematics([0] * 6)


ax = matplotlib.pyplot.figure().add_subplot(111, projection='3d')

target = my_arm_chain.inverse_kinematics([0,0,410])
print(target)
my_arm_chain.plot(target, ax)

#my_arm_chain.plot([0,0,0,0,0,0], ax)
matplotlib.pyplot.show()