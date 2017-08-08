import pytest
from data_collecting.protocol import CorruptedDataError
from pytest import raises

from aethalometer_collector.storage_handler import generate_filename, \
    AethalometerStorageHandler


class TestStorageHandler:
    @pytest.mark.parametrize("date_value, expected_filename", [
        ("\"01-jan-16\"", "BC010116.csv"),
        ("\"1-jan-16\"", "BC010116.csv"),
        ("01-jan-16", "BC010116.csv"),
        ("\"15-jan-16\"", "BC150116.csv"),
        ("\"15-feb-16\"", "BC150216.csv"),
        ("\"15-feb-17\"", "BC150217.csv"),
        ("\"15-feb-117\"", "BC150217.csv"),
        ("\"15-Feb-17\"", "BC150217.csv"),
    ])
    def test_generate_filename_with_valid_date_value(self, date_value,
                                                     expected_filename):
        filename = generate_filename(date_value)
        assert filename == expected_filename

    @pytest.mark.parametrize("invalid_date_value", [
        "",
        "01jan16",
        "01/jan/16",
        "01-jann-16",
        "A-jan-16",
        "01-jan-A",
        "01-jan",
        "01-16",
        "jan-16",
    ])
    def test_generate_filename_with_invalid_date_value(self,
                                                       invalid_date_value):
        with raises(CorruptedDataError):
            generate_filename(invalid_date_value)

    @pytest.mark.parametrize("data_line", [
        '"01-jan-17","22:10",   2.5, -11.0,  -9.5',
        '"01-jan-17"  ,"22:10",   2.5, -11.0,  -9.5',
        '  "01-jan-17"  ,"22:10",   2.5, -11.0,  -9.5',
    ])
    def test_process_valid_data_line(self, data_line, tmpdir):

        output_file = tmpdir.join("BC010117.csv")
        storage = AethalometerStorageHandler(storage_directory=str(tmpdir))

        storage.process(data_line)

        lines = output_file.readlines()
        assert len(lines) == 1
        assert lines[0] == data_line + '\n'

    def test_process_ignores_empty_data_lines(self, tmpdir):

        storage = AethalometerStorageHandler(storage_directory=str(tmpdir))

        storage.process(data="")

        # No new file was created
        assert len(tmpdir.listdir()) == 0

    @pytest.mark.parametrize("data_line", [
        '"22:10",   2.5, -11.0,  -9.5',
        '"01-jan-17"',
    ])
    def test_process_invalid_data_line(self, data_line, tmpdir):

        storage = AethalometerStorageHandler(storage_directory=str(tmpdir))

        with raises(CorruptedDataError):
            storage.process(data_line)
