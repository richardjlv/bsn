from pytest_bdd import given
import rospy
import rosnode

@given("the ROS environment is on")
def ros_environment_is_on():
    rospy.sleep(1)  # Give ROS some time to initialize
    nodes = rosnode.get_node_names()

    assert len(nodes) > 0, "ROS environment is not running or no nodes are active."
