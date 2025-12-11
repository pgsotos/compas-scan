#!/usr/bin/env python3
"""
🤖 CompasScan MCP Server

Enterprise-level MCP server exposing CompasScan API as MCP tools.
Integrates with VS Code, Cursor, and other MCP-compatible IDEs.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

import httpx
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    GetResourceRequest,
    GetResourceResult,
    ListResourcesRequest,
    ListResourcesResult,
    ListToolsRequest,
    ListToolsResult,
    Resource,
    TextContent,
    Tool,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CompasScanMCPServer:
    """Enterprise-level MCP Server for CompasScan API integration."""

    def __init__(self):
        self.server = Server("compascan-mcp")
        self.api_base_url = "http://localhost:8000"
        self.api_key = None

        # Register MCP tools
        self._register_tools()

        # Register MCP resources
        self._register_resources()

    def _register_tools(self):
        """Register all MCP tools for CompasScan functionality."""

        # Brand Analysis Tool
        self.server.list_tools = self._list_tools
        self.server.call_tool = self._call_tool

        logger.info(
            "✅ MCP Tools registered: scan_competitors, get_brand_context, analyze_market_trends"
        )

    def _register_resources(self):
        """Register all MCP resources for CompasScan data."""

        self.server.list_resources = self._list_resources
        self.server.read_resource = self._read_resource

        logger.info("✅ MCP Resources registered: brand://, competitor://, market://")

    async def _list_tools(self, request: ListToolsRequest) -> ListToolsResult:
        """List available MCP tools."""
        tools = [
            Tool(
                name="scan_competitors",
                description="Scan competitors for a brand using AI-powered analysis",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "brand": {
                            "type": "string",
                            "description": "Brand name or URL to analyze (e.g., 'Nike' or 'nike.com')",
                            "minLength": 2,
                        },
                        "deep_analysis": {
                            "type": "boolean",
                            "description": "Enable deep competitive analysis (slower but more comprehensive)",
                            "default": False,
                        },
                    },
                    "required": ["brand"],
                },
            ),
            Tool(
                name="get_brand_context",
                description="Get detailed context and analysis for a specific brand",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "brand": {
                            "type": "string",
                            "description": "Brand name to get context for",
                            "minLength": 2,
                        }
                    },
                    "required": ["brand"],
                },
            ),
            Tool(
                name="analyze_market_trends",
                description="Analyze market trends and competitive landscape for an industry",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "industry": {
                            "type": "string",
                            "description": "Industry to analyze (e.g., 'fashion', 'tech', 'automotive')",
                            "enum": [
                                "fashion",
                                "tech",
                                "automotive",
                                "healthcare",
                                "finance",
                                "retail",
                            ],
                        },
                        "region": {
                            "type": "string",
                            "description": "Geographic region to focus on",
                            "default": "global",
                        },
                    },
                    "required": ["industry"],
                },
            ),
            Tool(
                name="get_competitor_insights",
                description="Get detailed insights about specific competitors",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "competitors": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of competitor URLs or names to analyze",
                        }
                    },
                    "required": ["competitors"],
                },
            ),
        ]

        return ListToolsResult(tools=tools)

    async def _call_tool(self, request: CallToolRequest) -> CallToolResult:
        """Handle MCP tool calls."""

        try:
            if request.params.name == "scan_competitors":
                return await self._handle_scan_competitors(request.params.arguments)
            elif request.params.name == "get_brand_context":
                return await self._handle_get_brand_context(request.params.arguments)
            elif request.params.name == "analyze_market_trends":
                return await self._handle_analyze_market_trends(
                    request.params.arguments
                )
            elif request.params.name == "get_competitor_insights":
                return await self._handle_get_competitor_insights(
                    request.params.arguments
                )
            else:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text", text=f"Unknown tool: {request.params.name}"
                        )
                    ],
                    isError=True,
                )

        except Exception as e:
            logger.error(f"Error calling tool {request.params.name}: {e}")
            return CallToolResult(
                content=[
                    TextContent(type="text", text=f"Tool execution failed: {str(e)}")
                ],
                isError=True,
            )

    async def _handle_scan_competitors(
        self, arguments: Dict[str, Any]
    ) -> CallToolResult:
        """Handle competitor scanning tool."""

        brand = arguments.get("brand")
        deep_analysis = arguments.get("deep_analysis", False)

        if not brand:
            return CallToolResult(
                content=[TextContent(type="text", text="Brand parameter is required")],
                isError=True,
            )

        try:
            async with httpx.AsyncClient() as client:
                # Call CompasScan API
                params = {"brand": brand}
                if deep_analysis:
                    params["deep_analysis"] = "true"

                response = await client.get(
                    f"{self.api_base_url}/api/", params=params, timeout=30.0
                )

                if response.status_code == 200:
                    data = response.json()

                    # Format results for MCP
                    result_text = f"""
