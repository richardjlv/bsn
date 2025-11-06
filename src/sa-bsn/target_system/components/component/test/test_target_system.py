import ros_pytest
from pytest_bdd import scenarios, given, when, then, parsers
from test_sensor import SharedSensorTests
import rospy
import rosnode
from asserts import is_node_receiving_multiple_topics, assert_node_is_online, is_node_publishing_to_topics

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

@when("the /g4t1 node is publishing data")
def g4t1_is_publishing_data():
    SharedSensorTests.assert_sensors_are_publishing_data('/g4t1', ['/TargetSystemData'])

@when("respective topics have data")
def target_system_topics_have_data():
    SharedSensorTests.assert_topic_has_data('/TargetSystemData')

@then("the /data_access node should receive it")
def data_access_should_receive_data():
    node_name = '/data_access'
    is_receiving, missing_topics = is_node_receiving_multiple_topics(node_name, ['/TargetSystemData'])

    assert is_receiving, "{} is missing data from these topics: {}".format(node_name, missing_topics)

param_adapter_is_online = False

@given("the /param_adapter node is online")
def param_adapter_is_online():
    assert_node_is_online('/param_adapter')

@when("I check if topics /reconfigure are inbound from /logger")
def check_reconfigure_inbound_from_logger():
    is_receiving, missing_topics = is_node_publishing_to_topics('/logger', ['/reconfigure'])
    param_adapter_is_online = missing_topics == []
    assert is_receiving, "/logger is missing data from these topics: {}".format(missing_topics)

@when("I check if topics /reconfigure_/g3t1_1 are outbound to /g3t1_1")
def check_reconfigure_outbound_to_g3t1_1():
    is_receiving, missing_topics = is_node_receiving_multiple_topics('/g3t1_1', ['/reconfigure_/g3t1_1'])
    param_adapter_is_online = missing_topics == []
    assert is_receiving, "/g3t1_1 is missing data from these topics: {}".format(missing_topics)

@when("I check if topics /reconfigure_/g3t1_2 are outbound to /g3t1_2")
def check_reconfigure_outbound_to_g3t1_2():
    is_receiving, missing_topics = is_node_receiving_multiple_topics('/g3t1_2', ['/reconfigure_/g3t1_2'])
    param_adapter_is_online = missing_topics == []
    assert is_receiving, "/g3t1_2 is missing data from these topics: {}".format(missing_topics)

@when("I check if topics /reconfigure_/g3t1_3 are outbound to /g3t1_3")
def check_reconfigure_outbound_to_g3t1_3():
    is_receiving, missing_topics = is_node_receiving_multiple_topics('/g3t1_3', ['/reconfigure_/g3t1_3'])
    param_adapter_is_online = missing_topics == []
    assert is_receiving, "/g3t1_3 is missing data from these topics: {}".format(missing_topics)

@when("I check if topics /reconfigure_/g3t1_4 are outbound to /g3t1_4")
def check_reconfigure_outbound_to_g3t1_4():
    is_receiving, missing_topics = is_node_receiving_multiple_topics('/g3t1_4', ['/reconfigure_/g3t1_4'])
    param_adapter_is_online = missing_topics == []
    assert is_receiving, "/g3t1_4 is missing data from these topics: {}".format(missing_topics)

@when("I check if topics /reconfigure_/g3t1_5 are outbound to /g3t1_5")
def check_reconfigure_outbound_to_g3t1_5():
    is_receiving, missing_topics = is_node_receiving_multiple_topics('/g3t1_5', ['/reconfigure_/g3t1_5'])
    assert is_receiving, "/g3t1_5 is missing data from these topics: {}".format(missing_topics)

@when("I check if topics /reconfigure_/g3t1_6 are outbound to /g3t1_6")
def check_reconfigure_outbound_to_g3t1_6():
    is_receiving, missing_topics = is_node_receiving_multiple_topics('/g3t1_6', ['/reconfigure_/g3t1_6'])
    assert is_receiving, "/g3t1_6 is missing data from these topics: {}".format(missing_topics)

@when("I check if topics /reconfigure_/g4t1 are outbound to /g4t1")
def check_reconfigure_outbound_to_g4t1():
    is_receiving, missing_topics = is_node_receiving_multiple_topics('/g4t1', ['/reconfigure_/g4t1'])
    assert is_receiving, "/g4t1 is missing data from these topics: {}".format(missing_topics)

@then("/param_adapter node is connected appropriately")
def param_adapter_connected_appropriately():
    assert param_adapter_is_online, "/param_adapter node is not connected appropriately"

patient_response = {
    'oxigenation': None,
    'heart_rate': None,
    'abps': None,
    'abpd': None,
    'glucose': None,
}

@given("the /Patient node is online")
def patient_node_is_online():
    assert_node_is_online('/patient')
from services.srv import PatientData 
@when(parsers.parse("I call rosservice /getPatientData with {sensor_type} and None"))
def call_get_patient_data_service(sensor_type):
    rospy.wait_for_service('/getPatientData')
    try:
        get_patient_data = rospy.ServiceProxy('/getPatientData', PatientData)
        response = get_patient_data(sensor_type)
        patient_response[sensor_type] = response.data
        assert response.data != '', "No data received from /getPatientData service"
    except rospy.ServiceException as e:
        pytest.fail("Service call to /getPatientData failed: %s" % str(e))
    
@then("response should not be null")
def response_should_not_be_null():
    for response in patient_response.values():
        assert response is not None, "/getPatientData service returned null response"
