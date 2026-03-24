"""Tests for NPI service — mock lookup and validation."""

import pytest
from app.services.npi_service import lookup_npi_mock, MOCK_PRACTICES


class TestMockNpiLookup:
    def test_known_npi_returns_practice(self):
        result = lookup_npi_mock("1234567890")
        assert result is not None
        assert result.practice_name == "Springfield Family Medicine"
        assert result.specialty == "Family Medicine"
        assert len(result.providers) == 3

    def test_cardiology_npi(self):
        result = lookup_npi_mock("9876543210")
        assert result is not None
        assert result.practice_name == "Bayview Cardiology Associates"
        assert result.specialty == "Cardiology"

    def test_pediatrics_npi(self):
        result = lookup_npi_mock("5551234567")
        assert result is not None
        assert result.specialty == "Pediatrics"
        assert len(result.providers) == 4

    def test_unknown_npi_returns_none(self):
        result = lookup_npi_mock("0000000000")
        assert result is None

    def test_all_mock_npis_have_required_fields(self):
        for npi, data in MOCK_PRACTICES.items():
            result = lookup_npi_mock(npi)
            assert result is not None
            assert result.npi == npi
            assert result.practice_name
            assert result.address
            assert result.specialty
            assert len(result.providers) > 0
            for provider in result.providers:
                assert provider.name
                assert provider.role
                assert provider.npi
