#!/usr/bin/env python
__author__ = 'Jamie Diprose'

import rospy
from sensor_msgs.msg import JointState
from threading import Thread
from ros_pololu_servo.srv import pololu_state
from dynamixel_msgs.msg import MotorStateList
import threading


class ZenoSensors(Thread):
    def __init__(self, actuator_yaml_path):
        Thread.__init__(self)

        rospy.init_node('zeno_sensors')
        self.rate = rospy.Rate(rospy.get_param('~sensor_rate', 15.0))
        self.base_frame_id = rospy.get_param('~base_frame_id', "base_link")
        self.joint_state_pub = rospy.Publisher("joint_states", JointState)
        self.joint_state = JointState()
        self.joint_state.header.frame_id = self.base_frame_id
        self.joint_state.name = ['r_hip_yaw_joint', 'r_hip_roll_joint', 'r_hip_pitch_joint', 'r_knee_pitch_joint', 'r_ankle_pitch_joint', 'r_ankle_roll_joint',
                                 'l_hip_yaw_joint', 'l_hip_roll_joint', 'l_hip_pitch_joint', 'l_knee_pitch_joint', 'l_ankle_pitch_joint', 'l_ankle_roll_joint']

        self.motor_states_lock = threading.RLock()
        self.motor_states = []
        self.motor_status_sub = rospy.Subscriber("/motor_states/zeno_legs", MotorStateList, self.update_leg_motor_states)

    def update_leg_motor_states(self, msg):
        with self.motor_states_lock:
            self.motor_states = msg.motor_states

    @staticmethod
    def encoder_to_radians(encoder):
        return encoder

    def run(self):
        while not rospy.is_shutdown():
            self.joint_state.header.stamp = rospy.Time.now()
            position = []
            velocity = []

            with self.motor_states_lock:
                for motor_state in self.motor_states:
                    position.append(ZenoSensors.encoder_to_radians(motor_state.position))
                    velocity.append(motor_state.speed)

            self.joint_state.position = position
            self.joint_state.velocity = velocity
            self.joint_state_pub.publish(self.joint_state)
            self.rate.sleep()

if __name__ == '__main__':
    rospy.loginfo("Starting zeno_sensors...")
    sensors = ZenoSensors()
    sensors.start()
    rospy.loginfo("zeno_sensors started")

    rospy.spin()

    rospy.loginfo("Stopping zeno_sensors...")
    sensors.join()
    rospy.loginfo("zeno_sensors stopped.")