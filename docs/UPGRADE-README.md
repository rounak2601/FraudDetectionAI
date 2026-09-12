# Interview Upgrade Pack

This pack adds a safe, additive compliance and model-monitoring foundation:

- `backend/services/compliance.py` — configurable sanctions matcher, rules evaluator, SAR draft builder, evidence hashing
- `backend/services/drift.py` — dependency-free PSI calculation and drift bands
- `backend/routers/compliance.py` — `/api/compliance/check` and `/api/compliance/sar/{transaction_id}`
- `tests/upgrade-pack/test_compliance_and_drift.py` — focused tests
- `docs/REQUIREMENTS-MATRIX.md` — honest mapping to the company brief
- `docs/INTERVIEW-GUIDE.md` — concise architecture and interview answers

The SAR output is a **draft for analyst review**, not an automatic FinCEN filing. The sanctions matcher is a configurable integration point, not a replacement for an authoritative refreshed SDN dataset.
