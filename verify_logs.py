import json

logs = json.load(open('logs/experiment_data.json'))
required_fields = {'input_prompt', 'output_response'}
valid_count = 0
invalid_entries = []

for i, entry in enumerate(logs):
    details = entry.get('details', {})
    if isinstance(details, dict) and required_fields.issubset(details.keys()):
        valid_count += 1
    else:
        invalid_entries.append((i, type(details), details if isinstance(details, dict) else str(details)[:50]))

print(f"✅ Valid log entries: {valid_count}/{len(logs)}")
if valid_count == len(logs):
    print("✅ All entries have input_prompt and output_response")
else:
    print(f"⚠️ {len(logs) - valid_count} entries missing required fields")
    for idx, typ, detail in invalid_entries[:5]:
        print(f"  Entry {idx}: type={typ}, details={detail}")
