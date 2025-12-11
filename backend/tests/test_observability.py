#!/usr/bin/env python3
"""
Script de Testing para Observability (Logfire + Sentry)

Este script genera tráfico de prueba para:
1. Logfire: Traces, métricas y logs estructurados
2. Sentry: Errores controlados y contexto

Usage:
    python test_observability.py [--env staging|development|production] [--count N]
"""

import argparse
import asyncio
import json
import sys
import time
from typing import Any

import httpx


# Colores para output
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def print_success(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")


def print_error(msg: str):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")


def print_info(msg: str):
    print(f"{Colors.CYAN}ℹ️  {msg}{Colors.RESET}")


def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.RESET}")


def print_header(msg: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{msg}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}\n")


# URLs por ambiente
ENVIRONMENTS = {
    "development": "https://compas-scan-dev.vercel.app",
    "staging": "https://compas-scan-staging.vercel.app",
    "production": "https://compas-scan.vercel.app",
    "local": "http://localhost:8000",
}

# Marcas de prueba (diversas para generar diferentes traces)
TEST_BRANDS = [
    "Nike",
    "Adidas",
    "Spotify",
    "Netflix",
    "Tesla",
    "Apple",
    "Google",
    "Microsoft",
    "Amazon",
    "Meta",
    "hubspot.com",
    "salesforce.com",
    "shopify.com",
]


async def test_health_check(base_url: str) -> dict[str, Any]:
    """Test 1: Health Check - Genera trace simple en Logfire"""
    print_info("Testing Health Check endpoint...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{base_url}/health")
            response.raise_for_status()
            data = response.json()
            print_success(f"Health Check OK: {data.get('status')}")
            print_info(f"   Observability: {json.dumps(data.get('observability', {}), indent=2)}")
            return {"status": "success", "data": data}
    except Exception as e:
        print_error(f"Health Check failed: {e}")
        return {"status": "error", "error": str(e)}


async def test_successful_scans(base_url: str, brands: list[str], count: int = 3) -> list[dict[str, Any]]:
    """Test 2: Scans Exitosos - Genera traces completos en Logfire"""
    print_header(f"Testing {count} Successful Scans (Logfire Traces)")
    results = []

    selected_brands = brands[:count]

    async with httpx.AsyncClient(timeout=60.0) as client:
        for i, brand in enumerate(selected_brands, 1):
            print_info(f"[{i}/{count}] Scanning: {brand}")
            try:
                start_time = time.time()
                response = await client.get(f"{base_url}/", params={"brand": brand})
                elapsed = time.time() - start_time

                if response.status_code == 200:
                    data = response.json()
                    print_success(f"   ✅ Scan OK ({elapsed:.2f}s)")
                    print_info(f"   Status: {data.get('status')}")
                    if data.get("data"):
                        hda_count = len(data["data"].get("HDA_Competitors", []))
                        lda_count = len(data["data"].get("LDA_Competitors", []))
                        print_info(f"   Found: {hda_count} HDA, {lda_count} LDA competitors")
                    results.append({"brand": brand, "status": "success", "elapsed": elapsed})
                else:
                    print_warning(f"   ⚠️  Status {response.status_code}")
                    results.append({"brand": brand, "status": "error", "code": response.status_code})

            except httpx.TimeoutException:
                print_error("   ❌ Timeout (>60s)")
                results.append({"brand": brand, "status": "timeout"})
            except Exception as e:
                print_error(f"   ❌ Error: {e}")
                results.append({"brand": brand, "status": "error", "error": str(e)})

            # Pequeña pausa entre requests
            if i < count:
                await asyncio.sleep(2)

    return results


async def test_error_scenarios(base_url: str) -> list[dict[str, Any]]:
    """Test 3: Errores Controlados - Genera eventos en Sentry"""
    print_header("Testing Error Scenarios (Sentry Events)")
    results = []

    error_tests = [
        {
            "name": "Missing brand parameter",
            "url": f"{base_url}/",
            "expected_status": 422,
        },
        {
            "name": "Invalid brand (too short)",
            "url": f"{base_url}/?brand=A",
            "expected_status": 422,
        },
        {
            "name": "Non-existent endpoint",
            "url": f"{base_url}/nonexistent",
            "expected_status": 404,
        },
    ]

    async with httpx.AsyncClient(timeout=10.0) as client:
        for test in error_tests:
            print_info(f"Testing: {test['name']}")
            try:
                response = await client.get(test["url"])
                if response.status_code == test["expected_status"]:
                    print_success(f"   ✅ Expected error {test['expected_status']} received")
                    results.append({"test": test["name"], "status": "success", "code": response.status_code})
                else:
                    print_warning(f"   ⚠️  Got {response.status_code}, expected {test['expected_status']}")
                    results.append({"test": test["name"], "status": "unexpected", "code": response.status_code})
            except Exception as e:
                print_error(f"   ❌ Exception: {e}")
                results.append({"test": test["name"], "status": "error", "error": str(e)})

            await asyncio.sleep(1)

    return results


