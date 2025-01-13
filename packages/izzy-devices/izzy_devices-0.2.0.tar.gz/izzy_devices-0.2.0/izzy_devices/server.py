class Server:
    """
        A class to store status information about Mother server devices.

        status (IZZYStatus)
            Current status of the device.

        uuid (UUID)
            A 64-bit unique UUID generated at device startup.

        ip_address (str)
            A string representation of the IP address of the unit.

        clients (list[Client])
            Holds a list of the client devices found on the network.
        """
    def __init__(self, uuid):
        """
        Ccnstructor requires a UUID parameter.

        Parameters
        ----------
        uuid (UUID)
            A 64-bit UUID.
        """
        self.status = None
        self.uuid = uuid
        self.ip_address = None
        self.clients = []
