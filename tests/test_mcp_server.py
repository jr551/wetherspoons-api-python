"""Smoke tests for MCP server"""

import pytest
import json
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from wetherspoons_mcp.server import list_tools, call_tool, app


class TestMCPServer:
    """Test MCP server functionality"""

    @pytest.mark.asyncio
    async def test_list_tools_returns_expected_tools(self):
        """Test that list_tools returns all expected tools"""
        tools = await list_tools()
        
        tool_names = [tool.name for tool in tools]
        
        assert "get_venues" in tool_names
        assert "search_venues" in tool_names
        assert "get_venue_details" in tool_names
        assert "get_menus" in tool_names
        assert "get_menu_details" in tool_names
        assert "get_drinks" in tool_names
        
        assert len(tools) == 6

    @pytest.mark.asyncio
    @patch("wetherspoons_mcp.server.venues")
    async def test_get_venues_tool_returns_venues(self, mock_venues):
        """Test get_venues tool returns venue data"""
        # Create mock venue
        mock_venue = Mock()
        mock_venue.name = "Test Venue"
        mock_venue.franchise = "lloyds"
        mock_venue.venue_ref = 123
        mock_venue.address = None
        
        mock_venues.return_value = [mock_venue]
        
        result = await call_tool("get_venues", {})
        
        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["total_count"] == 1
        assert data["showing"] == 1
        assert data["venues"][0]["name"] == "Test Venue"
        assert data["venues"][0]["venue_ref"] == 123

    @pytest.mark.asyncio
    @patch("wetherspoons_mcp.server.venues")
    async def test_search_venues_tool_finds_matches(self, mock_venues):
        """Test search_venues tool finds matching venues"""
        mock_venue1 = Mock()
        mock_venue1.name = "The Watchman"
        mock_venue1.franchise = "lloyds"
        mock_venue1.venue_ref = 5447
        mock_venue1.address = None
        
        mock_venue2 = Mock()
        mock_venue2.name = "The Moon Under Water"
        mock_venue2.franchise = "lloyds"
        mock_venue2.venue_ref = 123
        mock_venue2.address = None
        
        mock_venues.return_value = [mock_venue1, mock_venue2]
        
        result = await call_tool("search_venues", {"name": "Watchman"})
        
        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["matches_found"] == 1
        assert data["venues"][0]["name"] == "The Watchman"
        assert data["venues"][0]["venue_ref"] == 5447

    @pytest.mark.asyncio
    @patch("wetherspoons_mcp.server.venues")
    async def test_get_venue_details_tool_with_invalid_venue(self, mock_venues):
        """Test get_venue_details returns error for invalid venue"""
        mock_venues.return_value = []
        
        result = await call_tool("get_venue_details", {"venue_ref": 999999})
        
        assert len(result) == 1
        data = json.loads(result[0].text)
        assert "error" in data
        assert "Venue not found" in data["error"]

    @pytest.mark.asyncio
    async def test_call_tool_with_unknown_tool_returns_error(self):
        """Test that unknown tool returns error"""
        result = await call_tool("unknown_tool", {})
        
        assert len(result) == 1
        data = json.loads(result[0].text)
        assert "error" in data
        assert "Unknown tool" in data["error"]