async def test_docs_endpoint(base_url: str) -> dict[str, Any]:
    """Test 4: Docs Endpoint - Genera trace adicional"""
    print_info("Testing Docs endpoint...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{base_url}/docs")
            if response.status_code == 200:
                print_success("Docs endpoint accessible")
                return {"status": "success"}
            else:
                print_warning(f"Docs returned {response.status_code}")
                return {"status": "error", "code": response.status_code}
    except Exception as e:
        print_error(f"Docs test failed: {e}")
        return {"status": "error", "error": str(e)}


async def test_concurrent_requests(base_url: str, count: int = 5) -> list[dict[str, Any]]:
    """Test 5: Requests Concurrentes - Genera múltiples traces simultáneos"""
    print_header(f"Testing {count} Concurrent Requests (Stress Test)")

    async def single_request(brand: str) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                start = time.time()
                response = await client.get(f"{base_url}/", params={"brand": brand})
                elapsed = time.time() - start
                return {
                    "brand": brand,
                    "status": "success" if response.status_code == 200 else "error",
                    "code": response.status_code,
                    "elapsed": elapsed,
                }
        except Exception as e:
            return {"brand": brand, "status": "error", "error": str(e)}

    # Ejecutar requests concurrentes
    brands = TEST_BRANDS[:count]
    tasks = [single_request(brand) for brand in brands]
    results = await asyncio.gather(*tasks)

    success_count = sum(1 for r in results if r.get("status") == "success")
    print_success(f"Completed: {success_count}/{count} successful")

    return results


def print_summary(
    health_result: dict,
    scan_results: list[dict],
    error_results: list[dict],
    docs_result: dict,
    concurrent_results: list[dict],
):
    """Imprime resumen de todos los tests"""
    print_header("📊 Test Summary")

    total_tests = 1 + len(scan_results) + len(error_results) + 1 + len(concurrent_results)
    successful = (
        (1 if health_result.get("status") == "success" else 0)
        + sum(1 for r in scan_results if r.get("status") == "success")
        + sum(1 for r in error_results if r.get("status") == "success")
        + (1 if docs_result.get("status") == "success" else 0)
        + sum(1 for r in concurrent_results if r.get("status") == "success")
    )

    print(f"{Colors.BOLD}Total Tests:{Colors.RESET} {total_tests}")
    print(f"{Colors.BOLD}Successful:{Colors.RESET} {Colors.GREEN}{successful}{Colors.RESET}")
    print(f"{Colors.BOLD}Failed:{Colors.RESET} {Colors.RED}{total_tests - successful}{Colors.RESET}")

    print(f"\n{Colors.BOLD}📈 Expected Observability Data:{Colors.RESET}")
    print(f"  • Logfire: {len(scan_results) + len(concurrent_results) + 2} traces (health + scans + docs)")
    print(f"  • Sentry: {len(error_results)} error events (controlled errors)")
    print("  • Metrics: Request counts, response times, error rates")

    print(f"\n{Colors.CYAN}🔍 Check your dashboards:{Colors.RESET}")
    print("  • Logfire: https://logfire.pydantic.dev")
    print("  • Sentry: https://sentry.io")


async def main():
    parser = argparse.ArgumentParser(description="Test Observability (Logfire + Sentry)")
    parser.add_argument(
        "--env",
        choices=["development", "staging", "production", "local"],
        default="staging",
        help="Environment to test (default: staging)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=3,
        help="Number of successful scans to perform (default: 3)",
    )
    parser.add_argument(
        "--concurrent",
        type=int,
        default=3,
        help="Number of concurrent requests (default: 3)",
    )
    parser.add_argument(
        "--skip-errors",
        action="store_true",
        help="Skip error scenario tests",
    )

    args = parser.parse_args()

    base_url = ENVIRONMENTS[args.env]

    print_header(f"🧪 Observability Testing - {args.env.upper()}")
    print_info(f"Target: {base_url}")
    print_info(f"Scans: {args.count}")
    print_info(f"Concurrent: {args.concurrent}\n")

    # Ejecutar tests
    health_result = await test_health_check(base_url)

    scan_results = await test_successful_scans(base_url, TEST_BRANDS, args.count)

    error_results = []
    if not args.skip_errors:
        error_results = await test_error_scenarios(base_url)

    docs_result = await test_docs_endpoint(base_url)

    concurrent_results = await test_concurrent_requests(base_url, args.concurrent)

    # Resumen
    print_summary(health_result, scan_results, error_results, docs_result, concurrent_results)

    print(f"\n{Colors.GREEN}{Colors.BOLD}✅ Testing Complete!{Colors.RESET}")
    print(f"{Colors.CYAN}Check your observability dashboards in 1-2 minutes for new data.{Colors.RESET}\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Interrupted by user{Colors.RESET}")
        sys.exit(1)
