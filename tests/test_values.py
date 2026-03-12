import pytest

from gardena_smartsystem_prometheus_exporter.iapi.values import to_camel_case, to_snake_case


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("soilHumidity", "soil_humidity"),
        ("soilTemperature", "soil_temperature"),
        ("rfLinkState", "rf_link_state"),
        ("batteryLevel", "battery_level"),
        ("ambientTemperature", "ambient_temperature"),
        ("lightIntensity", "light_intensity"),
        ("operatingHours", "operating_hours"),
        ("already_snake", "already_snake"),
        ("simple", "simple"),
    ],
)
def test_to_snake_case(input_str, expected):
    assert to_snake_case(input_str) == expected


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("soil_humidity", "soilHumidity"),
        ("soil_temperature", "soilTemperature"),
        ("rf_link_state", "rfLinkState"),
        ("battery_level", "batteryLevel"),
        ("already", "already"),
        ("simple", "simple"),
    ],
)
def test_to_camel_case(input_str, expected):
    assert to_camel_case(input_str) == expected


def test_snake_camel_roundtrip():
    for value in ["soil_humidity", "rf_link_state", "battery_level", "operating_hours"]:
        assert to_snake_case(to_camel_case(value)) == value
