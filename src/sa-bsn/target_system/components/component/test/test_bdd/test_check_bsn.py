import ros_pytest
from pytest_bdd import scenarios, given, when, then, parsers
from interface_map import SYSTEM_MAP
import rospy
import rosnode
from parsers import process_real_time_topics, capture_topic_data
from asserts import node_is_active, bool_node_is_active

scenarios("./features/check_bsn.feature")

def count_and_get_matching_elements_with_time(sensor_data, target_system_data, key, value, evaluate):
    matching_count = 0
    matched_data = []

    # Iterate over both lists and check for matching values and time condition
    for i, sensor_risk in enumerate(sensor_data[key][evaluate]):
        for j, target_risk in enumerate(target_system_data[value]):
            print('SENSOR RISK of {}: {} TARGET RISK: {}'.format(key, sensor_risk, target_risk))
            if sensor_risk == target_risk:
                # Parse time strings into floats
                sensor_time = float(sensor_data[key]['%time'][i])
                target_time = float(target_system_data['%time'][j])

                # Round and compare times
                rounded_sensor_time = round(sensor_time, -5) / 1e6
                rounded_target_time = round(target_time, -5) / 1e6

                print('TIME DIFFERENCE in {}: {} - {}'.format(key, rounded_sensor_time, rounded_target_time))

                if abs(rounded_sensor_time - rounded_target_time) < 2000:
                    matching_count += 1
                    matched_data.append({
                        'sensor_risk': sensor_risk,
                        'sensor_time': sensor_time,
                        'target_risk': target_risk,
                        'target_time': target_time
                    })

    return matching_count, matched_data


def step_given_node_is_inactive(context, node):
    node_name = SYSTEM_MAP[node]
    if node_name in rosnode.get_node_names():
        rosnode.kill_nodes([node_name])
    rospy.sleep(.2)

    is_active = bool_node_is_active(node_name)
    assert not is_active, "{} is active".format(node_name)

def bodyhub_not_process(context):
    target_system_data = context['target_system_data']
    assert not target_system_data, "Patient status is unexpectedly updated in TargetSystemData."
    # Check that no risks are present in the target system data
    if target_system_data:
        for key in ['trm_risk', 'ecg_risk', 'oxi_risk', 'abps_risk', 'abpd_risk', 'glc_risk', 'trm_data', 'ecg_data', 'oxi_data', 'abps_data', 'abpd_data', 'glc_data']:
            # Assert that the target system data for risks is empty or doesn't contain any values
            assert not target_system_data[key], "Expected no data for {}, but found: {}".format(key, target_system_data[key])

SENSOR_TOPIC_INFO = {
    'g3t1_1': {'topic': '/oximeter_data',    'data_key': 'oxi_data',  'risk_key': 'oxi_risk'},
    'g3t1_2': {'topic': '/ecg_data',          'data_key': 'ecg_data', 'risk_key': 'ecg_risk'},
    'g3t1_3': {'topic': '/thermometer_data',  'data_key': 'trm_data', 'risk_key': 'trm_risk'},
    'g3t1_4': {'topic': '/abps_data',         'data_key': 'abps_data', 'risk_key': 'abps_risk'},
    'g3t1_5': {'topic': '/abpd_data',         'data_key': 'abpd_data', 'risk_key': 'abpd_risk'},
    'g3t1_6': {'topic': '/glucosemeter_data', 'data_key': 'glc_data', 'risk_key': 'glc_risk'},
}

def _sensor_topic_info(sensor):
    """Resolve a Gherkin sensor label (e.g. 'the oximeter') to its topic info via SYSTEM_MAP."""
    node_name = SYSTEM_MAP[sensor].lstrip('/')
    return SENSOR_TOPIC_INFO[node_name]

@given(parsers.parse('the patient is being monitored by {sensor}'))
@given('the patient is being monitored by <sensor>')
def step_given_patient_monitored_by_sensor(context, sensor):
    node_is_active([SYSTEM_MAP[sensor], SYSTEM_MAP['the central hub']])

@when('<sensor> reports a new vital sign reading')
@when(parsers.parse('{sensor} reports a new vital sign reading'))
def step_when_sensor_reports_new_reading(context, sensor):
    context['sensor_data'] = {}
    context['found_high_risk'] = []
    context['target_system_data'] = {}

    topic = _sensor_topic_info(sensor)['topic']
    process_real_time_topics(context, capture_topic_data, [topic, "/TargetSystemData"])

@when('the oximeter reports a blood oxygenation reading outside its normal range')
def step_when_oximeter_reports_out_of_range(context):
    step_when_sensor_reports_new_reading(context, 'the oximeter')

@then(parsers.parse('the central hub should receive that reading with the value reported by {sensor}'))
@then('the central hub should receive that reading with the value reported by <sensor>')
def step_then_central_hub_receives_reading(context, sensor):
    info = _sensor_topic_info(sensor)
    count, matched = count_and_get_matching_elements_with_time(
        context['sensor_data'], context['target_system_data'], info['topic'], info['data_key'], 'data'
    )
    assert count > 0, "Topics {} and {} do not have matching data.".format(info['topic'], info['data_key'])

@then('the central hub should classify the patient risk for blood oxygenation as high')
def step_then_central_hub_classifies_high_risk(context):
    info = _sensor_topic_info('the oximeter')
    count, matched = count_and_get_matching_elements_with_time(
        context['sensor_data'], context['target_system_data'], info['topic'], info['risk_key'], 'risk'
    )
    assert count > 0, "Topics {} and {} do not have matching risk data.".format(info['topic'], info['risk_key'])
    assert any(float(m['target_risk']) > 10 for m in matched), \
        "Central hub did not classify the blood oxygenation reading as high risk."

@given('the central hub is unavailable')
def step_given_central_hub_unavailable(context):
    step_given_node_is_inactive(context, 'the central hub')

@then('no patient risk level should be reported for that reading')
def step_then_no_patient_risk_reported(context):
    bodyhub_not_process(context)
