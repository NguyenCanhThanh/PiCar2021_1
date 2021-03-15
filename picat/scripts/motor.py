#!/usr/bin/env python
#encoding: utf8

import sys
import rospy
import math
from picat.msg import MotorFreqs
from picat.srv import PutMotorFreqs
from geometry_msgs.msg import Twist
from std_msgs.msg import UInt16MultiArray, Int16MultiArray, Float32, Int16, Float64, UInt16

class Motor():
    def __init__(self):
        self.motor = rospy.Publisher("/motor", Int16MultiArray, queue_size= 1)
        self.sub_pulse = rospy.Subscriber('pub_pulse', Int16MultiArray, self.calback_pulse)
        self.sub_raw = rospy.Subscriber('motor_raw', MotorFreqs, self.callback_raw_freq)
        self.sub_cmd_vel = rospy.Subscriber('cmd_vel', Twist, self.callback_cmd_vel)
        self.sub_srv_tm = rospy.Service('timed_motion', PutMotorFreqs, self.callback_tm)

        self.vel1 = Float64()
        self.vel2 = Float64()
        self.last_time = rospy.Time.now()
        self.using_cmd_vel = False

    def set_raw_freq(self,left_hz,right_hz):
        m = Int16MultiArray()
        m.data.append(left_hz)
        m.data.append(right_hz)
        self.motor.publish(m)

    def calback_pulse (self, message):
        self.pulse1.data = message.data[0]
        self.pulse2.data = message.data[1]

    def callback_raw_freq(self,message):
        self.set_raw_freq(message.left, message.right)

    def callback_cmd_vel(self,message):
        self.vel1 = (message.linear.x - message.angular.z)
        self.vel2 = (message.linear.x + message.angular.z)
	
        pw1 = UInt16()
        pw2 = UInt16()
        pw1.data = self.vel1*200
        pw2.data = self.vel2*200
        print(pw1.data, pw2.data)
	self.set_raw_freq(pw1.data, pw2.data)

        self.using_cmd_vel = True
        self.last_time = rospy.Time.now()

    def callback_tm(self,message):
        self.set_raw_freq(message.left, message.right)
        rospy.sleep(message.duration)
        self.set_raw_freq(0, 0)

if __name__ == '__main__':
    rospy.init_node('motor_freq')
    m = Motor()
    
    rate = rospy.Rate(1)
    while not rospy.is_shutdown():
        if m.using_cmd_vel and rospy.Time.now().to_sec() - m.last_time.to_sec() >= 1.0:
            m.set_raw_freq(0,0)
            m.using_cmd_vel = False
        rate.sleep()
