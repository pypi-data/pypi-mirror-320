import math
import struct
from datetime import datetime
from logger import setup_logger

logger = setup_logger(__name__, 'heartbeat-log')


class Client:
    """
    A class to store status information about IZZY devices.

    delimiter (bytearray)
        The delimiter for bytearray message building.

    name (str)
        A user-friendly name for the device.

    uuid (UUID)
        A 64-bit unique UUID generated at device startup.

    ip_address (str)
        A string representation of the IP address of the unit.

    status (IZZYStatus)
        Current status of the device.

    last_contact (datetime)
        Holds the time of the last contact with Mother server.

    wheel_radius (float)
        The radius of a drive wheel, in mm.

    system_radius (float)
        The distance from the center of the unit to the outer edge of a drive wheel, in mm.

    line_sensor_y_offset (int)
        The distance from the center of the unit to the middle of the line sensor array, in mm.

    encoder_resolution (int)
        The number of encoder counts for one revolution of the motor drive shaft.

    motor_ratio (int)
        The gearbox reduction ratio.

    position ('x'=int, 'y'=int, 'z'=int)
        A dictionary holding the current relative x,y,z position of the unit.

    heading (int)
        The relative current heading of the unit in degrees.

    speed (int)
        The current speed of the unit.

    drive_resolution (int)
        The resolution of the motor wheels, in encoder ticks per centimeter of straight-line travel.

    turn_resolution (int)
        The resolution of the motor wheels, in encoder ticks per degree of turn.
    """

    delimiter = ",".encode()
    name = None
    uuid = None
    ip_address = None
    status = None
    last_contact = None
    # TODO: How can I get these initially from Izzy?
    wheel_radius = 67.3 / 2
    system_radius = 124.5
    line_sensor_y_offset = 88
    encoder_resolution = 20
    motor_ratio = 100
    position = {"x": 0, "y": 0, "z": 0}
    heading = 0
    speed = 0
    drive_resolution = int(math.pi * wheel_radius * 2 * encoder_resolution *
                           motor_ratio)
    turn_resolution = int(math.pi / 180 * system_radius * drive_resolution)

    pid_kp = 0
    pid_ki = 0
    pid_kd = 0
    error = 0
    error_angle = 0

    # TODO: I should probably recall the line sensor offsets from Izzy as well.
    line_sensor_1_min = 0
    line_sensor_1_max = 0
    line_sensor_1_read = 0
    line_sensor_1_offset = 0
    line_sensor_2_min = 0
    line_sensor_2_max = 0
    line_sensor_2_read = 0
    line_sensor_2_offset = 0

    def __init__(self):
        """
        Constructor has no parameters. Defines the drive and turn units based on default values for the Mini-IZZY
        test/development platform.
        """
        self.drive_units = f"1 centimeter = {self.drive_resolution} ticks"
        self.turn_units = f"1 degree = {self.turn_resolution} ticks"

    def set_last_contact(self):
        """
        When called, sets the value of `last_contact` to the current time.S
        """
        self.last_contact = datetime.now()

    def build_base_response(self):
        """
        When called, builds a bytearray that contains the client status, name, x, y, z positions, heading,
        and speed with "," as delimiters.

        Returns
        -------
        A bytearray.
        """
        data = bytearray(self.name.encode())
        data.extend(self.delimiter)
        data.extend(struct.pack("i", self.status.value))
        data.extend(self.delimiter)
        data.extend(struct.pack("i", self.position["x"]))
        data.extend(self.delimiter)
        data.extend(struct.pack("i", self.position["y"]))
        data.extend(self.delimiter)
        data.extend(struct.pack("i", self.position["z"]))
        data.extend(self.delimiter)
        data.extend(struct.pack("i", self.heading))
        data.extend(self.delimiter)
        data.extend(struct.pack("i", self.speed))

        logger.debug(f"(%s) - Message length: {len(data)}", format(__name__))

        return data

    def build_following_response(self):
        data = self.build_base_response()
        data.extend(self.delimiter)
        data.extend(struct.pack("f", self.pid_kp))
        data.extened(self.delimiter)
        data.extend(struct.pack("f", self.pid_ki))
        data.extend(self.delimiter)
        data.extend(struct.pack("f", self.pid_kd))
        data.extend(self.delimiter)
        data.extend(struct.pack("f", self.error))
        data.extend(self.delimiter)
        data.extend(struct.pack("f", self.error_angle))
        data.extend(self.delimiter)
        data.extend(struct.pack("f", self.line_sensor_1_min))
        data.extend(self.delimiter)
        data.extend(struct.pack("f", self.line_sensor_1_max))
        data.extend(self.delimiter)
        data.extend(struct.pack("f", self.line_sensor_1_read))
        data.extend(self.delimiter)
        data.extend(struct.pack("f", self.line_sensor_2_min))
        data.extend(self.delimiter)
        data.extend(struct.pack("f", self.line_sensor_2_max))
        data.extend(self.delimiter)
        data.extend(struct.pack("f", self.line_sensor_2_read))

        logger.debug(f"(%s) - length of data: {len(data)}", format(__name__))
        logger.debug(f"(%s) - packed data: {data}", format(__name__))

        return data
