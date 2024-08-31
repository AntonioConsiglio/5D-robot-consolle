import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from hmiLib import MainWindow

from sensor_msgs.msg import Image, JointState

from antoniobot_msgs.action import TargetGoal
import numpy as np
import sys
#3rd party
from PySide2.QtWidgets import QApplication
from threading import Thread

class IKClientNode(Node):
    def __init__(self):
        super().__init__("ik_client_node")
        self.mvclient = ActionClient(self,TargetGoal,"task_server",)
        self.get_logger().info(f"ActionClient initialized Correctly!")

    def send_goal(self,x,y,z):
        goal_msg = TargetGoal.Goal()
        goal_msg.x = x
        goal_msg.y = y
        goal_msg.z = z
        self.get_logger().info(f"Send Target Server request: {goal_msg.x=},{goal_msg.y=}, {goal_msg.z=}")
        
        try:
            self.mvclient.wait_for_server(1)
        except Exception as e:
           self.get_logger().error(str(e)) 
        if not rclpy.ok(): return False

        return self.mvclient.send_goal_async(goal_msg,feedback_callback=self.get_feedback)
        
    def get_feedback(self,feedback_msg):
        self.get_logger().info(f"Feedback from action server: {feedback_msg.feedback}")

class FKTFPub(Node):
    def __init__(self):
        super().__init__("ik_client_node")
        self.pub = self.create_publisher()

    def send_goal(self,x,y,z):
        goal_msg = TargetGoal.Goal()
        goal_msg.x = x
        goal_msg.y = y
        goal_msg.z = z
        self.get_logger().info(f"Send Target Server request: {goal_msg.x=},{goal_msg.y=}, {goal_msg.z=}")
        
        try:
            self.mvclient.wait_for_server(1)
        except Exception as e:
           self.get_logger().error(str(e)) 
        if not rclpy.ok(): return False
        
        return self.mvclient.send_goal_async(goal_msg,feedback_callback=self.get_feedback)
class ImageSUB(Node):
    def __init__(self,image_queue):
        super().__init__("iamge_sub_node")
        self.image_queue = image_queue
        self.sub = self.create_subscription(Image,topic="/color/video/image",callback=self.emitCallback,qos_profile=10)

    def emitCallback(self,image:Image):
        img = np.frombuffer(image.data, dtype=np.uint8).reshape(image.height, image.width, -1)
        # image = np.array(image).reshape(480,640,3)
        #self.get_logger().info(f"Image Recived, adding to queue: {img.shape=}")
        self.image_queue.put(img)
        #self.get_logger().info(f"Queue count: {self.image_queue.qsize()}")

def main():

    rclpy.init()
    
    app = QApplication(sys.argv)
    root = MainWindow()

    img_sub = ImageSUB(root.image_queue)
    action_client = IKClientNode()
    root.assing_logger(img_sub.get_logger())
    root.assing_action_client(action_client)
    
    root.show()

    executor = rclpy.executors.MultiThreadedExecutor()
    executor.add_node(img_sub)
    executor.add_node(action_client)
    t = Thread(target=executor.spin,daemon=True)
    t.start()
    
    app.exec_()
    img_sub.destroy_node()
    action_client.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()