"""
Portability Scoring Framework
==============================

10 dimensions, each scored 0–10. Weighted sum gives overall score.

Rubric per dimension:
  0–2: Hostile — actively prevents portability
  3–4: Poor — technically possible but painful
  5–6: Fair — basic capabilities exist
  7–8: Good — solid portability support
  9–10: Excellent — best-in-class, open by design
"""

DIMENSIONS = [
    {
        "name": "API Access",
        "slug": "api_access",
        "weight": 0.15,
        "description": "REST/GraphQL API availability, rate limits, authentication complexity.",
        # Rubric:
        # 0: No API at all
        # 3: Undocumented or SOAP-only API
        # 5: REST API with heavy rate limits
        # 7: Well-documented REST API, reasonable limits
        # 10: Open API with generous limits, GraphQL, SDKs
    },
    {
        "name": "Export Formats",
        "slug": "export_formats",
        "weight": 0.12,
        "description": "CSV, JSON, XML, Parquet export support; schema preservation.",
        # 0: No export capability
        # 3: PDF/print only
        # 5: CSV export but lossy (no relationships)
        # 7: CSV + JSON with relationships
        # 10: Multiple formats including Parquet, schema preserved
    },
    {
        "name": "Data Ownership",
        "slug": "data_ownership",
        "weight": 0.15,
        "description": "Contract terms — who owns the data? Exit clauses? Data deletion rights.",
        # 0: Vendor claims ownership of your production data
        # 3: Ambiguous ownership, no exit clause
        # 5: You own data but exit is expensive/slow
        # 7: Clear ownership, reasonable exit terms
        # 10: Explicit customer ownership, free exit, data deletion on request
    },
    {
        "name": "Schema Documentation",
        "slug": "schema_docs",
        "weight": 0.08,
        "description": "Is the data model published? ERDs? Field-level documentation?",
        # 0: Completely opaque
        # 5: Partial docs, key tables only
        # 10: Full ERD, field-level docs, versioned schema
    },
    {
        "name": "Migration Tools",
        "slug": "migration_tools",
        "weight": 0.10,
        "description": "Official import/export tools, migration guides, professional services.",
        # 0: No tools, no guidance
        # 5: Basic export wizard
        # 10: Full migration toolkit with validation
    },
    {
        "name": "Real-time Streaming",
        "slug": "realtime_streaming",
        "weight": 0.08,
        "description": "MQTT, Kafka, webhooks — can you tap into live data?",
        # 0: No streaming capability
        # 5: Webhooks only, limited events
        # 10: MQTT/Kafka with full event coverage
    },
    {
        "name": "Historical Data Access",
        "slug": "historical_access",
        "weight": 0.10,
        "description": "Can you bulk-query historical records? Time range limits?",
        # 0: No historical access
        # 5: Limited time range or record count
        # 10: Full historical access, no arbitrary limits
    },
    {
        "name": "Bulk Export",
        "slug": "bulk_export",
        "weight": 0.10,
        "description": "Full database dump capability vs. record-by-record extraction.",
        # 0: No bulk export
        # 5: Paginated API only (slow)
        # 10: Full dump with relationships intact
    },
    {
        "name": "Open Standards Compliance",
        "slug": "open_standards",
        "weight": 0.07,
        "description": "OPC-UA, MTConnect, ISA-95, B2MML compliance.",
        # 0: Proprietary everything
        # 5: Partial OPC-UA support
        # 10: Full OPC-UA + MTConnect + ISA-95
    },
    {
        "name": "Community/Ecosystem",
        "slug": "community_ecosystem",
        "weight": 0.05,
        "description": "Third-party integrations, open-source tools, community knowledge.",
        # 0: Walled garden, no ecosystem
        # 5: Some integrations, limited community
        # 10: Vibrant ecosystem, marketplace, open-source tools
    },
]


def calculate_overall(scores: dict[str, float]) -> float:
    """Calculate weighted overall score from dimension scores.

    Args:
        scores: {dimension_slug: value} where value is 0–10

    Returns:
        Weighted score 0–10
    """
    dim_weights = {d["slug"]: d["weight"] for d in DIMENSIONS}
    total = 0.0
    for slug, value in scores.items():
        if slug in dim_weights:
            total += value * dim_weights[slug]
    return round(total, 1)


def grade(score: float) -> str:
    """Letter grade from numeric score."""
    if score >= 9:
        return "A+"
    elif score >= 8:
        return "A"
    elif score >= 7:
        return "B"
    elif score >= 6:
        return "C"
    elif score >= 5:
        return "D"
    else:
        return "F"
