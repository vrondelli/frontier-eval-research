"""Local first-answer sealing and fixed hot-account reveal; no timestamp authority."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

from evaluate import ROOT, canonical, digest, grade

TASK = ROOT / 'input' / 'E1.md'


def source_hash():
    return hashlib.sha256(TASK.read_bytes()).hexdigest()


def seal(state):
    return {**state, 'state_sha256': digest(state)}


def load_state(path, phase):
    state = json.loads(Path(path).read_text(encoding='utf-8'))
    binding = state.pop('state_sha256')
    if digest(state) != binding or state['task_sha256'] != source_hash():
        raise ValueError('state or task source binding mismatch')
    if state['phase'] != phase:
        raise ValueError('incorrect stage')
    return state


def write_new(path, data):
    with Path(path).open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(data, indent=2, allow_nan=False) + '\n')


def start():
    facts = '\n\n'.join(line for line in TASK.read_text(encoding='utf-8').splitlines()
                         if line.startswith(tuple(f'F{i}.' for i in range(1, 6))))
    view = ('# E1: Concurrent allowance and duplicate identity\n\n'
            'You are evolving a transfer-admission service. Explain the design and implement it.\n\n'
            + facts + '\n\nReturn a JSON object with task_id:"E1", code (the complete Service '
            'source string), and explanation. Explain atomic boundaries, identity scope, '
            'unknown-outcome replay and deployment tradeoffs. Alternatively submit '
            'alternative_format:true, alternative:"...", explanation:"..." for independent '
            'review without an executable pass. A later fixed evidence reveal will ask you '
            'to revisit the design. See input/README.md for runtime constraints.\n')
    return seal({'schema_version': 'e1-staged/v1', 'phase': 'initial',
                 'task_sha256': source_hash(), 'view': view})


def reveal(state_path, answer_path):
    state = load_state(state_path, 'initial')
    answer = json.loads(Path(answer_path).read_text(encoding='utf-8'))
    if not isinstance(answer, dict) or answer.get('task_id') != 'E1':
        raise ValueError('first answer must be an E1 JSON object')
    return seal({'schema_version': 'e1-staged/v1', 'phase': 'revealed',
                 'task_sha256': state['task_sha256'], 'parent_sha256': digest(state),
                 'initial_state': state, 'initial_answer': answer,
                 'initial_answer_sha256': digest(answer),
                 'view': TASK.read_text(encoding='utf-8')})


def finish(state_path, answer_path):
    state = load_state(state_path, 'revealed')
    initial = state['initial_state']
    if (state['initial_answer_sha256'] != digest(state['initial_answer'])
            or state['parent_sha256'] != digest(initial)
            or initial != {k: v for k, v in start().items() if k != 'state_sha256'}):
        raise ValueError('first-answer lineage mismatch')
    answer = json.loads(Path(answer_path).read_text(encoding='utf-8'))
    report = grade(answer)
    report['staged_evidence'] = {'initial_answer': state['initial_answer'],
                                 'initial_answer_sha256': state['initial_answer_sha256'],
                                 'revealed_state_sha256': digest(state),
                                 'task_sha256': state['task_sha256']}
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    initial = sub.add_parser('start')
    initial.add_argument('output')
    for name in ('reveal', 'finish'):
        step = sub.add_parser(name)
        step.add_argument('state')
        step.add_argument('answer')
        step.add_argument('output')
    args = parser.parse_args()
    try:
        if args.command == 'start':
            result = start()
        elif args.command == 'reveal':
            result = reveal(args.state, args.answer)
        else:
            result = finish(args.state, args.answer)
        write_new(args.output, result)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'error': str(exc)}), file=sys.stderr)
        return 2
    return 0 if args.command != 'finish' or result['formal_status'] == 'pass' else 2


if __name__ == '__main__':
    sys.exit(main())
