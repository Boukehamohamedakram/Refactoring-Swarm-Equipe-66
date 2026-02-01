import json

logs = json.load(open('logs/experiment_data.json'))
tester_logs = [e for e in logs if e.get('agent') == 'Tester']
print(f'✅ Tester agent entries: {len(tester_logs)}')
for entry in tester_logs[:5]:
    output = entry['details'].get('output_response', 'N/A')
    print(f"  - {output[:80]}")

fixer_logs = [e for e in logs if e.get('agent') == 'Fixer']
print(f'\n✅ Fixer agent entries: {len(fixer_logs)}')

judge_logs = [e for e in logs if e.get('agent') == 'Judge']
print(f'✅ Judge agent entries: {len(judge_logs)}')

auditor_logs = [e for e in logs if e.get('agent') == 'Auditor']
print(f'✅ Auditor agent entries: {len(auditor_logs)}')

# Check for feedback loop entries
feedback_entries = [e for e in logs if 'feedback' in str(e.get('details', '')).lower()]
print(f'\n✅ Feedback loop entries: {len(feedback_entries)}')
