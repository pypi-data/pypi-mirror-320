# ruff: noqa: S603 = allow check_output with arbitrary cmdline

import json
from pathlib import Path
from shlex import split
from subprocess import check_output

import cyclopts


IMG = 'makukha/multipython:unsafe'
BAKEFILE = 'tests/docker-bake.hcl'
REPORTS_DIR = Path('docs/testreport')

POS = '✅'
NEG = '🚫'
COLSP = ' '

app = cyclopts.App()


@app.command
def gen_reports() -> None:
    """
    Generate test reports.
    """
    # get source data
    data = json.loads(check_output(split(f'docker buildx bake -f {BAKEFILE} --print')))
    tags = check_output(
        split(f'docker run --rm {IMG} py ls --tag'),
        text=True,
    ).splitlines()

    # generate reports
    T = 'tox>=3,<4'
    V = 'virtualenv>=20'
    for bake_group, venv_pin, desc, name in (
        ('tox3', '>=20', f'`{T}`, `{V}`', 'tox3_venv'),
        ('tox3', '>=20,<20.27', f'`{T}`, `{V},<20.27`', 'tox3_venv27'),
        ('tox3', '>=20,<20.22', f'`{T}`, `{V},<20.22`', 'tox3_venv22'),
    ):
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        write_report(data, tags, bake_group, venv_pin, desc, name, skip=('py20',))


def write_report(
    data: dict,
    tags: list[str],
    bake_group: str,
    venv_pin: str,
    desc: str,
    name: str,
    skip: tuple[str, ...],
) -> None:
    def host_tag_results(args: dict) -> tuple[str, list[str]]:
        marks = [
            *((t, 'P') for t in args['TAGS_PASSING'].split()),
            *((t, 'F') for t in set(args['TAGS_FAILING'].split()) - set(skip)),
        ]
        marks.sort(key=lambda tm: tags.index(tm[0]))
        return (args['PYTHON_TAG'], ''.join(tm[1] for tm in marks))

    targets = data['group'][bake_group]['targets']
    args = [data['target'][t]['args'] for t in targets]
    table = [host_tag_results(a) for a in args if a['VIRTUALENV_PIN'] == venv_pin]
    table.sort(key=lambda row: tags.index(row[0]))
    results = dict(desc=desc, target_tags=tags, host_tag_results=dict(table))
    with (REPORTS_DIR / f'{name}.json').open('wt') as f:
        json.dump(results, f, indent=2)


@app.command
def pretty_report(name: str) -> None:
    """
    Print report in compact terminal-based format.

    Parameters
    ----------
    name: str
        Test report name.
    """
    ALPHA = 'ABCDEFGHIJKLMNOPQRSTUVW'

    with (REPORTS_DIR / f'{name}.json').open() as f:
        data = json.load(f)
    row_title = 'HOST'
    col_title = 'TARGETS'
    tags = data['target_tags']

    if len(tags) > len(ALPHA):
        raise RuntimeError('Too many tags')

    width = max(len(row_title), max(len(v) for v in tags))

    print(f'{" " * width}    {col_title}')
    print(f'{row_title: >{width}}    {COLSP.join(ALPHA[: len(tags)])}')
    for i, tag in enumerate(tags):
        res = data['host_tag_results'].get(tag)
        marks = (
            [{'P': POS, 'F': NEG}[x] for x in res]
            if res
            else COLSP.join('.' * len(tags))
        )
        print(f'{tag: >{width}}  {ALPHA[i]} {"".join(marks)}')


if __name__ == '__main__':
    app()
