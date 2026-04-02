"""Seed the database with dimensions and initial platform scores."""

from portability_score.models import init_db, Dimension, Platform, Score
from portability_score.framework import DIMENSIONS

# Platform data: {slug: {name, vendor, category, website, description, notes, scores: {dim_slug: (value, notes)}}}
PLATFORMS = {
    "tulip": {
        "name": "Tulip",
        "vendor": "Tulip Interfaces",
        "category": "MES/Composable MfgOS",
        "website": "https://tulip.co",
        "description": "No-code manufacturing platform for frontline operations.",
        "notes": "Triple-layered lock-in: proprietary app builder + data model + edge devices. "
                 "Data is trapped inside their ecosystem by design.",
        "scores": {
            "api_access":          (5, "REST API exists but limited; GraphQL for apps only"),
            "export_formats":      (3, "Basic CSV export; no bulk JSON/Parquet"),
            "data_ownership":      (2, "Proprietary data model; exit is extremely painful; triple-layered lock-in"),
            "schema_docs":         (4, "Some API docs; internal schema not published"),
            "migration_tools":     (1, "No migration tools; no export wizard"),
            "realtime_streaming":  (4, "Connector-based; MQTT possible via edge but limited"),
            "historical_access":   (3, "API queries with pagination; limited historical depth"),
            "bulk_export":         (2, "No bulk export; record-by-record via API only"),
            "open_standards":      (3, "Some OPC-UA via edge; not native"),
            "community_ecosystem": (5, "Growing library; university program; but walled garden"),
        },
    },
    "machinemetrics": {
        "name": "MachineMetrics",
        "vendor": "MachineMetrics",
        "category": "IIoT/Machine Monitoring",
        "website": "https://www.machinemetrics.com",
        "description": "Machine data platform for discrete manufacturing.",
        "notes": "API-first approach; better than average but still SaaS-locked.",
        "scores": {
            "api_access":          (7, "Well-documented REST API; reasonable rate limits"),
            "export_formats":      (6, "CSV and JSON export available"),
            "data_ownership":      (5, "Standard SaaS terms; you own data but extraction is work"),
            "schema_docs":         (6, "API docs are decent; data model partially documented"),
            "migration_tools":     (3, "No official migration tools"),
            "realtime_streaming":  (7, "Webhooks + MQTT available"),
            "historical_access":   (6, "API supports historical queries with time ranges"),
            "bulk_export":         (4, "Paginated API; no full dump"),
            "open_standards":      (6, "MTConnect support; OPC-UA adapter"),
            "community_ecosystem": (5, "Some integrations; growing partner ecosystem"),
        },
    },
    "vorne": {
        "name": "Vorne (XL)",
        "vendor": "Vorne Industries",
        "category": "OEE",
        "website": "https://www.vorne.com",
        "description": "OEE monitoring hardware/software for production lines.",
        "notes": "Hardware-based; data lives on the device which is good for ownership.",
        "scores": {
            "api_access":          (6, "REST API on device; local network access"),
            "export_formats":      (6, "CSV export; JSON via API"),
            "data_ownership":      (8, "Data lives on YOUR hardware; you own it completely"),
            "schema_docs":         (5, "Basic API docs; schema is relatively simple"),
            "migration_tools":     (4, "Manual export; no automated migration"),
            "realtime_streaming":  (5, "Local API polling; no native MQTT/Kafka"),
            "historical_access":   (7, "Full history on device; limited by storage"),
            "bulk_export":         (6, "Can dump all data from device"),
            "open_standards":      (4, "Limited standards support"),
            "community_ecosystem": (3, "Small ecosystem; niche product"),
        },
    },
    "ignition-sepasoft": {
        "name": "Ignition + Sepasoft",
        "vendor": "Inductive Automation / Sepasoft",
        "category": "SCADA/MES",
        "website": "https://inductiveautomation.com",
        "description": "Ignition SCADA platform with Sepasoft MES modules.",
        "notes": "Gold standard for openness in manufacturing. SQL database you own. "
                 "Open architecture, modular, self-hosted.",
        "scores": {
            "api_access":          (9, "Full API; scripting engine; direct DB access"),
            "export_formats":      (9, "Direct SQL access; export anything in any format"),
            "data_ownership":      (10, "Self-hosted; YOUR database; YOUR servers; perpetual license option"),
            "schema_docs":         (8, "Well-documented; active community; open schema"),
            "migration_tools":     (7, "SQL-based so standard tools work; community scripts"),
            "realtime_streaming":  (9, "OPC-UA native; MQTT module; Kafka connector"),
            "historical_access":   (9, "Direct SQL — query anything, no limits"),
            "bulk_export":         (9, "It's YOUR database — pg_dump/mysqldump"),
            "open_standards":      (9, "OPC-UA native; ISA-95 via Sepasoft; B2MML"),
            "community_ecosystem": (9, "Ignition Exchange; massive community; IA University"),
        },
    },
    "aveva-wonderware": {
        "name": "AVEVA (Wonderware)",
        "vendor": "AVEVA / Schneider Electric",
        "category": "SCADA/MES/Historian",
        "website": "https://www.aveva.com",
        "description": "Enterprise SCADA, MES, and historian platform.",
        "notes": "Legacy enterprise — powerful but expensive and complex to extract from.",
        "scores": {
            "api_access":          (5, "APIs exist but complex; SOAP legacy + newer REST"),
            "export_formats":      (4, "Proprietary formats; CSV possible with effort"),
            "data_ownership":      (4, "Enterprise licensing; data accessible but exit is expensive"),
            "schema_docs":         (5, "Documentation exists but enterprise-gated"),
            "migration_tools":     (3, "Professional services required; no self-serve tools"),
            "realtime_streaming":  (6, "OPC-UA/DA; some streaming capability"),
            "historical_access":   (5, "Historian queries; proprietary query language"),
            "bulk_export":         (3, "Difficult; often requires professional services"),
            "open_standards":      (6, "OPC-UA/DA support; ISA-95 partial"),
            "community_ecosystem": (4, "Large install base but gated community"),
        },
    },
    "rockwell-factorytalk": {
        "name": "Rockwell FactoryTalk",
        "vendor": "Rockwell Automation",
        "category": "SCADA/MES/IIoT",
        "website": "https://www.rockwellautomation.com",
        "description": "Industrial automation and MES suite.",
        "notes": "Deep PLC integration but very proprietary ecosystem.",
        "scores": {
            "api_access":          (4, "FactoryTalk APIs; complex authentication; Rockwell-centric"),
            "export_formats":      (3, "Proprietary formats dominate; CSV with effort"),
            "data_ownership":      (3, "Enterprise licensing; vendor-dependent for extraction"),
            "schema_docs":         (4, "Documentation behind TechConnect paywall"),
            "migration_tools":     (2, "Rockwell-to-Rockwell migration only; no outbound tools"),
            "realtime_streaming":  (5, "CIP protocol; OPC-UA adapter available"),
            "historical_access":   (4, "FactoryTalk Historian; proprietary query"),
            "bulk_export":         (3, "Difficult without professional services"),
            "open_standards":      (5, "OPC-UA via gateway; CIP is proprietary"),
            "community_ecosystem": (5, "Large ecosystem but Rockwell-centric"),
        },
    },
    "evocon": {
        "name": "Evocon",
        "vendor": "Evocon",
        "category": "OEE",
        "website": "https://evocon.com",
        "description": "Cloud-based OEE and production monitoring.",
        "notes": "Simple SaaS OEE tool; limited data model.",
        "scores": {
            "api_access":          (5, "Basic REST API"),
            "export_formats":      (5, "CSV export available"),
            "data_ownership":      (5, "Standard SaaS; you own data per terms"),
            "schema_docs":         (4, "Basic API docs"),
            "migration_tools":     (2, "No migration tools"),
            "realtime_streaming":  (3, "Limited streaming; mostly polling"),
            "historical_access":   (5, "API supports date range queries"),
            "bulk_export":         (4, "CSV bulk export; limited scope"),
            "open_standards":      (3, "Minimal standards support"),
            "community_ecosystem": (2, "Small ecosystem"),
        },
    },
    "amper": {
        "name": "Amper",
        "vendor": "Amper",
        "category": "IIoT/Machine Monitoring",
        "website": "https://amper.xyz",
        "description": "Non-invasive machine monitoring via current sensors.",
        "notes": "Simple sensor-based monitoring; limited data depth.",
        "scores": {
            "api_access":          (4, "Basic API; limited documentation"),
            "export_formats":      (4, "CSV export"),
            "data_ownership":      (5, "Standard SaaS terms"),
            "schema_docs":         (3, "Minimal docs"),
            "migration_tools":     (2, "No migration tools"),
            "realtime_streaming":  (4, "Sensor data streaming possible"),
            "historical_access":   (4, "Limited historical access via API"),
            "bulk_export":         (3, "No bulk export"),
            "open_standards":      (2, "Proprietary sensor protocol"),
            "community_ecosystem": (2, "Small/emerging"),
        },
    },
    "redzone": {
        "name": "Redzone",
        "vendor": "QAD Redzone",
        "category": "Connected Workforce",
        "website": "https://rfrenz.com",
        "description": "Connected workforce platform for manufacturing productivity.",
        "notes": "Workforce-focused; data is operational/behavioral.",
        "scores": {
            "api_access":          (3, "Limited API; primarily a mobile-first platform"),
            "export_formats":      (4, "Basic reporting exports"),
            "data_ownership":      (4, "SaaS; data access limited"),
            "schema_docs":         (3, "Limited documentation"),
            "migration_tools":     (1, "No migration support"),
            "realtime_streaming":  (2, "No streaming APIs"),
            "historical_access":   (4, "Report-based historical access"),
            "bulk_export":         (2, "No bulk export capability"),
            "open_standards":      (2, "No manufacturing standards support"),
            "community_ecosystem": (3, "QAD ecosystem; limited third-party"),
        },
    },
    "guidewheel": {
        "name": "Guidewheel",
        "vendor": "Guidewheel",
        "category": "IIoT/Factory OS",
        "website": "https://guidewheel.com",
        "description": "Clip-on power meter for machine monitoring and factory optimization.",
        "notes": "Simple hardware approach; SaaS dashboard.",
        "scores": {
            "api_access":          (4, "Basic API; early stage"),
            "export_formats":      (4, "CSV export from dashboard"),
            "data_ownership":      (5, "Standard SaaS terms; sensor data"),
            "schema_docs":         (3, "Limited; early-stage product"),
            "migration_tools":     (2, "No migration tools"),
            "realtime_streaming":  (4, "Power data streaming via sensors"),
            "historical_access":   (4, "Dashboard-based historical views"),
            "bulk_export":         (3, "Limited bulk capabilities"),
            "open_standards":      (2, "Proprietary sensor approach"),
            "community_ecosystem": (2, "Early-stage ecosystem"),
        },
    },
}


def seed():
    session = init_db()

    # Check if already seeded
    if session.query(Dimension).count() > 0:
        print("Database already seeded. Drop portability.db to re-seed.")
        return

    # Create dimensions
    dims = {}
    for d in DIMENSIONS:
        dim = Dimension(name=d["name"], slug=d["slug"], description=d["description"], weight=d["weight"])
        session.add(dim)
        dims[d["slug"]] = dim
    session.flush()

    # Create platforms and scores
    for slug, data in PLATFORMS.items():
        platform = Platform(
            name=data["name"],
            slug=slug,
            vendor=data["vendor"],
            category=data["category"],
            website=data["website"],
            description=data["description"],
            notes=data.get("notes", ""),
        )
        session.add(platform)
        session.flush()

        for dim_slug, (value, notes) in data["scores"].items():
            score = Score(
                platform_id=platform.id,
                dimension_id=dims[dim_slug].id,
                value=value,
                notes=notes,
            )
            session.add(score)

    session.commit()
    print(f"Seeded {len(PLATFORMS)} platforms with {len(DIMENSIONS)} dimensions.")
    session.close()


if __name__ == "__main__":
    seed()
