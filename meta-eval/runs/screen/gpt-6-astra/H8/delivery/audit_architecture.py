"""Audit the supplied evidence packet without reading historical workspaces.

Usage: python audit_architecture.py [--input input] [--manifest MANIFEST.json]
                                   [--output audit]
Exit 1 means an accounting/integrity inconsistency; evidence limitations are
reported separately and never upgraded to successful workspace verification.
"""
import argparse
import collections
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(base, packet_manifest):
    issues, observations, rows = [], [], []
    counts = collections.Counter()

    def issue(code, path, detail):
        issues.append(dict(code=code, path=str(path), detail=detail))

    def read(path):
        def pairs(items):
            result = {}
            for key, value in items:
                if key in result:
                    issue('duplicate_json_key', path, key)
                result[key] = value
            return result
        try:
            return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=pairs)
        except (OSError, ValueError) as exc:
            issue('unreadable_json', path, str(exc))
            return {}

    def duplicates(values, code, path):
        for key, n in collections.Counter(values).items():
            if n > 1:
                issue(code, path, dict(value=key, occurrences=n))

    def safe_relative(value):
        p = PurePosixPath(value)
        return bool(value) and not p.is_absolute() and '..' not in p.parts and '\\' not in value and ':' not in value

    files = sorted(p for p in base.rglob('*') if p.is_file())
    docs = {p: read(p) for p in files if p.suffix == '.json'}
    counts['input_files'] = len(files)
    counts['json_files_parsed'] = len(docs)
    packet = read(packet_manifest)
    listed = []
    for item in packet.get('files', []):
        rel = item['path']
        if not rel.startswith('input/'):
            continue
        rel = rel[len('input/'):]
        listed.append(rel)
        if not safe_relative(rel):
            issue('unsafe_packet_path', rel, 'Not a safe relative path')
            continue
        p = base / rel
        if not p.is_file():
            issue('missing_packet_file', rel, 'Listed in MANIFEST.json')
        elif p.stat().st_size != item['bytes'] or digest(p) != item['sha256']:
            issue('packet_hash_or_size_mismatch', rel, item)
        else:
            counts['packet_files_verified'] += 1
    duplicates(listed, 'duplicate_packet_path', packet_manifest)
    for rel in sorted({p.relative_to(base).as_posix() for p in files} - set(listed)):
        issue('unlisted_packet_file', rel, 'Not in MANIFEST.json files')
    for binding in packet.get('source_bindings', []):
        destination = binding['destination']
        if '/input/' not in destination:
            continue
        rel = destination.split('/input/', 1)[1]
        if not safe_relative(rel):
            issue('unsafe_binding_path', rel, destination)
            continue
        p = base / rel
        if not p.is_file() or p.stat().st_size != binding['bytes'] or digest(p) != binding['sha256']:
            issue('source_binding_mismatch', rel, destination)
        else:
            counts['source_bindings_verified'] += 1

    episodes = {p.parent.relative_to(base).as_posix(): d for p, d in docs.items() if p.name == 'episode.json'}
    aggregates = [(p, d) for p, d in docs.items() if p.name.startswith('NATIVE-')]
    mapped = collections.defaultdict(list)
    aggregate_summary = []
    for p, doc in aggregates:
        results = doc.get('results', [])
        aggregate_summary.append(dict(path=p.relative_to(base).as_posix(), results=len(results), statuses=dict(collections.Counter(r.get('status') for r in results))))
        duplicates([r['id'] for r in results], 'duplicate_aggregate_id', p)
        if 'registered' in doc and doc['registered'] != len(results):
            issue('registration_count_mismatch', p, doc['registered'])
        for index, record in enumerate(results):
            if 'native' in record:
                nested = [('', record)]
            else:
                nested = [(k, record[k]) for k in ('repair', 'maintenance') if record.get(k)]
                if not record.get('maintenance'):
                    issue('missing_maintenance', p, record['id'])
                assignment = record.get('assignment', {})
                maintenance = record.get('maintenance') or {}
                if assignment.get('sequence') != [s.get('task') for s in maintenance.get('stages', [])]:
                    issue('sequence_mismatch', p, record['id'])
                if assignment.get('policy') == 'repair' and not record.get('repair'):
                    issue('missing_repair', p, record['id'])
                if record.get('blocked_stages') or record.get('errors'):
                    observations.append(dict(code='chain_exception', path=str(p), id=record['id'], blocked=record.get('blocked_stages'), errors=record.get('errors')))
            for component, episode in nested:
                root = ('r3/' if p.parent == base / 'r3' else '') + 'runs/' + episode['id']
                source = f'{p.relative_to(base).as_posix()}#/results/{index}' + ('/' + component if component else '')
                mapped[root].append(source)
                if root not in episodes:
                    issue('missing_episode', root, source)
                elif episodes[root] != episode:
                    issue('aggregate_episode_mismatch', root, source)
                else:
                    counts['aggregate_episode_matches'] += 1
    for root, sources in mapped.items():
        if len(sources) > 1:
            issue('episode_multiple_aggregate_references', root, sources)
    for root in sorted(set(episodes) - set(mapped)):
        observations.append(dict(code='standalone_episode', path=root + '/episode.json', detail='No NATIVE aggregate reference supplied; retained in coverage.'))

    layout_doc = docs.get(base / 'snapshot-layout.json', {})
    layout_items = layout_doc.get('source_layout', [])
    duplicates([x['root'] for x in layout_items], 'duplicate_layout_root', 'snapshot-layout.json')
    layout = {x['root']: x for x in layout_items}
    manifests = {p.parent.relative_to(base).as_posix(): (p, d) for p, d in docs.items() if p.name == 'manifest.json'}
    expected_roots = []
    threads, turns = [], []
    groups = collections.defaultdict(collections.Counter)
    statuses = collections.Counter()
    for root, episode in sorted(episodes.items()):
        assignment = episode.get('assignment', {})
        if root.startswith('r3/'):
            group = 'R3 ' + assignment.get('partition', 'unknown')
        elif episode['id'].startswith('R2-'):
            group = 'R2 maintenance' if 'stages' in episode else 'R2 repair'
        else:
            group = assignment.get('family', 'Compatibility policy')
        groups[group]['sessions'] += 1
        threads.append(episode.get('thread_id'))
        if episode.get('id') != PurePosixPath(root).name:
            issue('episode_directory_id_mismatch', root, episode.get('id'))
        if assignment.get('id', episode['id']) != episode['id']:
            issue('assignment_id_mismatch', root, assignment.get('id'))
        if not episode.get('actor_stopped'):
            issue('actor_not_stopped', root, episode.get('actor_stopped'))
        try:
            if datetime.fromisoformat(episode['finished_utc']) < datetime.fromisoformat(episode['started_utc']):
                issue('negative_session_duration', root, 'finish precedes start')
        except (KeyError, ValueError) as exc:
            issue('invalid_session_timestamp', root, str(exc))
        if episode.get('human_validation') == 'pending':
            counts['sessions_human_validation_pending'] += 1
        stages = episode.get('stages', [episode])
        if not stages:
            issue('empty_session', root, 'No stages')
        duplicates([s.get('id') for s in stages], 'duplicate_stage_id', root)
        previous_usage = {}
        for stage in stages:
            native = stage.get('native', {})
            turn_id = native.get('turn_id')
            turns.append(turn_id)
            if native.get('thread_id') != episode.get('thread_id'):
                issue('thread_mismatch', root, turn_id)
            candidates = [root + '/final'] if 'stages' not in episode else [root + '/stages/' + stage['id'], root + '/stages/' + stage['id'] + '/snapshot']
            matches = [r for r in candidates if r in manifests]
            if len(matches) != 1:
                issue('snapshot_cardinality', root, dict(stage=stage['id'], expected=1, found=matches, candidates=candidates))
            snapshot = matches[0] if len(matches) == 1 else candidates[0]
            expected_roots.append(snapshot)
            if snapshot not in layout:
                issue('snapshot_not_in_layout', snapshot, stage['id'])
            if 'stages' in episode and stage.get('snapshot_status') != 'completed':
                issue('snapshot_status_incomplete', snapshot, stage.get('snapshot_status'))
            status = native.get('status', 'missing')
            statuses[status] += 1
            if status != 'completed':
                observations.append(dict(code='noncompleted_turn', path=root + '/episode.json', turn_id=turn_id, episode_status=episode.get('status'), native_status=status, generation_status=native.get('generation_status'), error=native.get('error'), errors=episode.get('errors'), answer_sha256=native.get('answer_sha256')))
            elif native.get('generation_status') != 'completed' or native.get('native_status') != 'completed':
                issue('native_status_disagreement', root, turn_id)
            for key in ('prompt_sha256', 'answer_sha256'):
                value = native.get(key, '')
                if len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
                    issue('invalid_native_digest', root, key)
            event_range = native.get('server_event_range', [])
            if len(event_range) != 2 or event_range[0] > event_range[1]:
                issue('invalid_event_range', root, event_range)
            usage = native.get('cumulative_native_usage', {})
            if usage.get('totalTokens') != usage.get('inputTokens', 0) + usage.get('outputTokens', 0):
                issue('token_total_mismatch', root, turn_id)
            if any(usage.get(k, 0) < v for k, v in previous_usage.items()):
                issue('cumulative_usage_decreased', root, turn_id)
            previous_usage = usage
            groups[group]['turns'] += 1
            groups[group]['manifests'] += len(matches)
            groups[group]['completed_turns'] += status == 'completed'
            rows.append(dict(group=group, episode=root + '/episode.json', episode_id=episode['id'], stage_id=stage['id'] if 'stages' in episode else '', thread_id=episode.get('thread_id'), turn_id=turn_id, native_status=status, snapshot_root=snapshot, manifest_present=len(matches) == 1, layout_present=snapshot in layout, aggregate_sources=';'.join(mapped.get(root, []))))
        resource_usage = episode.get('resources', {}).get('cumulative_native_usage', episode.get('cumulative_native_usage'))
        if resource_usage is not None and resource_usage != previous_usage:
            issue('resource_usage_mismatch', root, 'Episode resource usage differs from final native usage')
    duplicates(threads, 'duplicate_session_thread', 'episodes')
    duplicates(turns, 'duplicate_turn', 'episodes')
    if None in threads or None in turns:
        issue('missing_native_identity', 'episodes', 'Missing thread or turn ID')
    duplicates(expected_roots, 'snapshot_reused_by_turns', 'episodes')
    for root in sorted(set(manifests) - set(expected_roots)):
        issue('orphan_snapshot_manifest', root, 'No matching session turn')
    for root in sorted(set(layout) - set(manifests)):
        issue('layout_manifest_missing', root, 'No manifest file')
    for root in sorted(set(manifests) - set(layout)):
        issue('manifest_not_in_layout', root, 'No layout declaration')
    for root, (path, manifest) in manifests.items():
        if not manifest:
            issue('empty_snapshot_manifest', root, 'No file entries')
        declaration = layout.get(root, {})
        if digest(path) != declaration.get('manifest_source_sha256'):
            issue('layout_manifest_hash_mismatch', root, 'Manifest differs from declared source digest')
        else:
            counts['layout_manifest_hashes_verified'] += 1
        counts['declared_source_workspaces'] += declaration.get('workspace_exists') is True
        counts['local_workspace_directories'] += (path.parent / 'workspace').is_dir()
        for rel, meta in manifest.items():
            counts['manifest_file_entries'] += 1
            if not safe_relative(rel):
                issue('unsafe_snapshot_entry', root, rel)
            if not isinstance(meta, dict) or not isinstance(meta.get('bytes'), int) or meta['bytes'] < 0 or len(meta.get('sha256', '')) != 64 or any(c not in '0123456789abcdef' for c in meta.get('sha256', '')):
                issue('invalid_snapshot_entry', root, rel)
            else:
                counts['declared_workspace_bytes_across_snapshots'] += meta['bytes']
    counts.update(sessions=len(episodes), turns=len(rows), unique_threads=len(set(threads)), unique_turns=len(set(turns)), snapshots=len(manifests), layout_entries=len(layout_items), aggregate_files=len(aggregates), aggregate_referenced_sessions=len(mapped))
    if len(manifests) != len(rows) or set(manifests) != set(expected_roots):
        issue('turn_snapshot_coverage_mismatch', 'input', dict(turns=len(rows), manifests=len(manifests)))
    return dict(schema='architecture-evidence-audit/v1', generated_utc=datetime.now(timezone.utc).isoformat(), accounting_status='FAIL' if issues else 'PASS', workspace_byte_integrity='NOT_VERIFIABLE: workspace bodies intentionally omitted', source_notice=layout_doc.get('reconstruction_notice'), counts=dict(counts), groups={k: dict(v) for k, v in sorted(groups.items())}, native_statuses=dict(statuses), aggregate_summary=aggregate_summary, inconsistencies=issues, observations=observations, coverage=rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=Path('input'))
    parser.add_argument('--manifest', type=Path, default=Path('MANIFEST.json'))
    parser.add_argument('--output', type=Path, default=Path('audit'))
    args = parser.parse_args()
    result = audit(args.input, args.manifest)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / 'audit.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    with (args.output / 'coverage.csv').open('w', newline='', encoding='utf-8') as handle:
        if result['coverage']:
            writer = csv.DictWriter(handle, fieldnames=list(result['coverage'][0]))
            writer.writeheader()
            writer.writerows(result['coverage'])
    print(json.dumps({k: v for k, v in result.items() if k != 'coverage'}, indent=2))
    return bool(result['inconsistencies'])


if __name__ == '__main__':
    raise SystemExit(main())
