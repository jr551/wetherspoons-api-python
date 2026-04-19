"""Unit tests for Wetherspoons API"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from wetherspoons_api import venues, get_venue, get_menus, get_menu, get_drinks
from wetherspoons_api.models import HighLevelVenue, DetailedVenue, HighLevelMenu
import time


@pytest.fixture
def mock_globals_response():
    """Mock global.json response"""
    return {
        "venues": [
            {"identifier": 456, "name": "Test Venue 1"},
            {"identifier": 789, "name": "Test Venue 2"},
        ]
    }


@pytest.fixture
def mock_venues_response():
    """Mock venues API response"""
    return {
        "data": [
            {
                "franchise": "lloyds",
                "id": 123,
                "isClosed": False,
                "name": "The Moon Under Water",
                "venueRef": 456,
                "address": {
                    "line1": "123 Test Street",
                    "town": "London",
                    "postcode": "SW1A 1AA",
                },
            },
            {
                "franchise": "lloyds",
                "id": 124,
                "isClosed": False,
                "name": "The Captain Flinders",
                "venueRef": 999,  # Not in globals
                "address": {
                    "line1": "456 Another Street",
                    "town": "Manchester",
                    "postcode": "M1 1AA",
                },
            },
        ]
    }


@pytest.fixture
def mock_detailed_venue_response():
    """Mock detailed venue API response"""
    return {
        "data": {
            "canPlaceOrder": True,
            "franchise": "lloyds",
            "id": 123,
            "isClosed": False,
            "name": "The Moon Under Water",
            "salesAreas": [{"id": 789}],
            "venueCanOrder": True,
            "venueRef": 456,
            "address": {
                "line1": "123 Test Street",
                "town": "London",
                "postcode": "SW1A 1AA",
            },
        }
    }


@pytest.fixture
def mock_menus_response():
    """Mock menus API response"""
    return {
        "data": [
            {
                "canOrder": True,
                "franchise": "lloyds",
                "id": 1,
                "name": "Drinks",
                "salesAreaId": 789,
                "venueRef": 456,
            },
            {
                "canOrder": True,
                "franchise": "lloyds",
                "id": 2,
                "name": "Food",
                "salesAreaId": 789,
                "venueRef": 456,
            },
        ]
    }


@pytest.fixture
def mock_detailed_menu_response():
    """Mock detailed menu API response"""
    from wetherspoons_api.models import DetailedMenu
    return DetailedMenu(
        data={
            "canOrder": True,
            "categories": [
                {
                    "name": "Beers",
                    "itemGroups": [
                        {
                            "name": "Ales",
                            "items": [
                                {
                                    "itemType": "product",
                                    "id": 12345,
                                    "isOutOfStock": False,
                                    "name": "Ruddles Best",
                                    "description": "4.2% ABV 500ml",
                                    "options": {
                                        "portion": {
                                            "options": [
                                                {
                                                    "label": "500ml",
                                                    "value": {
                                                        "price": {
                                                            "currency": "GBP",
                                                            "discount": 0,
                                                            "initialValue": 299,
                                                            "value": 299,
                                                        }
                                                    },
                                                }
                                            ]
                                        }
                                    },
                                }
                            ]
                        }
                    ]
                }
            ],
            "franchise": "lloyds",
            "id": 1,
            "salesAreaId": 789,
            "venueRef": 456,
        }
    )


class TestVenues:
    """Test venues function"""

    @patch("wetherspoons_api.api._rate_limit")
    @patch("wetherspoons_api.api.requests.get")
    def test_venues_filters_open_venues(self, mock_get, mock_rate_limit, mock_globals_response, mock_venues_response):
        """Test that venues() filters to only open venues"""
        # Mock the globals response
        mock_globals = Mock()
        mock_globals.json.return_value = mock_globals_response
        mock_venues = Mock()
        mock_venues.json.return_value = mock_venues_response
        
        mock_get.side_effect = [mock_globals, mock_venues]
        
        result = venues()
        
        # Should only return venue with venueRef 456 (in globals)
        assert len(result) == 1
        assert result[0].venue_ref == 456
        assert result[0].name == "The Moon Under Water"

    @patch("wetherspoons_api.api._rate_limit")
    @patch("wetherspoons_api.api.requests.get")
    def test_venues_parses_address(self, mock_get, mock_rate_limit, mock_globals_response, mock_venues_response):
        """Test that venues() parses address data correctly"""
        mock_globals = Mock()
        mock_globals.json.return_value = mock_globals_response
        mock_venues = Mock()
        mock_venues.json.return_value = mock_venues_response
        
        mock_get.side_effect = [mock_globals, mock_venues]
        
        result = venues()
        
        assert result[0].address is not None
        assert result[0].address.line1 == "123 Test Street"
        assert result[0].address.town == "London"
        assert result[0].address.postcode == "SW1A 1AA"


class TestGetVenue:
    """Test get_venue function"""

    @patch("wetherspoons_api.api._rate_limit")
    @patch("wetherspoons_api.api._request")
    def test_get_venue_parses_response(self, mock_request, mock_rate_limit, mock_detailed_venue_response):
        """Test that get_venue() parses API response correctly"""
        mock_request.return_value = mock_detailed_venue_response
        
        venue = HighLevelVenue(
            franchise="lloyds",
            id=123,
            is_closed=False,
            name="The Moon Under Water",
            venue_ref=456,
        )
        
        result = get_venue(venue)
        
        assert result.name == "The Moon Under Water"
        assert result.can_place_order is True
        assert result.venue_can_order is True
        assert len(result.sales_areas) == 1
        assert result.sales_areas[0]["id"] == 789


class TestGetMenus:
    """Test get_menus function"""

    @patch("wetherspoons_api.api._rate_limit")
    @patch("wetherspoons_api.api._request")
    def test_get_menus_parses_response(self, mock_request, mock_rate_limit, mock_menus_response):
        """Test that get_menus() parses API response correctly"""
        mock_request.return_value = mock_menus_response
        
        venue = DetailedVenue(
            franchise="lloyds",
            id=123,
            name="The Moon Under Water",
            venue_ref=456,
            sales_areas=[{"id": 789}],
        )
        
        result = get_menus(venue, 789)
        
        assert len(result) == 2
        assert result[0].name == "Drinks"
        assert result[1].name == "Food"


class TestGetDrinks:
    """Test get_drinks function"""

    @patch("wetherspoons_api.api._rate_limit")
    @patch("wetherspoons_api.api.get_menu")
    @patch("wetherspoons_api.api.get_menus")
    @patch("wetherspoons_api.api.get_venue")
    def test_get_drinks_calculates_ppu(
        self, mock_get_venue, mock_get_menus, mock_get_menu, mock_rate_limit, mock_detailed_menu_response
    ):
        """Test that get_drinks() calculates price per unit correctly"""
        mock_detailed_venue = DetailedVenue(
            franchise="lloyds",
            id=123,
            name="The Moon Under Water",
            venue_ref=456,
            sales_areas=[{"id": 789}],
        )
        mock_get_venue.return_value = mock_detailed_venue
        
        mock_menus = [
            HighLevelMenu(
                can_order=True,
                franchise="lloyds",
                id=1,
                name="Drinks",
                sales_area_id=789,
                venue_ref=456,
            )
        ]
        mock_get_menus.return_value = mock_menus
        
        mock_get_menu.return_value = mock_detailed_menu_response
        
        venue = HighLevelVenue(
            franchise="lloyds",
            id=123,
            is_closed=False,
            name="The Moon Under Water",
            venue_ref=456,
        )
        
        result = get_drinks(venue)
        
        assert len(result) == 1
        assert result[0].name == "Ruddles Best"
        # 4.2% ABV, 500ml = 2.1 units
        # Price 299 pence = £2.99
        # PPU = 299 / 2.1 = ~142.38 pence
        assert result[0].units == 2.1
        assert result[0].price == 299
        assert abs(result[0].ppu - 142.38) < 0.1

    @patch("wetherspoons_api.api.get_venue")
    def test_get_drinks_no_sales_areas(self, mock_get_venue):
        """Test that get_drinks() returns empty list when no sales areas"""
        mock_detailed_venue = DetailedVenue(
            franchise="lloyds",
            id=123,
            name="The Moon Under Water",
            venue_ref=456,
            sales_areas=[],
        )
        mock_get_venue.return_value = mock_detailed_venue
        
        venue = HighLevelVenue(
            franchise="lloyds",
            id=123,
            is_closed=False,
            name="The Moon Under Water",
            venue_ref=456,
        )
        
        result = get_drinks(venue)
        
        assert result == []


class TestStrengthAndVolumeToUnits:
    """Test _strength_and_volume_to_units helper function"""

    def test_calculates_units_correctly(self):
        """Test unit calculation formula"""
        from wetherspoons_api.api import _strength_and_volume_to_units
        
        # 4.2% ABV, 500ml = 2.1 units
        result = _strength_and_volume_to_units(4.2, 500)
        assert result == 2.1
        
        # 5.0% ABV, 568ml (pint) = 2.84 units
        result = _strength_and_volume_to_units(5.0, 568)
        assert result == 2.84
