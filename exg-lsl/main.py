from datetime import datetime
import sys
from pylsl import StreamInfo, StreamOutlet
import PySide6.QtWidgets as QtWidgets
import PySide6.QtBluetooth as QtBluetooth
from PySide6.QtCore import QByteArray, Qt
import numpy as np

# Bluetooth stuff
PACKET_LEN = 232
SERVICE_UUID = QtBluetooth.QBluetoothUuid.fromString("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
RX_UUID = QtBluetooth.QBluetoothUuid.fromString("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")
TX_UUID = QtBluetooth.QBluetoothUuid.fromString("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")

# EEG info
EEG_CHANNEL_COUNT = 4
FS_EXG = 250

# Accelerometer info
ACC_AXIS = 3
FS_ACC = 50

class ExgPacket():
    acc = np.array(3)
    eeg = np.array(4)

    @classmethod
    def from_bytes(cls, pkt: np.ndarray, gain: int = 24):
        if len(pkt) != 232:
            return None
        if not (pkt[1] == 222 and pkt[-4] == 239 and pkt[-3] == 190):
            return None

        offset = 2

        acc_x = np.frombuffer(pkt[offset:offset + 6], "<i2"); offset += 6
        acc_y = np.frombuffer(pkt[offset:offset + 6], "<i2"); offset += 6
        acc_z = np.frombuffer(pkt[offset:offset + 6], "<i2"); offset += 6

        exg = []
        for _ in range(4):
            ch_bytes = pkt[offset:offset + 13 * 4]
            offset += 13 * 4
            ch_bytes = np.reshape(ch_bytes, (13, 4)).astype(np.int32)

            v = (
                ch_bytes[:, 2] * (16 ** 4)
                + ch_bytes[:, 1] * (16 ** 2)
                + ch_bytes[:, 0]
            )
            # ch_bytes[:3] is number 0~250 as counter, can serve as interpolation method if ble packet loss
            v = v.astype(np.int64)
            v[v >= (16 ** 6) // 2] -= (16 ** 6)

            exg.append((v * 4.5 / gain / (2 ** 23)) * 1e6)

        output = cls()

        output.acc = np.array([acc_x, acc_y, acc_z])
        output.eeg = np.array(exg)

        output.eeg = output.eeg.T
        output.acc = output.acc.T

        return output

def build_datetime_bytes() -> bytes:
    """
    55 03 06 YY MM DD HH mm SS AA
    """
    now = datetime.now()
    return bytes([
        0x55, 0x03, 0x06,
        (now.year - 2000) & 0xFF,
        now.month & 0xFF,
        now.day & 0xFF,
        now.hour & 0xFF,
        now.minute & 0xFF,
        now.second & 0xFF,
        0xAA
    ])

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("4ch EXG module LSL adapter")

        self.raw_buffer = bytearray()

        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)
        self.setCentralWidget(container)

        devices_widget = QtWidgets.QWidget()
        devices_layout = QtWidgets.QHBoxLayout(devices_widget)
        layout.addWidget(devices_widget)
        self.index = 0

        self.devices_combobox = QtWidgets.QComboBox()
        self.devices_combobox.currentIndexChanged.connect(self.on_device_selected)
        devices_layout.addWidget(self.devices_combobox)

        self.refresh_device_button = QtWidgets.QToolButton()
        self.refresh_device_button.setText("↺")
        self.refresh_device_button.clicked.connect(self.scan_devices)
        devices_layout.addWidget(self.refresh_device_button)

        connect_widget = QtWidgets.QWidget()
        connect_layout = QtWidgets.QHBoxLayout(connect_widget)
        connect_layout.setDirection(QtWidgets.QBoxLayout.Direction.RightToLeft)
        layout.addWidget(connect_widget)

        self.connect_button = QtWidgets.QPushButton("Connect...")
        self.connect_button.clicked.connect(self.connect_device)
        self.connect_button.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        connect_layout.addWidget(self.connect_button)

        self.status_label = QtWidgets.QLabel("Status: N/A")
        connect_layout.addWidget(self.status_label)

        self.devices: list[QtBluetooth.QBluetoothDeviceInfo] = []
        self.scanning = False
        self.scan_devices()

        acc_info = StreamInfo("NCBCI ACC Module", "ACC", ACC_AXIS, FS_ACC)
        self.acc_outlet = StreamOutlet(acc_info)

        eeg_info = StreamInfo("NCBCI EEG Module", "EEG", EEG_CHANNEL_COUNT, FS_EXG)
        self.eeg_outlet = StreamOutlet(eeg_info)

    def update_status(self, message: str) -> None:
        """
        Updates the status message.
        """
        self.status_label.setText(f"Status: {message}")

    def on_device_found(self, device):
        """
        Callback for when a BLE device is found.
        Adds the corresponding device info into the list of found devices.
        """
        if device.coreConfigurations() == QtBluetooth.QBluetoothDeviceInfo.CoreConfiguration.LowEnergyCoreConfiguration:
            devInfo = QtBluetooth.QBluetoothDeviceInfo(device)
            print(f"{devInfo.name()} || ({devInfo.address().toString()}): {devInfo.rssi()} {devInfo.serviceUuids()}")
            self.devices.append(devInfo)

    def on_scan_finished(self) -> None:
        """
        Callback for when BLE device scan finishes.
        Updates the devices_combobox with the found devices.
        """
        self.scanning = False
        self.devices_combobox.clear()
        self.devices_combobox.addItems([d.name() for d in self.devices])
        self.update_status(f"Found {len(self.devices)} devices!")

    def on_device_connected(self) -> None:
        """
        Callback for when the device is connected.
        After connecting, we discover the services.
        """
        assert(self.selected_device is not None)
        print("Device connected!")
        self.update_status("Discovering services")
        self.ble_controller.discoverServices()

    def on_service_scan_complete(self) -> None:
        """
        Callback for when the service scan is complete.
        Once the scan is complete, we can connect to the service and discover its details.
        """
        print("Service scan complete!")
        assert(self.selected_device is not None)
        assert(len(self.selected_device.serviceUuids()) > 0)
        self.service = self.ble_controller.createServiceObject(SERVICE_UUID)
        if self.service:
            self.service.stateChanged.connect(self.on_service_state_changed)
            self.service.characteristicChanged.connect(self.on_notification_recieved)
            self.service.discoverDetails()
        else:
            self.update_status("Selected bluetooth device is not compatible.")

    def on_notification_recieved(
            self,
            characteristic: QtBluetooth.QLowEnergyCharacteristic,
            value: QByteArray
    ) -> None:
        """
        Callback function for when BLE notification is recieved.
        The BLE notification should be a data packet from the device, and is sent to
        the LSL outlets (if they have consumers).
        """
        if not (self.acc_outlet.have_consumers() or self.eeg_outlet.have_consumers()):
            self.update_status("Device connected, LSL awaiting connection")
            return

        self.update_status("Device connected, LSL connected")

        self.raw_buffer.extend(value.data())
        while len(self.raw_buffer) >= PACKET_LEN:
            pkt = np.frombuffer(self.raw_buffer[:PACKET_LEN], dtype=np.uint8)
            del self.raw_buffer[:PACKET_LEN]
            out = ExgPacket.from_bytes(pkt)
            if out is not None:
                if self.acc_outlet.have_consumers():
                    self.acc_outlet.push_chunk(out.acc.tolist())
                if self.eeg_outlet.have_consumers():
                    self.eeg_outlet.push_chunk(out.eeg.tolist())

        # packet = ExgPacket.from_bytes(value)
        # if packet is not None:
        #     if self.acc_outlet.have_consumers():
        #         self.acc_outlet.push_sample(packet.acc.tolist())
        #     if self.eeg_outlet.have_consumers():
        #         # print(packet.eeg)
        #         self.eeg_outlet.push_sample(packet.eeg.tolist())
        # else:
        #     print("Packet could not be decoded")

    def on_service_state_changed(self, s: QtBluetooth.QLowEnergyService.ServiceState) -> None:
        """
        Callback for when the service state is changed
        (this is called when we're discovering the service, and have successfully discovered the service).

        Once the service is successfully discovered, we want to connect to the notification characteristic,
        as well as sending the update_time command to begin recieving data.
        """
        if s != QtBluetooth.QLowEnergyService.ServiceState.ServiceDiscovered:
            return

        tx_char = self.service.characteristic(TX_UUID)

        if not tx_char.isValid():
            print("Characteristic not found")
            return

        if not (tx_char.properties() & QtBluetooth.QLowEnergyCharacteristic.PropertyType.Notify):
            print("Characteristic does not support notifications")
            return

        notify_desc = tx_char.descriptor(QtBluetooth.QBluetoothUuid.DescriptorType.ClientCharacteristicConfiguration)
        if notify_desc.isValid():
            self.service.characteristicWritten.connect(lambda: print("Wrote to characteristic successfully"))
            self.service.writeDescriptor(notify_desc, b"\x01\x00") # enable notifications

            rx_char = self.service.characteristic(RX_UUID)
            if not rx_char.isValid():
                print("RX Characteristic not valid")
                return

            self.service.writeCharacteristic(rx_char, build_datetime_bytes()) # start command (update time)

            self.update_status("Device successfully connected")
        else:
            print("Descriptor not found...")

    def on_device_selected(self, index: int) -> None:
        """
        Callback called when the device combobox selected index changes.
        Updates the selected device.
        """
        if index >= 0 and index < len(self.devices):
            self.selected_device = self.devices[index]
        else:
            self.selected_device = None

    def connect_device(self) -> None:
        """
        Connects to the selected BLE device.
        To call this function, `self.selected_device` must be an instance of QBluetoothDeviceInfo.
        """
        if self.selected_device is None:
            self.update_status("Must select a device to connect!")
            return

        self.update_status("Connecting...")
        self.ble_controller = QtBluetooth.QLowEnergyController.createCentral(self.selected_device, self)
        self.ble_controller.connected.connect(self.on_device_connected)
        self.ble_controller.disconnected.connect(lambda: self.update_status("Device disconnected"))
        self.ble_controller.discoveryFinished.connect(self.on_service_scan_complete)
        self.ble_controller.connectToDevice()


    def scan_devices(self) -> None:
        """
        Begins a BLE device scan.
        """
        if self.scanning:
            return

        self.update_status("Scanning...")
        self.devices = []
        self.scanning = True
        deviceDiscoveryAgent = QtBluetooth.QBluetoothDeviceDiscoveryAgent(self)
        deviceDiscoveryAgent.setLowEnergyDiscoveryTimeout(5000)
        deviceDiscoveryAgent.deviceDiscovered.connect(self.on_device_found)
        deviceDiscoveryAgent.finished.connect(self.on_scan_finished)
        deviceDiscoveryAgent.canceled.connect(self.on_scan_finished)
        deviceDiscoveryAgent.start(QtBluetooth.QBluetoothDeviceDiscoveryAgent.DiscoveryMethod.LowEnergyMethod)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()

    main_window.setWindowFlags(
        Qt.WindowType.Dialog |
        Qt.WindowType.Window
    )

    main_window.show()
    app.exec()
