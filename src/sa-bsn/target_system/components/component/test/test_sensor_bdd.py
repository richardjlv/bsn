import ros_pytest
from pytest_bdd import scenarios, given, when, then
from test_sensor import SharedSensorTests
import rospy
import rosnode
from asserts import is_node_receiving_multiple_topics

scenarios("../features/target_system.feature")

topics = ['/oximeter_data', '/ecg_data', '/thermometer_data','/abps_data', '/abpd_data', '/glucosemeter_data']
sensors = ['/g3t1_1', '/g3t1_2', '/g3t1_3', '/g3t1_4', '/g3t1_5', '/g3t1_6']
sensor_topic = {
    '/g3t1_1': ['/oximeter_data'],
    '/g3t1_2': ['/ecg_data'],
    '/g3t1_3': ['/thermometer_data'],
    '/g3t1_4': ['/abps_data'],
    '/g3t1_5': ['/abpd_data'],
    '/g3t1_6': ['/glucosemeter_data'],
}

@given("the ROS environment is on")
def ros_environment_is_on():
    rospy.sleep(1)  # Give ROS some time to initialize
    nodes = rosnode.get_node_names()

    assert len(nodes) > 0, "ROS environment is not running or no nodes are active."

@when("I check if the sensors are publishing data")
def sensors_are_publishing_data():
    for sensor, topics in sensor_topic.items():
        SharedSensorTests.assert_sensors_are_publishing_data(sensor, topics)


@when("I check if respective topics have data")
def sensor_topics_have_data():
    for topic in topics:
        SharedSensorTests.assert_topic_has_data(topic)


@then("/g4t1 should receive data")
def g4t1_should_receive_data():
    node_name = '/g4t1'
    is_receiving, missing_topics = is_node_receiving_multiple_topics(node_name, topics)

    assert is_receiving, "{} is missing data from these topics: {}".format(node_name, missing_topics)
