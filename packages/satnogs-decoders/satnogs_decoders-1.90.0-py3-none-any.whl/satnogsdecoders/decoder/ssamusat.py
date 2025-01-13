# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Ssamusat(KaitaiStruct):
    """:field preamble: ssamusat.preamble
    :field sync_word: ssamusat.sync_word
    :field data_field1: ssamusat.data_field1
    :field data_field2: ssamusat.data_field2
    :field crc: ssamusat.crc
    :field ax25_frame: ssamusat.data_field2.ax25_frame
    :field ax25_header: ssamusat.data_field2.ax25_frame.ax25_header
    :field dest_address: ssamusat.data_field2.ax25_frame.ax25_header.dest_address
    :field dest_ssid: ssamusat.data_field2.ax25_frame.ax25_header.dest_ssid
    :field src_address: ssamusat.data_field2.ax25_frame.ax25_header.src_address
    :field src_ssid: ssamusat.data_field2.ax25_frame.ax25_header.src_ssid
    :field control_id: ssamusat.data_field2.ax25_frame.ax25_header.control_id
    :field pid: ssamusat.data_field2.ax25_frame.ax25_header.pid
    :field information_field: ssamusat.data_field2.ax25_frame.information_field
    :field packet_type: ssamusat.data_field2.ax25_frame.information_field.packet_type
    :field telemetry_data_1: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_1
    :field sensor1: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_1.sensor1
    :field sensor2: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_1.sensor2
    :field sensor3: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_1.sensor3
    :field sensor4: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_1.sensor4
    :field battery_voltage: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_1.battery_voltage
    :field battery_temperature: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_1.battery_temperature
    :field battery_soc: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_1.battery_soc
    :field battery_current: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_1.battery_current
    :field temp_in: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_1.temp_in
    :field temp_out: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_1.temp_out
    :field temp_3: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_1.temp_3
    :field pl_temp: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_1.pl_temp
    :field rtc: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_1.rtc
    :field temp_out_l: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_1.temp_out_l
    :field temp_out_h: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_1.temp_out_h
    :field acceleration_x: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_1.acceleration_x
    :field acceleration_y: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_1.acceleration_y
    :field acceleration_z: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_1.acceleration_z
    :field magnetic_field_x: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_1.magnetic_field_x
    :field magnetic_field_y: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_1.magnetic_field_y
    :field magnetic_field_z: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_1.magnetic_field_z
    :field angular_rate_x: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_1.angular_rate_x
    :field angular_rate_y: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_1.angular_rate_y
    :field angular_rate_z: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_1.angular_rate_z
    :field velocity: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_1.velocity
    :field latitude: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_1.latitude
    :field longitude: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_1.longitude
    :field telemetry_data_2: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_2
    :field gps_time: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_2.gps_time
    :field solar_deployment_status: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_2.solar_deployment_status
    :field eps_health_status: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_2.eps_health_status
    :field adcs_health_status: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_2.adcs_health_status
    :field payload_health_status: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_2.payload_health_status
    :field com_health_status: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_2.com_health_status
    :field battery1_health_status: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_2.battery1_health_status
    :field battery2_health_status: ssamusat.data_field2.ax25_frame.information_field.telemetry_data_2.battery2_health_status
    :field image_data_0: ssamusat.data_field2.ax25_frame.information_field.image_data_0
    :field image_id: ssamusat.data_field2.ax25_frame.information_field.image_data_0.image_id
    :field payload_data: ssamusat.data_field2.ax25_frame.information_field.image_data_0.payload_data
    
    .. seealso::
       Source - https://amu-sat.github.io/
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.preamble = (self._io.read_bytes(5)).decode(u"ascii")
        self.sync_word = self._io.read_u1()
        self.data_field1 = self._io.read_u2be()
        self.data_field2 = Ssamusat.DataField2Struct(self._io, self, self._root)
        self.crc = self._io.read_u2be()

    class InformationFieldStruct(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.packet_type = self._io.read_u1()
            if self.packet_type == 1:
                self.telemetry_data_1 = Ssamusat.TelemetryDataStruct1(self._io, self, self._root)

            if self.packet_type == 2:
                self.telemetry_data_2 = Ssamusat.TelemetryDataStruct2(self._io, self, self._root)

            if self.packet_type == 0:
                self.image_data_0 = Ssamusat.ImageDataStruct0(self._io, self, self._root)



    class ImageDataStruct0(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.image_id = self._io.read_u1()
            self.payload_data = self._io.read_bits_int_be(93)


    class TelemetryDataStruct2(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.gps_time = self._io.read_u8be()
            self.solar_deployment_status = self._io.read_bits_int_be(1) != 0
            self.eps_health_status = self._io.read_bits_int_be(1) != 0
            self.adcs_health_status = self._io.read_bits_int_be(1) != 0
            self.payload_health_status = self._io.read_bits_int_be(1) != 0
            self.com_health_status = self._io.read_bits_int_be(1) != 0
            self.battery1_health_status = self._io.read_bits_int_be(1) != 0
            self.battery2_health_status = self._io.read_bits_int_be(1) != 0


    class DataField2Struct(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.preamble = (self._io.read_bytes(8)).decode(u"ascii")
            self.ax25_frame = Ssamusat.Ax25FrameStruct(self._io, self, self._root)
            self.postamble = (self._io.read_bytes(3)).decode(u"ascii")


    class Ax25HeaderStruct(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_address = (self._io.read_bytes(7)).decode(u"ASCII")
            self.dest_ssid = self._io.read_u1()
            self.src_address = (self._io.read_bytes(7)).decode(u"ASCII")
            self.src_ssid = self._io.read_u1()
            self.control_id = self._io.read_u1()
            self.pid = self._io.read_u1()


    class TelemetryDataStruct1(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sensor1 = self._io.read_f4be()
            self.sensor2 = self._io.read_f4be()
            self.sensor3 = self._io.read_f4be()
            self.sensor4 = self._io.read_f4be()
            self.battery_voltage = self._io.read_f4be()
            self.battery_temperature = self._io.read_f4be()
            self.battery_soc = self._io.read_f4be()
            self.battery_current = self._io.read_f4be()
            self.temp_in = self._io.read_u1()
            self.temp_out = self._io.read_u1()
            self.temp_3 = self._io.read_u1()
            self.pl_temp = self._io.read_u1()
            self.rtc = self._io.read_u8be()
            self.temp_out_l = self._io.read_u1()
            self.temp_out_h = self._io.read_u1()
            self.acceleration_x = self._io.read_f4be()
            self.acceleration_y = self._io.read_f4be()
            self.acceleration_z = self._io.read_f4be()
            self.magnetic_field_x = self._io.read_f4be()
            self.magnetic_field_y = self._io.read_f4be()
            self.magnetic_field_z = self._io.read_f4be()
            self.angular_rate_x = self._io.read_f4be()
            self.angular_rate_y = self._io.read_f4be()
            self.angular_rate_z = self._io.read_f4be()
            self.velocity = self._io.read_f4be()
            self.latitude = self._io.read_f4be()
            self.longitude = self._io.read_f4be()


    class Ax25FrameStruct(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.flag1 = self._io.read_u1()
            self.ax25_header = Ssamusat.Ax25HeaderStruct(self._io, self, self._root)
            self.information_field = Ssamusat.InformationFieldStruct(self._io, self, self._root)
            self.fcs = self._io.read_u2be()
            self.flag2 = self._io.read_u1()



