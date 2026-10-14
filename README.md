# Manufacturing Data Portability Score

## Status — research prototype, reviewed 2026-10-13

The seeded vendor scores are unverified editorial inputs, not results of completed
platform export tests. They cover the included sample platforms, not every MES/MOM.
Do not use the scores as procurement evidence until each value has dated sources
and a repeatable test. The unchecked launch list below records unfinished work.

Use a local-only development server: `flask --app app run --host 127.0.0.1 --port 5050`.
`python app.py` currently enables debug mode on all interfaces. The SQLite database
persists scores and submitted reports; submissions are not authenticated.

A prototype comparison interface and scoring rubric for manufacturing-data portability.

## Why This Exists

Manufacturing companies get locked into software platforms that hold their production data hostage. Switching costs are astronomical — not because the new system is hard, but because getting your data *out* of the old one is nearly impossible.

The prototype scores a seeded sample on 10 dimensions; the inputs require verification.

## Quick Start

```bash
pip install -r requirements.txt
python seed_data.py    # Initialize database with platform data
flask --app app run --host 127.0.0.1 --port 5050
```

## Scoring Dimensions

| # | Dimension | Weight | What We Measure |
|---|-----------|--------|-----------------|
| 1 | API Access | 15% | REST/GraphQL API availability, rate limits, authentication complexity |
| 2 | Export Formats | 12% | CSV, JSON, XML, Parquet support; schema preservation on export |
| 3 | Data Ownership | 15% | Contract terms — who owns the data? Exit clauses? |
| 4 | Schema Documentation | 8% | Is the data model published? Can you understand what you're exporting? |
| 5 | Migration Tools | 10% | Official export/import tools, migration guides, professional services |
| 6 | Real-time Streaming | 8% | MQTT, Kafka, webhooks — can you tap into live data? |
| 7 | Historical Data Access | 10% | Can you bulk-query historical records? Rate limits? Time restrictions? |
| 8 | Bulk Export | 10% | Full database dump capability, not just record-by-record |
| 9 | Open Standards | 7% | OPC-UA, MTConnect, ISA-95, B2MML compliance |
| 10 | Community/Ecosystem | 5% | Third-party integrations, open-source tools, community knowledge |

## Architecture

- **Backend:** Flask + SQLAlchemy + SQLite
- **Frontend:** Server-rendered templates + Chart.js for radar charts
- **API:** RESTful JSON endpoints for programmatic access
- **Community:** User-submitted experience reports

## API Endpoints

- `GET /api/platforms` — all platforms with overall scores
- `GET /api/platforms/<id>` — single platform with all dimension scores
- `GET /api/compare?ids=1,2,3` — side-by-side comparison
- `POST /api/reports` — submit a user experience report

## Launch Checklist

- [ ] Verify all seed data scores with at least 2 independent sources
- [ ] Legal review of platform descriptions (no defamation risk)
- [ ] Add user authentication for report submissions
- [ ] Rate limiting on API endpoints
- [ ] CAPTCHA or honeypot on submission form
- [ ] SSL/TLS certificate
- [ ] Domain name registration
- [ ] Privacy policy and terms of service
- [ ] Contact/feedback mechanism
- [ ] SEO: meta tags, sitemap, structured data
- [ ] Analytics (privacy-respecting: Plausible or Umami)
- [ ] Backup strategy for SQLite database
- [ ] Load testing (even basic)
- [ ] Content review by manufacturing domain expert
- [ ] Social proof: get 3-5 beta users to submit reports before public launch

## License

TBD

The audit reproduced and repaired a platform-detail HTTP 500 caused by a Flask-SQLAlchemy helper used with plain SQLAlchemy. Two regression tests cover existing and missing platform slugs. Run `python -m pytest test_routes.py -q` after installing pytest.
