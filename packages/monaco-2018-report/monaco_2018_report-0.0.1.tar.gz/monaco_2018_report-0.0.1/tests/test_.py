from unittest.mock import patch, MagicMock
from src import monaco_2018_report
import sys
from src.monaco_2018_report import compute_racers_time, print_report
import pytest


def test_get_data():
    result = monaco_2018_report.get_data("data")

    assert isinstance(result, dict)
    assert len(result) == 3
    assert "abbreviations.txt" in result.keys()
    assert "end.log" in result.keys()
    assert "start.log" in result.keys()
    assert result["abbreviations.txt"][0] == "DRR_Daniel Ricciardo_RED BULL RACING TAG HEUER"
    assert result["start.log"][0] == "SVF2018-05-24_12:02:58.917"
    assert result["end.log"][0] == "MES2018-05-24_12:05:58.778"


def test_build_racers_profile(monkeypatch):
    mocked_folder_path = "data"
    test_args = ["monaco_2018_report\\report.py", "--folder_path", mocked_folder_path]
    monkeypatch.setattr(sys, "argv", test_args)
    profiles = monaco_2018_report.get_racers_profile()

    assert len(profiles) == 19
    assert len(profiles[0]["abbrev"]) == 3
    assert profiles[0]["profile"] == ['Daniel Ricciardo', 'RED BULL RACING TAG HEUER', '12:14:12.054', '12:11:24.067']


def test_calculate_race_time():
    race_time_test_1 = monaco_2018_report.calculate_race_time(start_time = "12:02:58.917", end_time="12:04:03.332")
    race_time_test_2 = monaco_2018_report.calculate_race_time(start_time = "12:14:12.054", end_time="12:11:24.067")
    assert isinstance(race_time_test_1, str)
    assert race_time_test_1 == "00:01:04.415"
    assert race_time_test_2 == "00:02:47.987"
    assert len(race_time_test_1) == 12


def test_compute_racers_time():
    required_keys = ["abbrev", "name", "team", "time"]
    profiles = [{"abbrev": "CSR", "profile": ["Carlos Sainz", "RENAULT", "12:03:15.145", "12:04:28.095"]},
                {"abbrev": "SPF", "profile": ["Sergio Perez", "FORCE INDIA MERCEDES", "12:12:01.035", "12:13:13.883"]}]
    computed_races_result = monaco_2018_report.compute_racers_time(profiles)
    computed_keys = list(computed_races_result[0].keys())

    assert isinstance(computed_races_result, list)
    assert len(computed_races_result[0]) == 4
    assert computed_keys == required_keys
    assert computed_races_result == [{'abbrev': 'CSR', 'name': 'Carlos Sainz', 'team': 'RENAULT', 'time': '00:01:12.950'},
                                     {'abbrev': 'SPF', 'name': 'Sergio Perez', 'team': 'FORCE INDIA MERCEDES', 'time': '00:01:12.848'}]


def test_build_report_with_rank():
    races = [{"name": f"Racer{number}", "team": "TeamA", "time": {number}} for number in range(1, 19)]
    report = monaco_2018_report.build_report(races)
    assert '---------------------------------------------------------------------------' in report
    assert report[16].startswith("16.")


def test_build_report():
    required_args = [{'abbrev': 'CSR', 'name': 'Carlos Sainz', 'team': 'RENAULT', 'time': '00:01:12.950'},
                     {'abbrev': 'SPF', 'name': 'Sergio Perez', 'team': 'FORCE INDIA MERCEDES', 'time': '00:01:12.848'}]
    report = monaco_2018_report.build_report(required_args)

    assert isinstance(report, list)
    assert len(report) == 2
    assert report == ["1. Sergio Perez | FORCE INDIA MERCEDES | 00:01:12.848",
                      "2. Carlos Sainz | RENAULT | 00:01:12.950"]


def test_print_report(capsys):
    mock_racers_profile = [
        {"name": "Racer 1", "team": "Team A", "time": "1:30.456"},
        {"name": "Racer 2", "team": "Team B", "time": "1:31.123"},
    ]
    mock_racers_data = ["1. Racer 1 | Team A | 1:30.456", "2. Racer 2 | Team B | 1:31.123"]

    mock_args = MagicMock()
    mock_args.order = "asc"
    mock_args.driver = "Racer 1"

    with patch("src.monaco_2018_report.report.get_racers_profile", return_value=mock_racers_profile), \
        patch("src.monaco_2018_report.report.compute_racers_time", return_value=mock_racers_data), \
        patch("src.monaco_2018_report.report.parse_arguments") as mock_parser, \
        patch("src.monaco_2018_report.report.build_report", return_value=mock_racers_data):

        mock_parser.return_value.parse_args.return_value = mock_args

        print_report()