🎯 **Competitor Analysis for: {brand}**

## 📊 **Summary**
- **Status**: {data.get("status", "Unknown")}
- **Target**: {data.get("target", brand)}
- **Message**: {data.get("message", "No message")}

## 🏆 **High-Domain-Availability (HDA) Competitors**
"""

                    hda_count = 0
                    if data.get("data", {}).get("HDA_Competitors"):
                        for i, comp in enumerate(data["data"]["HDA_Competitors"], 1):
                            result_text += f"{i}. **{comp.get('name', 'Unknown')}**\n"
                            result_text += f"   - URL: {comp.get('url', 'N/A')}\n"
                            result_text += f"   - Justification: {comp.get('justification', 'No justification')}\n\n"
                            hda_count += 1

                    result_text += f"**Total HDA Competitors**: {hda_count}\n\n"

                    # LDA Competitors
                    result_text += (
                        "## 🚀 **Low-Domain-Availability (LDA) Competitors**\n"
                    )

                    lda_count = 0
                    if data.get("data", {}).get("LDA_Competitors"):
                        for i, comp in enumerate(data["data"]["LDA_Competitors"], 1):
                            result_text += f"{i}. **{comp.get('name', 'Unknown')}**\n"
                            result_text += f"   - URL: {comp.get('url', 'N/A')}\n"
                            result_text += f"   - Justification: {comp.get('justification', 'No justification')}\n\n"
                            lda_count += 1

                    result_text += f"**Total LDA Competitors**: {lda_count}\n\n"

                    # Discarded Candidates
                    result_text += "## ❌ **Discarded Candidates**\n"

                    discarded_count = 0
                    if data.get("data", {}).get("Discarded_Candidates"):
                        for i, comp in enumerate(
                            data["data"]["Discarded_Candidates"], 1
                        ):
                            result_text += f"{i}. **{comp.get('url', 'Unknown')}**\n"
                            result_text += (
                                f"   - Reason: {comp.get('reason', 'No reason')}\n\n"
                            )
                            discarded_count += 1

                    result_text += f"**Total Discarded**: {discarded_count}\n\n"

                    # Warnings
                    if data.get("warnings"):
                        result_text += "## ⚠️ **Warnings**\n"
                        for warning in data["warnings"]:
                            result_text += f"- {warning}\n"
                        result_text += "\n"

                    return CallToolResult(
                        content=[TextContent(type="text", text=result_text)],
                        isError=False,
                    )
                else:
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text", text=f"API Error: {response.status_code}"
                            )
                        ],
                        isError=True,
                    )

        except httpx.TimeoutException:
            return CallToolResult(
                content=[
                    TextContent(type="text", text="Request timeout. Please try again.")
                ],
                isError=True,
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Scan failed: {str(e)}")],
                isError=True,
            )

    async def _handle_get_brand_context(
        self, arguments: Dict[str, Any]
    ) -> CallToolResult:
        """Handle brand context tool."""

        brand = arguments.get("brand")
        if not brand:
            return CallToolResult(
                content=[TextContent(type="text", text="Brand parameter is required")],
                isError=True,
            )

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/api/", params={"brand": brand}, timeout=30.0
                )

                if response.status_code == 200:
                    data = response.json()

                    result_text = f"""
