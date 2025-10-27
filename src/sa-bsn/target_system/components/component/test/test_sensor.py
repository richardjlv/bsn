# # -*- coding: utf-8 -*-
import pytest
import rospy
import rostopic
import ros_pytest
from std_msgs.msg import String, Float64
from asserts import is_node_publishing_to_topics, Command, TIMEOUT_SECONDS
from parsers import get_rostopic_sensor_data
from messages.msg import SensorData
import subprocess

class SharedSensorTests:
    """Shared test methods for sensor testing"""

    @staticmethod
    def assert_sensors_are_publishing_data(node, topic_name):
        """Assert that sensors are actively publishing data"""
        is_publishing, missing_topics = is_node_publishing_to_topics(node, topic_name)
        assert is_publishing, "{} is missing data from these topics: {}".format(node, missing_topics)
    
    @staticmethod
    def assert_topic_has_data(sensor_topic_name, timeout=5.0):
        """Assert that a topic is publishing data within a timeout period"""
        try:
            sensor_data = {}
            cmd = ['rostopic', 'echo', sensor_topic_name, '-n', '1']
            topic_executor = Command(cmd)
            stdout_bytes, stderr_bytes, returncode = topic_executor.run(timeout=TIMEOUT_SECONDS)
            sensor_data[sensor_topic_name] = get_rostopic_sensor_data(returncode, stdout_bytes, stderr_bytes)
            assert sensor_data[sensor_topic_name]['data'], "No data published on topic {}".format(sensor_topic_name)
        except Exception as e:
            if str(e) == "TimeoutExpired":
                raise AssertionError("Timeout: No data published on topic {}".format(sensor_topic_name))
            else:
                raise





        # try:
            
        #     msg = rospy.wait_for_message(sensor_topic_name, topic_class[0], timeout=5.0)
        #     print("Temperatura (data): {}".format(msg.data))
        #     print("Risco: {}".format(msg.risk))
        #     print("Bateria: {}".format(msg.batt))
        #     rospy.loginfo("Mensagem recebida com sucesso do no C++!")
        
        # except rospy.ROSException as e:
        #     pytest.fail("Falha ao receber mensagem do topico %s. O no C++ nao esta publicando ou o topico esta errado. Error: %s" % (sensor_topic_name, str(e)))
        # data_received = []
        
        # def callback(data):
        #     data_received.append(data)
        
        # subscriber = rospy.Subscriber(sensor_topic_name, SensorData, callback)
        
        # start_time = time.time()
        # while time.time() - start_time < timeout:
        #     if data_received:
        #         subscriber.unregister()
        #         return
        #     rospy.sleep(0.1)
        
        # subscriber.unregister()
        # assert False, "No data published on topic {} within {} seconds".format(sensor_topic_name, timeout)