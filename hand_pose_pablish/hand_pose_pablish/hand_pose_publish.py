import rclpy
from rclpy.node import Node
from std_msgs.msg import String

import cv2
import mediapipe as mp
import logging

mp_hands = mp.solutions.hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Create a logger instance
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a file handler to save logs to a file
handler = logging.FileHandler('hand_pose_detection.log')
handler.setLevel(logging.INFO)

# Create a formatter to format the log messages
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)


class HandPosePublish(Node):
    def __init__(self):
        super().__init__('hand_pose_publisher')
        self.pub = self.create_publisher(String, 'hand_pose', 10)
        self.timer = self.create_timer(1, self.timer_callback)

    def timer_callback(self):
        msg = String()
        msg.data = f'Hand position: x=%f, y=%f, z=%f, Hand pose: x=%f, y=%f, z=%f'
        hand_position = None
        hand_pose = None
        image = None
        cap = cv2.VideoCapture(4)
        ret, frame = cap.read()
        if ret:
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = mp_hands.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(image, results.multi_hand_landmarks[0], mp.solutions.hands.HAND_CONNECTIONS)

                for hand_landmarks in results.multi_hand_landmarks:
                    # Extract hand position and pose information from landmarks
                    hand_position = hand_landmarks.landmark[0] 
                    hand_pose = hand_landmarks.landmark[8] 

                    # Log hand position and pose information
                    logger.info('Hand position: x=%f, y=%f, z=%f', hand_position.x, hand_position.y, hand_position.z)
                    logger.info('Hand pose:                                        x=%f, y=%f, z=%f', hand_pose.x, hand_pose.y, hand_pose.z)

            cv2.imshow('Hand Pose Detection', image)
            cv2.waitKey(1)

        if hand_position and hand_pose:
            msg.data = msg.data % (hand_position.x, hand_position.y, hand_position.z, hand_pose.x, hand_pose.y, hand_pose.z)
            self.pub.publish(msg)
            self.get_logger().info(f'pub: {msg.data}')

        cap.release()


def detect_hand_pose(args=None):
    rclpy.init(args=args)
    node = HandPosePublish()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    detect_hand_pose()

