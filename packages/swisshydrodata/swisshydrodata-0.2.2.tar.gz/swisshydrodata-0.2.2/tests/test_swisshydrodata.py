from swisshydrodata import SwissHydroData


def test_stations(requests_mock):
    mock_data = [
        {
            "id": "2232",
            "name": "Adelboden",
            "water-body-name": "Allenbach",
            "water-body-type": "river",
        },
        {
            "id": "2629",
            "name": "Agno",
            "water-body-name": "Vedeggio",
            "water-body-type": "river",
        },
    ]
    requests_mock.get(
        "https://swisshydroapi.bouni.de/api/v1/stations",
        json=mock_data,
        status_code=200,
    )
    SHD = SwissHydroData()
    r = SHD.get_stations()
    assert r == mock_data
    assert requests_mock.called


def test_stations_fail(requests_mock):
    requests_mock.get(
        "https://swisshydroapi.bouni.de/api/v1/stations",
        status_code=500,
    )
    SHD = SwissHydroData()
    r = SHD.get_stations()
    assert r is None
    assert requests_mock.called


def test_station(requests_mock):
    mock_data = {
        "name": "Rekingen",
        "water-body-name": "Rhein",
        "water-body-type": "river",
        "coordinates": {"latitude": 47.57034859100692, "longitude": 8.329828541142797},
        "parameters": {
            "discharge": {
                "unit": "m3/s",
                "datetime": "2021-04-12T06:50:00+01:00",
                "value": 335.749,
                "max-24h": 337.483,
                "mean-24h": 328.097,
                "min-24h": 313.777,
            },
            "level": {
                "unit": "°C",
                "datetime": "2021-04-12T06:50:00+01:00",
                "value": 8.79,
                "max-24h": 9.22,
                "mean-24h": 8.79,
                "min-24h": 8.26,
            },
        },
    }
    requests_mock.get(
        "https://swisshydroapi.bouni.de/api/v1/station/2143",
        json=mock_data,
        status_code=200,
    )
    SHD = SwissHydroData()
    r = SHD.get_station(2143)
    assert r == mock_data
    assert requests_mock.called


def test_station_fail(requests_mock):
    requests_mock.get(
        "https://swisshydroapi.bouni.de/api/v1/station/2143",
        status_code=500,
    )
    SHD = SwissHydroData()
    r = SHD.get_station(2143)
    assert r is None
    assert requests_mock.called
