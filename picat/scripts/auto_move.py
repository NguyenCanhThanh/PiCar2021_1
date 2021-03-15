#!/usr/bin/env python
#encoding: utf8

import sys
import rospy
import math
from picat.msg import MotorFreqs
from picat.srv import PutMotorFreqs
from geometry_msgs.msg import Twist
from std_msgs.msg import Int16MultiArray, Float32,Float32MultiArray

class Auto_move():
    def __init__(self):
        self.cmd_vel = rospy.Publisher("/cmd_vel", Twist, queue_size= 1)
        self.sub_pulse = rospy.Subscriber('pub_pulse', Int16MultiArray, self.calback_pulse)
        rospy.Subscriber("/sonar", Float32MultiArray, self.callback)

        self.sonar_lb = Float32()
        self.sonar_lf = Float32()
        self.sonar_rb = Float32()
        self.sonar_rf = Float32()

    def calback_pulse (self, message):
        self.pulse1.data = message.data[0]
        self.pulse2.data = message.data[1]

    def callback(self, message):
        self.sonar_lb.data = message.data[0]
        self.sonar_lf.data = message.data[1]
        self.sonar_rf.data = message.data[2]
        self.sonar_rb.data = message.data[3]

    def auto_move_sonar(self):
        rate = rospy.Rate(10)
        data = Twist()

        while not rospy.is_shutdown():
            if self.sonar_rf.data < 20.0 or self.sonar_lf.data < 20.0:
                data.linear.x = 0.0
                if self.sonar_lb < self.sonar_rb:
                    data.angular.z = -0.6
             	    self.cmd_vel.publish(data)
                else:
                    data.angular.z = 0.6
                    self.cmd_vel.publish(data)
            else:
                data.linear.x = 0.6
                data.angular.z = 0

                self.cmd_vel.publish(data)
            
            print(self.sonar_rf, self.sonar_lf)
            rate.sleep()

if __name__ == '__main__':
    rospy.init_node('auto_move')
    Auto_move().auto_move_sonar()
