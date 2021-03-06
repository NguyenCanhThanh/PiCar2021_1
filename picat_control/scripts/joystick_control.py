#!/usr/bin/env python
# coding: UTF-8

import rospy
import math
from sensor_msgs.msg import Joy
from std_msgs.msg import UInt16, UInt16MultiArray
from geometry_msgs.msg import Twist
from std_srvs.srv import Trigger

class JoyWrapper(object):
    def __init__(self):

        self._BUTTON_SHUTDOWN_1 = rospy.get_param('~button_shutdown_1')
        self._BUTTON_SHUTDOWN_2 = rospy.get_param('~button_shutdown_2')

        self._BUTTON_MOTOR_ON = rospy.get_param('~button_motor_on')
        self._BUTTON_MOTOR_OFF = rospy.get_param('~button_motor_off')

        self._BUTTON_CMD_ENABLE = rospy.get_param('~button_cmd_enable')
        self._AXIS_CMD_LINEAR_X = rospy.get_param('~axis_cmd_linear_x')
        self._AXIS_CMD_ANGULAR_Z = rospy.get_param('~axis_cmd_angular_z')
        self._AXIS_CF_ANGULAR_Z = rospy.get_param('~axis_config_angular_z')

        self._ANALOG_D_PAD = rospy.get_param('~analog_d_pad')
        self._D_PAD_UP = rospy.get_param('~d_pad_up')
        self._D_PAD_DOWN = rospy.get_param('~d_pad_down')
        self._D_PAD_LEFT = rospy.get_param('~d_pad_left')
        self._D_PAD_RIGHT = rospy.get_param('~d_pad_right')

        self._BUTTON_BUZZER_ENABLE = rospy.get_param('~button_buzzer_enable')
        self._DPAD_BUZZER0 = rospy.get_param('~dpad_buzzer0')
        self._DPAD_BUZZER1 = rospy.get_param('~dpad_buzzer1')
        self._DPAD_BUZZER2 = rospy.get_param('~dpad_buzzer2')
        self._DPAD_BUZZER3 = rospy.get_param('~dpad_buzzer3')
        self._BUTTON_BUZZER4 = rospy.get_param('~button_buzzer4')
        self._BUTTON_BUZZER5 = rospy.get_param('~button_buzzer5')
        self._BUTTON_BUZZER6 = rospy.get_param('~button_buzzer6')
        self._BUTTON_BUZZER7 = rospy.get_param('~button_buzzer7')
        
        self._D_UP_IS_POSITIVE = rospy.get_param('~d_pad_up_is_positive')
        self._D_RIGHT_IS_POSITIVE = rospy.get_param('~d_pad_right_is_positive')

        self._BUTTON_CONFIG_ENABLE = rospy.get_param('~button_config_enable')

        # for _joy_velocity_config()
        self._MAX_VEL_LINEAR_X = 1.25  # m/s
        self._MAX_VEL_ANGULAR_Z = 2.0 * math.pi  # rad/s
        self._DEFAULT_VEL_LINEAR_X = 0.5  # m/s
        self._DEFAULT_VEL_ANGULAR_Z = 0.5 * math.pi  # rad/s

        self._joy_msg = None
        self._cmdvel_has_value = False
        self._buzzer_has_value = False
        self._vel_linear_x = self._DEFAULT_VEL_LINEAR_X
        self._vel_angular_z = self._DEFAULT_VEL_ANGULAR_Z

        self._pub_cmdvel = rospy.Publisher('cmd_vel', Twist, queue_size=1)
        self._pub_buzzer = rospy.Publisher('buzzer', UInt16MultiArray, queue_size=1)
        self._sub_joy = rospy.Subscriber('joy', Joy, self._callback_joy, queue_size=1)

    def _callback_joy(self, msg):
        self._joy_msg = msg

    def _motor_on(self):
        rospy.loginfo("motor_on")

    def _motor_off(self):
        rospy.loginfo("motor_off")

    def _joy_dpad(self, joy_msg, target_pad, positive_on):
        if self._ANALOG_D_PAD:
            if positive_on:
                return joy_msg.axes[target_pad] > 0
            else:
                return joy_msg.axes[target_pad] < 0
        else:
            return joy_msg.buttons[target_pad]

    def _dpad_up(self, joy_msg):
        positive_on = self._D_UP_IS_POSITIVE
        return self._joy_dpad(joy_msg, self._D_PAD_UP, positive_on)

    def _dpad_down(self, joy_msg):
        positive_on = not self._D_UP_IS_POSITIVE
        return self._joy_dpad(joy_msg, self._D_PAD_DOWN, positive_on)

    def _dpad_left(self, joy_msg):
        positive_on = not self._D_RIGHT_IS_POSITIVE
        return self._joy_dpad(joy_msg, self._D_PAD_LEFT, positive_on)

    def _dpad_right(self, joy_msg):
        positive_on = self._D_RIGHT_IS_POSITIVE
        return self._joy_dpad(joy_msg, self._D_PAD_RIGHT, positive_on)

    def _dpad(self, joy_msg, target):
        if target == "up":
            return self._dpad_up(joy_msg)
        elif target == "down":
            return self._dpad_down(joy_msg)
        elif target == "left":
            return self._dpad_left(joy_msg)
        elif target == "right":
            return self._dpad_right(joy_msg)
        else:
            return False

    def _joy_shutdown(self, joy_msg):
        if joy_msg.buttons[self._BUTTON_SHUTDOWN_1] and\
                joy_msg.buttons[self._BUTTON_SHUTDOWN_2]:

            self._pub_cmdvel.publish(Twist())
            self._motor_off()
            rospy.signal_shutdown('finish')

    def _joy_motor_onoff(self, joy_msg):
        if joy_msg.buttons[self._BUTTON_MOTOR_ON]:
            self._motor_on()

        if joy_msg.buttons[self._BUTTON_MOTOR_OFF]:
	    cmdvel = Twist()
	    cmdvel.linear.x = 0
            cmdvel.angular.z = 0
            rospy.loginfo(cmdvel)
	    self._pub_cmdvel.publish(cmdvel)
	    self._motor_off()
    def _joy_cmdvel(self, joy_msg):
        cmdvel = Twist()
        if joy_msg.buttons[self._BUTTON_CMD_ENABLE]:
            cmdvel.linear.x = self._vel_linear_x * joy_msg.axes[self._AXIS_CMD_LINEAR_X]
            cmdvel.angular.z = self._vel_angular_z * joy_msg.axes[self._AXIS_CMD_ANGULAR_Z]
            rospy.loginfo(cmdvel)
            self._pub_cmdvel.publish(cmdvel)

            self._cmdvel_has_value = True
        else:
            if self._cmdvel_has_value:
                self._pub_cmdvel.publish(cmdvel)
                self._cmdvel_has_value = False
    
    def _joy_buzzer_freq(self, joy_msg):
        freq = UInt16MultiArray()
        buttons = [
                self._dpad(joy_msg, self._DPAD_BUZZER0),
                self._dpad(joy_msg, self._DPAD_BUZZER1),
                self._dpad(joy_msg, self._DPAD_BUZZER2),
                self._dpad(joy_msg, self._DPAD_BUZZER3),
                joy_msg.buttons[self._BUTTON_BUZZER4],
                joy_msg.buttons[self._BUTTON_BUZZER5],
                joy_msg.buttons[self._BUTTON_BUZZER6],
                joy_msg.buttons[self._BUTTON_BUZZER7],
                ]
        # buzzer frequency Hz
        SCALES = [
                523, 587, 659, 699,
                784, 880, 987, 1046
                ]

        if joy_msg.buttons[self._BUTTON_BUZZER_ENABLE]:
            buzzer_freq = False
            for i, button in enumerate(buttons):
                if button:
                    buzzer_freq = True
                    freq.data.append( SCALES[i])
                    break
            freq.data.append(125)
            if buzzer_freq:
                self._pub_buzzer.publish(freq)
                rospy.loginfo(freq)
                self._buzzer_has_value = True
        else:
            if self._buzzer_has_value:
                self._pub_buzzer.publish(freq)
                self._buzzer_has_value = False

    # def _positive(self, value):
    #     if value < 0:
    #         return 0
    #     else:
    #         return value

    def _joy_velocity_config(self, joy_msg):
        ADD_VEL_LINEAR_X = 0.1  # m/s
        ADD_VEL_ANGULAR_Z = 0.1 * math.pi  # m/s

        if self._dpad(joy_msg, self._DPAD_BUZZER0):
            print ("up")
        if self._dpad(joy_msg, self._DPAD_BUZZER1):
            print ("right")
        if self._dpad(joy_msg, self._DPAD_BUZZER2):
            print("down")
        if self._dpad(joy_msg, self._DPAD_BUZZER3):
            print("left")

        if joy_msg.buttons[self._BUTTON_CONFIG_ENABLE]:
            if joy_msg.axes[self._AXIS_CMD_LINEAR_X] > 0:
                self._vel_linear_x = self._config_velocity(
                        self._vel_linear_x, ADD_VEL_LINEAR_X,
                        0, self._MAX_VEL_LINEAR_X)
            if joy_msg.axes[self._AXIS_CMD_LINEAR_X] < 0:
                self._vel_linear_x = self._config_velocity(
                        self._vel_linear_x, -ADD_VEL_LINEAR_X,
                        0, self._MAX_VEL_LINEAR_X)

            if joy_msg.axes[self._AXIS_CF_ANGULAR_Z] > 0:
                self._vel_angular_z = self._config_velocity(
                        self._vel_angular_z, -ADD_VEL_ANGULAR_Z,
                        0, self._MAX_VEL_ANGULAR_Z)

            if joy_msg.axes[self._AXIS_CF_ANGULAR_Z] < 0:
                self._vel_angular_z = self._config_velocity(
                        self._vel_angular_z, ADD_VEL_ANGULAR_Z,
                        0, self._MAX_VEL_ANGULAR_Z)

            rospy.loginfo(
                    "linear_x:" + str(self._vel_linear_x) +
                    ", angular_z:" + str(self._vel_angular_z)
                    )

    def _config_velocity(self, current, add, lowerlimit, upperlimit):
        output = current + add

        if output < lowerlimit:
            output = lowerlimit
        if output > upperlimit:
            output = upperlimit

        return output

    def update(self):
        if self._joy_msg is None:
            return

        self._joy_motor_onoff(self._joy_msg)
        self._joy_cmdvel(self._joy_msg)
        self._joy_velocity_config(self._joy_msg)
        self._joy_buzzer_freq(self._joy_msg)
        self._joy_shutdown(self._joy_msg)


def main():
    rospy.init_node('joystick_control')

    joy_wrapper = JoyWrapper()

    r = rospy.Rate(60)
    while not rospy.is_shutdown():
        joy_wrapper.update()
        r.sleep()
if __name__ == '__main__':
    main()