🎯 **Brand Context Analysis: {brand}**

## 📋 **Brand Information**
- **Name**: {data.get("brand_context", {}).get("name", brand)}
- **URL**: {data.get("brand_context", {}).get("url", "N/A")}
- **Country**: {data.get("brand_context", {}).get("country", "Not detected")}
- **TLD**: {data.get("brand_context", {}).get("tld", "Not detected")}

## 🔍 **Keywords Identified**
"""

                    keywords = data.get("brand_context", {}).get("keywords", [])
                    if keywords:
                        for i, keyword in enumerate(keywords, 1):
                            result_text += f"{i}. {keyword}\n"

                    result_text += f"""
## 🏭 **Industry Description**
{data.get("brand_context", {}).get("industry_description", "No industry description detected")}

## 🔎 **Search Queries Used**
"""

                    queries = data.get("brand_context", {}).get("search_queries", [])
                    if queries:
                        for i, query in enumerate(queries, 1):
                            result_text += f"{i}. {query}\n"

                    return CallToolResult(
                        content=[TextContent(type="text", text=result_text)],
                        isError=False,
                    )
                else:
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text", text=f"API Error: {response.status_code}"
                            )
                        ],
                        isError=True,
                    )

        except Exception as e:
            return CallToolResult(
                content=[
                    TextContent(type="text", text=f"Context analysis failed: {str(e)}")
                ],
                isError=True,
            )

    async def _handle_analyze_market_trends(
        self, arguments: Dict[str, Any]
    ) -> CallToolResult:
        """Handle market trends analysis tool."""

        industry = arguments.get("industry")
        region = arguments.get("region", "global")

        if not industry:
            return CallToolResult(
                content=[
                    TextContent(type="text", text="Industry parameter is required")
                ],
                isError=True,
            )

        # For now, return a placeholder response
        # In a real implementation, this would call additional APIs or use cached data
        result_text = f"""
📈 **Market Trends Analysis: {industry} ({region})**

## 🏭 **Industry Overview**
Analyzing competitive landscape for {industry} in {region}...

## 📊 **Key Trends**
1. Digital transformation acceleration
2. AI-powered competitive intelligence adoption
3. Sustainability focus in brand positioning
4. Direct-to-consumer (D2C) growth strategies

## 🎯 **Recommendations**
- Leverage AI-powered competitor analysis
- Focus on digital-first customer experience
- Monitor emerging competitors in real-time
- Use data-driven brand positioning strategies

*Note: This is a placeholder implementation. Full market analysis would require additional data sources and APIs.*
"""

        return CallToolResult(
            content=[TextContent(type="text", text=result_text)], isError=False
        )

    async def _handle_get_competitor_insights(
        self, arguments: Dict[str, Any]
    ) -> CallToolResult:
        """Handle competitor insights tool."""

        competitors = arguments.get("competitors", [])
        if not competitors:
            return CallToolResult(
                content=[
                    TextContent(type="text", text="Competitors parameter is required")
                ],
                isError=True,
            )

        result_text = f"""
🔍 **Competitor Insights Analysis**

## 📋 **Competitors Analyzed**
"""

        for i, competitor in enumerate(competitors, 1):
            result_text += f"{i}. **{competitor}**\n"
            result_text += (
                f"   - Analysis: Detailed competitive intelligence would be performed\n"
            )
            result_text += f"   - Status: Ready for deep analysis\n\n"

        result_text += """
## 📊 **Insights Available**
- Market positioning analysis
- Strengths and weaknesses assessment
- Strategic recommendations
- Benchmarking opportunities

