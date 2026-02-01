import json

logs = json.load(open('logs/experiment_data.json'))

# Find directory validation entries
dir_validation = [e for e in logs if 'directory' in str(e.get('details', '')).lower()]
print(f'✅ Directory validation entries: {len(dir_validation)}')
for entry in dir_validation:
    output = entry['details'].get('output_response', 'N/A')
    print(f"  - {output[:80]}")

# Find security entries
security_entries = [e for e in logs if 'security' in str(e.get('details', '')).lower() or 'security' in str(e.get('action', '')).lower()]
print(f'\n✅ Security-related entries: {len(security_entries)}')
for entry in security_entries[:5]:
    output = entry['details'].get('output_response', 'N/A')
    print(f"  - {output[:80]}")
