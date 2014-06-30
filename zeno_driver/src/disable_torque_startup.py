#!/usr/bin/env python
__author__ = 'Jamie Diprose'

import rospy
from dynamixel_controllers.srv import TorqueEnable


if __name__ == '__main__':
    NODE_NAME = "zeno_disable_torque_startup"

    rospy.loginfo("Starting {0}...".format(NODE_NAME))
    rospy.init_node(NODE_NAME, log_level=rospy.INFO)

    names = ['r_hip_yaw', 'r_hip_roll', 'r_hip_pitch', 'r_knee_pitch', 'r_ankle_pitch', 'r_ankle_roll',
                          'l_hip_yaw', 'l_hip_roll', 'l_hip_pitch', 'l_knee_pitch', 'l_ankle_pitch', 'l_ankle_roll']

    for name in names:
        service_name = name + '_controller/torque_enable'
        torque_enable_srv = rospy.ServiceProxy(service_name, TorqueEnable)
        rospy.loginfo("Waiting for {0} service".format(service_name))
        rospy.wait_for_service(service_name)
        rospy.loginfo("{0} service found, disabling motor torque".format(service_name))
        torque_enable_srv(False)

    rospy.loginfo("{0} finished.".format(NODE_NAME))