*Note: This is a placeholder implementation. Full competitor insights would require additional analysis engines.*
"""

        return CallToolResult(
            content=[TextContent(type="text", text=result_text)], isError=False
        )

    async def _list_resources(
        self, request: ListResourcesRequest
    ) -> ListResourcesResult:
        """List available MCP resources."""

        resources = [
            Resource(
                uri="brand://recent",
                name="Recent Brand Analyses",
                description="Recent competitor analysis results",
                mimeType="application/json",
            ),
            Resource(
                uri="competitor://database",
                name="Competitor Database",
                description="Comprehensive competitor information database",
                mimeType="application/json",
            ),
            Resource(
                uri="market://intelligence",
                name="Market Intelligence",
                description="Market trends and competitive landscape data",
                mimeType="application/json",
            ),
            Resource(
                uri="cache://status",
                name="Cache Status",
                description="Current cache status and metrics",
                mimeType="application/json",
            ),
        ]

        return ListResourcesResult(resources=resources)

    async def _read_resource(self, request: GetResourceRequest) -> GetResourceResult:
        """Read MCP resource content."""

        try:
            if request.params.uri == "brand://recent":
                # Placeholder: Return recent analyses
                content = {
                    "recent_analyses": [
                        {
                            "brand": "Nike",
                            "timestamp": "2025-01-15T10:00:00Z",
                            "status": "completed",
                        },
                        {
                            "brand": "Apple",
                            "timestamp": "2025-01-15T09:30:00Z",
                            "status": "completed",
                        },
                    ]
                }

            elif request.params.uri == "competitor://database":
                # Placeholder: Return competitor database
                content = {
                    "competitors": [
                        {
                            "name": "Adidas",
                            "url": "https://adidas.com",
                            "category": "HDA",
                        },
                        {"name": "Puma", "url": "https://puma.com", "category": "HDA"},
                    ]
                }

            elif request.params.uri == "market://intelligence":
                # Placeholder: Return market intelligence
                content = {
                    "market_trends": {
                        "fashion": {
                            "growth": "+5%",
                            "key_players": ["Nike", "Adidas", "Puma"],
                        },
                        "tech": {
                            "growth": "+12%",
                            "key_players": ["Apple", "Google", "Microsoft"],
                        },
                    }
                }

            elif request.params.uri == "cache://status":
                # Placeholder: Return cache status
                content = {
                    "cache_status": {
                        "redis_connected": True,
                        "total_entries": 150,
                        "hit_rate": "85%",
                        "memory_usage": "45%",
                    }
                }

            else:
                return GetResourceResult(
                    contents=[
                        TextContent(
                            type="text",
                            text=f"Resource not found: {request.params.uri}",
                        )
                    ],
                    isError=True,
                )

            return GetResourceResult(
                contents=[TextContent(type="text", text=json.dumps(content, indent=2))],
                isError=False,
            )

        except Exception as e:
            return GetResourceResult(
                contents=[
                    TextContent(type="text", text=f"Resource access failed: {str(e)}")
                ],
                isError=True,
            )


async def main():
    """Main entry point for MCP server."""

    logger.info("🚀 Starting CompasScan MCP Server...")
    logger.info("📋 Available Tools:")
    logger.info("  - scan_competitors: AI-powered competitor analysis")
    logger.info("  - get_brand_context: Brand context and insights")
    logger.info("  - analyze_market_trends: Market trends analysis")
    logger.info("  - get_competitor_insights: Detailed competitor analysis")
    logger.info("📋 Available Resources:")
    logger.info("  - brand://recent: Recent brand analyses")
    logger.info("  - competitor://database: Competitor database")
    logger.info("  - market://intelligence: Market intelligence data")
    logger.info("  - cache://status: Cache status and metrics")

    # Create and run server
    mcp_server = CompasScanMCPServer()

    # Use stdio_server for MCP protocol
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="compascan-mcp",
                server_version="1.0.0",
                capabilities={"tools": {}, "resources": {}},
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
