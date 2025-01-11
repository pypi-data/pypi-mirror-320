import os
import time
import unittest
from time import sleep

from heinanalyticalcontrol.devices import HPLCController
from heinanalyticalcontrol.devices.Agilent.hplc_param_types import HPLCRunningStatus, HPLCAvailStatus, Command

# CONSTANTS: paths only work in Hein group HPLC machine in room XXX

DEFAULT_COMMAND_PATH = "C:\\Users\\User\\Desktop\\Lucy\\hein-analytical-control\\tests"
DEFAULT_METHOD = "GENERAL-POROSHELL"
DEFAULT_TESTING_METHOD = "GENERAL-POROSHELL-MIN"
DEFAULT_METHOD_DIR = "C:\\ChemStation\\1\\Methods\\"
DATA_DIR = "C:\\Users\\Public\\Documents\\ChemStation\\2\\Data"

HEIN_LAB_CONSTANTS = [DEFAULT_COMMAND_PATH, DEFAULT_METHOD_DIR, DATA_DIR]


class TestChemstationPaths(unittest.TestCase):
    def test_init_right_comm_path(self):
        try:
            HPLCController(data_dir=DATA_DIR, comm_dir=DEFAULT_COMMAND_PATH, method_dir=DEFAULT_METHOD_DIR)
        except FileNotFoundError:
            self.fail("Should not throw error")

    def test_init_wrong_data_dir(self):
        try:
            HPLCController(data_dir=DATA_DIR + "\\fake", comm_dir=DEFAULT_COMMAND_PATH, method_dir=DEFAULT_METHOD_DIR)
            self.fail("FileNotFoundError should be thrown.")
        except FileNotFoundError:
            pass

    def test_init_wrong_comm_dir(self):
        try:
            HPLCController(data_dir=DATA_DIR, comm_dir=DEFAULT_COMMAND_PATH + "\\fake", method_dir=DEFAULT_METHOD_DIR)
            self.fail("FileNotFoundError should be thrown.")
        except FileNotFoundError:
            pass

    def test_init_wrong_method_dir(self):
        try:
            HPLCController(data_dir=DATA_DIR, comm_dir=DEFAULT_COMMAND_PATH, method_dir=DEFAULT_METHOD_DIR + "fake")
            self.fail("FileNotFoundError should be thrown.")
        except FileNotFoundError:
            pass


class TestChemStationIntegration(unittest.TestCase):
    def setUp(self):
        for path in HEIN_LAB_CONSTANTS:
            if not os.path.exists(path):
                self.fail(
                    f"{path} does not exist on your system. If you would like to run tests, please change this path.")

        self.hplc_controller = HPLCController(data_dir=DATA_DIR,
                                              comm_dir=DEFAULT_COMMAND_PATH,
                                              method_dir=DEFAULT_METHOD_DIR)

    def test_status_check_standby(self):
        self.hplc_controller.standby()
        self.assertTrue(self.hplc_controller.status()[0] in [HPLCAvailStatus.STANDBY, HPLCRunningStatus.NOTREADY])

    def test_status_check_preprun(self):
        self.hplc_controller.preprun()
        self.assertEqual(HPLCAvailStatus.PRERUN, self.hplc_controller.status()[0])

    def test_send_command(self):
        try:
            self.hplc_controller.send(Command.GET_METHOD_CMD)
        except Exception as e:
            self.fail(f"Should not throw error: {e}")

    def test_send_str(self):
        try:
            self.hplc_controller.send("Local TestNum")
            self.hplc_controller.send("TestNum = 0")
        except Exception as e:
            self.fail(f"Should not throw error: {e}")

    def test_get_response(self):
        try:
            self.hplc_controller.switch_method(method_name=DEFAULT_METHOD)
            self.hplc_controller.send(Command.GET_METHOD_CMD)
            res = self.hplc_controller.receive()
            self.assertTrue(DEFAULT_METHOD in res)
        except Exception as e:
            self.fail(f"Should not throw error: {e}")

    def test_pump_lamp(self):
        pump_lamp = [
            ("response", self.hplc_controller.lamp_on),
            ("response", self.hplc_controller.lamp_off),
            ("response", self.hplc_controller.pump_on),
            ("response", self.hplc_controller.pump_off),
        ]

        for operation in pump_lamp:
            try:
                operation[1]()
            except Exception as e:
                self.fail(f"Failed due to: {e}")

    def test_start_method(self):
        self.hplc_controller.start_method()
        time.sleep(60)
        self.assertTrue(HPLCRunningStatus.has_member_key(self.hplc_controller.status()[0]))

    def test_run_method(self):
        self.hplc_controller.run_method(experiment_name="test_experiment")
        time.sleep(60)
        self.assertTrue(HPLCRunningStatus.has_member_key(self.hplc_controller.status()[0]))
        data_ready = self.hplc_controller.check_hplc_ready_with_data()
        self.assertTrue(data_ready)


if __name__ == '__main__':
    unittest.main()
