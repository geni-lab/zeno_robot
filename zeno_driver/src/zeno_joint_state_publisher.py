#!/usr/bin/env python
__author__ = 'Jamie Diprose'

import rospy
from sensor_msgs.msg import JointState
from threading import Thread
from dynamixel_msgs.msg import JointState as DynamixelJointState
from itertools import repeat


class ZenoJointStatePublisher(Thread):
    NODE_NAME = 'zeno_robot_joint_state_publisher'

    def __init__(self):
        Thread.__init__(self)
        rospy.init_node(ZenoJointStatePublisher.NODE_NAME, log_level=rospy.INFO)
        self.rate = rospy.Rate(rospy.get_param('~sensor_rate', 15.0))
        self.base_frame_id = rospy.get_param('~base_frame_id', "base_link")
        self.names = ['r_hip_yaw', 'r_hip_roll', 'r_hip_pitch', 'r_knee_pitch', 'r_ankle_pitch', 'r_ankle_roll',
                          'l_hip_yaw', 'l_hip_roll', 'l_hip_pitch', 'l_knee_pitch', 'l_ankle_pitch', 'l_ankle_roll']

        # Pre populate JointState message
        self.joint_state_pub = rospy.Publisher("joint_states", JointState)
        self.joint_state = JointState()
        self.joint_state.header.frame_id = self.base_frame_id
        for name in self.names:
            self.joint_state.name.append(name + "_joint")

        # Subscribe to joint state messages for each joint
        self.joint_positions = list(repeat(0.0, 12))
        self.joint_velocities = list(repeat(0.0, 12))
        for name in self.names:
            controller = name + '_controller/state'
            rospy.loginfo(controller)
            rospy.Subscriber(controller, DynamixelJointState, self.update_dynamixel_joint_state)

    def update_dynamixel_joint_state(self, msg):
        joint_index = msg.motor_ids[0] - 1
        self.joint_positions[joint_index] = msg.current_pos
        self.joint_velocities[joint_index] = msg.velocity

    def run(self):
        while not rospy.is_shutdown():
            self.joint_state.header.stamp = rospy.Time.now()
            # rospy.loginfo("JOINT POSITIONS: " + str(self.joint_positions))
            # rospy.loginfo("JOINT VELOCITIES: " + str(self.joint_velocities))

            self.joint_state.position = list(self.joint_positions)
            self.joint_state.velocity = list(self.joint_velocities)
            self.joint_state_pub.publish(self.joint_state)
            self.rate.sleep()

if __name__ == '__main__':
    rospy.loginfo("Starting {0}...".format(ZenoJointStatePublisher.NODE_NAME))
    joint_pub = ZenoJointStatePublisher()

    joint_pub.start()
    rospy.loginfo("{0} started".format(ZenoJointStatePublisher.NODE_NAME))

    rospy.spin()

    rospy.loginfo("Stopping {0}...".format(ZenoJointStatePublisher.NODE_NAME))
    joint_pub.join()
    rospy.loginfo("{0} stopped.".format(ZenoJointStatePublisher.NODE_NAME))
