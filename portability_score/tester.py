"""
Portability Test Runner
========================

Automated tests that probe a platform's actual portability capabilities.
Each test returns a TestResult with pass/fail and evidence.

These are skeleton implementations — real tests would hit actual APIs.
"""

from dataclasses import dataclass, field
from typing import Optional
from abc import ABC, abstractmethod


@dataclass
class TestResult:
    test_name: str
    passed: bool
    score: float  # 0–10
    evidence: str = ""
    error: Optional[str] = None


class PortabilityTest(ABC):
    """Base class for all portability tests."""

    name: str
    dimension_slug: str  # which dimension this test contributes to

    @abstractmethod
    def run(self, config: dict) -> TestResult:
        """Run the test against a platform.

        Args:
            config: Platform-specific config (base_url, api_key, etc.)
        """
        ...


class CanExportCSV(PortabilityTest):
    name = "can_export_csv"
    dimension_slug = "export_formats"

    def run(self, config: dict) -> TestResult:
        # Real implementation would:
        # 1. Authenticate to platform API
        # 2. Request CSV export of a known dataset
        # 3. Validate the CSV is well-formed and complete
        # 4. Check for schema preservation (headers match known fields)
        return TestResult(
            test_name=self.name,
            passed=True,
            score=7.0,
            evidence="Mock: CSV export endpoint exists and returns valid data",
        )


class CanExportJSON(PortabilityTest):
    name = "can_export_json"
    dimension_slug = "export_formats"

    def run(self, config: dict) -> TestResult:
        return TestResult(
            test_name=self.name,
            passed=True,
            score=7.0,
            evidence="Mock: JSON API returns structured data with relationships",
        )


class HasRestAPI(PortabilityTest):
    name = "has_rest_api"
    dimension_slug = "api_access"

    def run(self, config: dict) -> TestResult:
        # Real: probe /api, check OpenAPI spec, test CRUD operations
        return TestResult(
            test_name=self.name,
            passed=True,
            score=8.0,
            evidence="Mock: REST API responds at /api/v1, OpenAPI spec available",
        )


class HasStreamingAPI(PortabilityTest):
    name = "has_streaming_api"
    dimension_slug = "realtime_streaming"

    def run(self, config: dict) -> TestResult:
        # Real: check for MQTT broker, Kafka topics, webhook registration
        return TestResult(
            test_name=self.name,
            passed=False,
            score=2.0,
            evidence="Mock: No streaming endpoint found",
        )


class HasBulkExport(PortabilityTest):
    name = "has_bulk_export"
    dimension_slug = "bulk_export"

    def run(self, config: dict) -> TestResult:
        # Real: request full table dump, measure throughput, check completeness
        return TestResult(
            test_name=self.name,
            passed=False,
            score=3.0,
            evidence="Mock: Only paginated API available, no bulk endpoint",
        )


class DataOwnershipClauseCheck(PortabilityTest):
    name = "data_ownership_clause_check"
    dimension_slug = "data_ownership"

    def run(self, config: dict) -> TestResult:
        # Real: NLP analysis of ToS/contract for ownership language
        # Look for: "customer retains ownership", exit clauses, deletion rights
        return TestResult(
            test_name=self.name,
            passed=False,
            score=4.0,
            evidence="Mock: Contract review flagged ambiguous ownership language",
        )


# Registry of all available tests
ALL_TESTS: list[PortabilityTest] = [
    CanExportCSV(),
    CanExportJSON(),
    HasRestAPI(),
    HasStreamingAPI(),
    HasBulkExport(),
    DataOwnershipClauseCheck(),
]


def run_all(config: dict) -> list[TestResult]:
    """Run all portability tests against a platform."""
    results = []
    for test in ALL_TESTS:
        try:
            results.append(test.run(config))
        except Exception as e:
            results.append(TestResult(
                test_name=test.name, passed=False, score=0,
                error=str(e),
            ))
    return results
