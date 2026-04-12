import rospy
from services.srv import PatientData
from test_sensor import SharedSensorTests

class TestG3T1_1(SharedSensorTests):
    """Test suite for G3T1_1 sensor"""
    topic = 'oximeter_data'
    vital_sign = 'oxigenation'

    def test_collect_handles_patient_service_failure(self):
        """Cover collect() branch when getPatientData call fails."""
        if self.patient_service_server is not None:
            self.patient_service_server.shutdown("Simulando indisponibilidade do getPatientData")
            self.patient_service_server = None

        with self.message_lock:
            del self.received_messages[:]

        received_msg = self.wait_for_message(timeout=2.5)
        assert received_msg is not None
        assert received_msg.data == 0.0

        # Restore default mock service to avoid impacting following tests.
        self.patient_service_server = rospy.Service(
            "getPatientData",
            PatientData,
            self.mock_patient_data_service_callback,
        )
        rospy.sleep(0.1)
    