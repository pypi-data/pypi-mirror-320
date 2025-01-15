from __future__ import annotations
import benanalysis._benpy_core
__all__ = ['BenFile', 'DataInfo', 'DataSet', 'Graph', 'MeasurementTypeUnits', 'Meta', 'load_ben_scan_binary_data', 'load_ben_scan_data', 'load_benfile', 'load_benfile_binary_data', 'load_csv']
class BenFile:
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @property
    def data_info(self) -> DataInfo:
        ...
    @property
    def data_sets(self) -> list[DataSet]:
        ...
    @property
    def graph(self) -> Graph:
        ...
    @property
    def meta(self) -> Meta:
        ...
class DataInfo:
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @property
    def apply_data_calibration(self) -> bool:
        ...
    @property
    def apply_reference(self) -> bool:
        ...
    @property
    def auxiliary_type_and_units(self) -> MeasurementTypeUnits:
        ...
    @property
    def certificate_file(self) -> str:
        ...
    @property
    def data_calibration_file(self) -> str:
        ...
    @property
    def date_and_time(self) -> str:
        ...
    @property
    def post_scan_addon_description(self) -> str:
        ...
    @property
    def post_scan_addon_filename(self) -> str:
        ...
    @property
    def pre_scan_addon_description(self) -> str:
        ...
    @property
    def pre_scan_addon_filename(self) -> str:
        ...
    @property
    def reference_file(self) -> str:
        ...
    @property
    def reference_parameter(self) -> str:
        ...
    @property
    def reference_type(self) -> str:
        ...
    @property
    def scan_summary(self) -> str:
        ...
    @property
    def system_file(self) -> str:
        ...
    @property
    def type_and_units(self) -> MeasurementTypeUnits:
        ...
class DataSet:
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @property
    def data(self) -> benanalysis._benpy_core.Scan:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def no_of_points(self) -> int:
        ...
class Graph:
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @property
    def gv_version(self) -> int:
        ...
    @property
    def x_axis_title(self) -> str:
        ...
    @property
    def y_axis_title(self) -> str:
        ...
class MeasurementTypeUnits:
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @property
    def measurement_type(self) -> str:
        ...
    @property
    def measurement_type_code(self) -> int:
        ...
    @property
    def units(self) -> str:
        ...
    @property
    def units_code(self) -> int:
        ...
class Meta:
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @property
    def file_version(self) -> int:
        ...
    @property
    def has_timestamps(self) -> bool:
        ...
    @property
    def x_type(self) -> str:
        ...
def load_ben_scan_binary_data(buffer: list[int]) -> dict[str, benanalysis._benpy_core.Scan]:
    """
        Loads scan data from a binary buffer.
    
        This function reads binary scan data from the provided buffer and returns
        a map associating spectrum names with their corresponding Scan data.
    
        :param buffer: A vector of bytes containing the binary scan data.
        :return: A map from spectrum names to their corresponding Scan objects.
        :raises RuntimeError: If the buffer is empty.
    """
def load_ben_scan_data(file_path: str) -> dict[str, benanalysis._benpy_core.Scan]:
    """
        Loads scan data from a .ben file.
    
        This function reads a BenWin+ .ben data file from the specified file path
        and returns a map associating spectrum names with their corresponding Scan data.
    
        :param file_path: The path to the .ben file.
        :return: A map from spectrum names to their corresponding Scan objects.
        :raises ReadError: If the file cannot be opened for reading.
    """
def load_benfile(file_path: str) -> BenFile:
    """
        Loads a BenFile object from a file path.
    
        This function reads a BenWin+ .ben data file from the specified path
        and returns a BenFile object representing the parsed file contents.
    
        :param file_path: The path to the .ben file.
        :return: A BenFile object parsed from the file.
        :raises ReadError: If the file cannot be opened for reading.
        :raises RuntimeError: If the file data is empty.
    """
def load_benfile_binary_data(buffer: list[int]) -> BenFile:
    """
        Loads a BenFile object from a binary buffer.
    
        This function reads a BenWin+ .ben file (or equivalent binary data)
        from the provided buffer and returns a BenFile object representing
        the parsed file contents.
    
        :param buffer: A vector of bytes containing the .ben file data.
        :return: A BenFile object parsed from the buffer.
        :raises RuntimeError: If the buffer is empty.
    """
def load_csv(file_path: str) -> benanalysis._benpy_core.Scan:
    """
        Loads scan data from a CSV file.
    
        This function reads a CSV file from the specified file path and returns the
        parsed Scan data. The data is expected to be in key-value pairs, separated by
        a specific delimiter.
    
        :param file_path: The path to the CSV file.
        :return: A Scan object containing the data read from the CSV file.
        :raises ReadError: If the file cannot be opened for reading.
    """
