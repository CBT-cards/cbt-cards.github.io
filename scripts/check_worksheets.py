#!/usr/bin/env python3
from pathlib import Path
import json
import sys
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
SITE_HOST = "cbt-cards.github.io"


def url_to_local(url):
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme or parsed.netloc:
        if parsed.scheme not in {"http", "https"} or parsed.netloc != SITE_HOST:
            return None
        path = parsed.path
    else:
        path = parsed.path
        if not path.startswith("/"):
            return None
    if path == "/":
        return ROOT / "index.html"
    candidate = ROOT / path.lstrip("/")
    if path.endswith("/"):
        candidate = candidate / "index.html"
    return candidate


def require_local(label, url, errors):
    target = url_to_local(url)
    if target is None:
        errors.append(f"{label}: URL is outside CBT Cards site: {url}")
        return
    if not target.exists():
        errors.append(f"{label}: local target does not exist: {url}")


errors = []
worksheet_path = ROOT / "data/worksheets.json"
catalog_path = ROOT / "data/catalog.json"

try:
    data = json.loads(worksheet_path.read_text(encoding="utf-8"))
except Exception as exc:
    print(f"Worksheet checks failed: cannot parse data/worksheets.json: {exc}")
    raise SystemExit(1)

try:
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
except Exception as exc:
    print(f"Worksheet checks failed: cannot parse data/catalog.json: {exc}")
    raise SystemExit(1)

catalog_by_id = {item.get("id"): item for item in catalog.get("resources", []) if item.get("id")}
worksheets = data.get("worksheets")
if not isinstance(worksheets, list) or not worksheets:
    errors.append("data/worksheets.json: worksheets must be a non-empty list")
    worksheets = []

worksheet_ids = set()
for index, worksheet in enumerate(worksheets, start=1):
    label = f"data/worksheets.json worksheet #{index}"
    required = {
        "id", "locale", "title", "canonical_url", "learning_resource",
        "source", "safety_scope", "privacy_behavior", "fields"
    }
    missing = sorted(required - set(worksheet))
    if missing:
        errors.append(f"{label}: missing fields: {', '.join(missing)}")

    worksheet_id = worksheet.get("id")
    if not worksheet_id:
        continue
    if worksheet_id in worksheet_ids:
        errors.append(f"{label}: duplicate worksheet id {worksheet_id}")
    worksheet_ids.add(worksheet_id)

    catalog_item = catalog_by_id.get(worksheet_id)
    if catalog_item is None:
        errors.append(f"{label}: id {worksheet_id} missing from data/catalog.json")
    else:
        if catalog_item.get("type") != "worksheet":
            errors.append(f"{label}: catalog type must be worksheet for {worksheet_id}")
        if catalog_item.get("url") != worksheet.get("canonical_url"):
            errors.append(f"{label}: catalog URL differs from canonical_url for {worksheet_id}")

    canonical = worksheet.get("canonical_url")
    learning = worksheet.get("learning_resource")
    if canonical:
        require_local(f"{label} canonical_url", canonical, errors)
    if learning:
        require_local(f"{label} learning_resource", learning, errors)

    source = worksheet.get("source", "")
    if not isinstance(source, str) or not source.startswith("https://"):
        errors.append(f"{label}: source must be an https URL")

    privacy = worksheet.get("privacy_behavior", "")
    if "no submit" not in privacy.lower() or "not sent to CBT Cards" not in privacy:
        errors.append(f"{label}: privacy_behavior must explicitly describe no-submit and no-send behavior")

    fields = worksheet.get("fields")
    if not isinstance(fields, list) or not fields:
        errors.append(f"{label}: fields must be a non-empty list")
        continue

    field_ids = set()
    positions = []
    for field_index, field in enumerate(fields, start=1):
        field_label = f"{label} field #{field_index}"
        missing_field = sorted({"id", "position", "label", "prompt"} - set(field))
        if missing_field:
            errors.append(f"{field_label}: missing fields: {', '.join(missing_field)}")
        field_id = field.get("id")
        if field_id in field_ids:
            errors.append(f"{field_label}: duplicate field id {field_id}")
        if field_id:
            field_ids.add(field_id)
        position = field.get("position")
        if not isinstance(position, int) or position < 1:
            errors.append(f"{field_label}: position must be a positive integer")
        else:
            positions.append(position)
        if not str(field.get("label", "")).strip():
            errors.append(f"{field_label}: label must be non-empty")
        if not str(field.get("prompt", "")).strip():
            errors.append(f"{field_label}: prompt must be non-empty")

    expected_positions = list(range(1, len(fields) + 1))
    if positions != expected_positions:
        errors.append(
            f"{label}: field positions must be sequential and ordered {expected_positions}, got {positions}"
        )

for resource_id, item in catalog_by_id.items():
    if item.get("type") == "worksheet" and resource_id not in worksheet_ids:
        errors.append(f"data/catalog.json: worksheet {resource_id} missing from data/worksheets.json")

worksheet_definitions = catalog_by_id.get("worksheet-definitions")
if worksheet_definitions is None:
    errors.append("data/catalog.json: missing worksheet-definitions resource")
elif worksheet_definitions.get("url") != "https://cbt-cards.github.io/data/worksheets.json":
    errors.append("data/catalog.json: worksheet-definitions URL is unexpected")

if errors:
    print("Worksheet checks failed:")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print(f"OK: {len(worksheets)} worksheets; {sum(len(w['fields']) for w in worksheets)} ordered fields; catalog and local targets aligned.")
