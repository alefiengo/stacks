#!/usr/bin/env python3
"""Validate the local skill package without network access or project execution.

This deliberately supports the Markdown and frontmatter conventions used by
this repository. It is not a general YAML parser or an agent behavior test.
"""

import os
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent.parent
RUNTIME_RESOURCES = (
    'references/compatibility.md',
    'references/interview.md',
    'references/layers.md',
    'references/decision-criteria.md',
    'references/deployment.md',
    'references/security.md',
    'references/audit.md',
    'references/stacks/python.md',
    'references/stacks/typescript.md',
    'references/stacks/java.md',
    'templates/stack.md',
    'templates/stack-audit.md',
)
REQUIRED_FILES = (
    'SKILL.md', 'README.md', 'AGENTS.md', 'CONTRIBUTING.md', 'SECURITY.md',
    'CHANGELOG.md', 'LICENSE', '.editorconfig', '.gitattributes',
    '.gitignore', '.github/workflows/validate.yml', '.github/dependabot.yml',
    '.github/PULL_REQUEST_TEMPLATE.md', 'docs/maintainers/ARCHITECTURE.md',
    'docs/maintainers/RELEASING.md', 'docs/maintainers/LICENSING.md',
    'validation/README.md',
    'validation/check_skill.py', 'validation/test_check_skill.py',
) + RUNTIME_RESOURCES
EXCLUDED_DIRS = {
    '.git', '.hg', '.svn', '.venv', 'venv', 'node_modules', 'vendor',
    'dist', 'build', '__pycache__', '.aws', '.codex', '.agents', '.ssh',
    '.kube', '.gnupg',
}
TEMP_PREFIXES = ('.trial-', '.checker-negative-', '.check-test-')
MAX_RESOURCE_BYTES = 100_000


def secret_filename(name):
    return name == '.env' or (name.startswith('.env.') and name != '.env.example')


def heading_anchor(heading):
    """Return the base GFM-style anchor for the repository's heading subset."""
    heading = re.sub(r'\[([^]]+)\]\([^)]+\)', r'\1', heading)
    heading = heading.lower().strip()
    heading = ''.join(
        char for char in heading
        if char in ' -_' or unicodedata.category(char)[0] in 'LN'
    )
    return heading.replace(' ', '-')


def visible_markdown(content):
    """Blank fenced blocks, keeping line numbers; report an unclosed fence."""
    fence = None
    visible = []
    for number, line in enumerate(content.splitlines(), 1):
        match = re.match(r'^\s{0,3}(`{3,}|~{3,})', line)
        if match:
            marker = match[1]
            if fence is None:
                fence = (marker[0], len(marker), number)
            elif marker[0] == fence[0] and len(marker) >= fence[1]:
                fence = None
            visible.append('')
        else:
            visible.append(line if fence is None else '')
    return '\n'.join(visible), fence


class Validator:
    """Collect bounded diagnostics instead of failing on the first defect."""

    def __init__(self, root):
        self.root = Path(root).resolve()
        self.errors = []
        self.checks = 0
        self.docs = {}
        self.metadata = {}

    def check(self, condition, message):
        self.checks += 1
        if not condition:
            self.errors.append(message)
        return bool(condition)

    def inside(self, path):
        try:
            return path.resolve().is_relative_to(self.root)
        except (OSError, RuntimeError, ValueError):
            return False

    def safe_file(self, path):
        return self.inside(path) and not path.is_symlink() and path.is_file()

    def read_resource(self, path):
        """Read a bounded UTF-8 resource without dumping its contents on error."""
        relative = path.relative_to(self.root).as_posix()
        if not self.check(self.safe_file(path), f'Missing or unsafe resource: {relative}'):
            return None
        try:
            with path.open('rb') as stream:
                data = stream.read(MAX_RESOURCE_BYTES + 1)
        except (OSError, ValueError):
            self.check(False, f'Cannot read resource: {relative}')
            return None
        if not self.check(len(data) <= MAX_RESOURCE_BYTES,
                          f'Resource exceeds the review budget: {relative}'):
            return None
        try:
            return data.decode('utf-8')
        except UnicodeError:
            self.check(False, f'Resource is not valid UTF-8: {relative}')
            return None

    def excluded_link(self, path):
        parts = path.resolve().relative_to(self.root).parts
        return (any(part in EXCLUDED_DIRS or secret_filename(part) for part in parts)
                or any(part.startswith(TEMP_PREFIXES) for part in parts))

    def discover_markdown(self):
        for directory, folders, files in os.walk(self.root, followlinks=False):
            parent = Path(directory)
            retained = []
            for folder in sorted(folders):
                if folder in EXCLUDED_DIRS:
                    continue
                if parent == self.root / 'validation' and folder.startswith(TEMP_PREFIXES):
                    continue
                path = parent / folder
                if self.check(not path.is_symlink(),
                              f'Symlinked directory is not distributable: {path.relative_to(self.root)}'):
                    retained.append(folder)
            folders[:] = retained
            for filename in sorted(files):
                path = parent / filename
                if path.suffix.lower() == '.md' and not secret_filename(filename):
                    yield path

    def read_markdown(self):
        for relative in REQUIRED_FILES:
            self.check(self.safe_file(self.root / relative),
                       f'Missing or unsafe resource: {relative}')
        for path in self.discover_markdown():
            relative = path.relative_to(self.root).as_posix()
            if not self.check(self.safe_file(path), f'Unsafe Markdown resource: {relative}'):
                continue
            content = self.read_resource(path)
            if content is None:
                continue
            self.docs[relative] = content
            self.check(content.endswith('\n'), f'Missing final newline: {relative}')
            self.check('\x00' not in content, f'NUL byte in Markdown: {relative}')
            self.check(not any(line.rstrip() != line for line in content.splitlines()),
                       f'Trailing whitespace: {relative}')
            visible, fence = visible_markdown(content)
            self.check(fence is None, f'Unclosed fenced block: {relative}')
            lines = visible.splitlines()
            for index, line in enumerate(lines):
                if not re.match(r'^#{1,6}\s+', line):
                    continue
                self.check(index == 0 or not lines[index - 1].strip(),
                           f'Heading needs a preceding blank line: {relative}:{index + 1}')
                self.check(index + 1 == len(lines) or not lines[index + 1].strip(),
                           f'Heading needs a following blank line: {relative}:{index + 1}')

    def frontmatter(self):
        skill = self.docs.get('SKILL.md', '')
        match = re.match(r'\A---\n(.*?)\n---\n', skill, re.S)
        if not self.check(match is not None, 'Missing or malformed skill frontmatter'):
            return
        field = None
        fields = {}
        for number, line in enumerate(match[1].splitlines(), 2):
            if line.startswith('  ') and field == 'description':
                fields[field].append(line.strip())
                continue
            item = re.fullmatch(r'([a-z]+): (.+)', line)
            if not self.check(item is not None, f'Unsupported frontmatter syntax on line {number}'):
                continue
            field, value = item.groups()
            self.check(field not in fields, f'Duplicate frontmatter key: {field}')
            self.check(field in {'name', 'description', 'license'},
                       f'Unsupported frontmatter key on line {number}')
            fields[field] = [] if field == 'description' and value == '>' else [value]
        self.metadata = {key: ' '.join(values) for key, values in fields.items()}
        name = self.metadata.get('name', '')
        self.check(bool(re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name)) and len(name) <= 64,
                   'Skill name must use lowercase hyphenated text of at most 64 characters')
        self.check(name == 'stacks', 'Skill name changed unexpectedly')
        self.check(1 <= len(self.metadata.get('description', '')) <= 1024,
                   'Description must be 1..1024 characters')
        self.check(self.metadata.get('license') == 'MIT', 'Frontmatter license must be MIT')
        self.check(len(skill.splitlines()) <= 250, 'Core workflow exceeds its 250-line budget')
        license_path = self.root / 'LICENSE'
        if self.safe_file(license_path):
            text = self.read_resource(license_path)
            if text is not None:
                self.check(text.startswith('MIT License\n'), 'LICENSE must identify the approved MIT terms')
                self.check('Permission is hereby granted' in text and 'THE SOFTWARE IS PROVIDED "AS IS"' in text,
                           'LICENSE must retain the permission and disclaimer text')
        self.check('](LICENSE)' in self.docs.get('README.md', ''), 'README must link the active license')
        self.check(not (self.root / 'LICENSE.proposed').exists(), 'Remove the obsolete adopted license draft')

    def anchors(self, content):
        visible, _ = visible_markdown(content)
        counts = {}
        anchors = set()
        for heading in re.findall(r'^#{1,6}\s+(.+)$', visible, re.M):
            base = heading_anchor(heading)
            count = counts.get(base, 0)
            anchors.add(base if count == 0 else f'{base}-{count}')
            counts[base] = count + 1
        return anchors

    def links(self):
        for relative, content in self.docs.items():
            visible, _ = visible_markdown(content)
            # Inline code can show example link syntax without creating a link.
            visible = re.sub(r'`[^`\n]+`', '', visible)
            for target in re.findall(r'\[[^]\n]+\]\(([^)\n]+)\)', visible):
                target = target.strip().strip('<>')
                try:
                    parsed = urlsplit(target)
                except ValueError:
                    self.check(False, f'Malformed link in {relative}: {target}')
                    continue
                if parsed.scheme in {'https', 'http', 'mailto'}:
                    continue
                portable = not parsed.scheme and not parsed.netloc and not parsed.path.startswith('/')
                if not self.check(portable, f'Nonportable link in {relative}: {target}'):
                    continue
                decoded_path = unquote(parsed.path)
                if not self.check('\x00' not in decoded_path,
                                  f'Invalid character in link path: {relative}'):
                    continue
                path = self.root / relative
                if parsed.path:
                    path = path.parent / decoded_path
                if not self.check(self.inside(path), f'Link escapes root in {relative}: {target}'):
                    continue
                if not self.check(not self.excluded_link(path),
                                  f'Link targets excluded content in {relative}: {target}'):
                    continue
                if not self.check(self.safe_file(path), f'Broken or unsafe link in {relative}: {target}'):
                    continue
                if parsed.fragment:
                    normalized = path.resolve().relative_to(self.root).as_posix()
                    text = self.docs.get(normalized)
                    if text is None:
                        self.check(False, f'Anchor target is not validated Markdown in {relative}: {target}')
                        continue
                    self.check(unquote(parsed.fragment) in self.anchors(text),
                               f'Broken anchor in {relative}: {target}')

    def contracts(self):
        skill = self.docs.get('SKILL.md', '')
        for relative in RUNTIME_RESOURCES:
            self.check(f']({relative})' in skill,
                       f'Runtime resource is not routed from SKILL.md: {relative}')
        for relative in ('templates/stack.md', 'templates/stack-audit.md', 'references/layers.md'):
            layers = re.findall(r'^\| (L\d+)\b', self.docs.get(relative, ''), re.M)
            self.check(layers == [f'L{number}' for number in range(1, 13)],
                       f'Layer inventory must contain L1..L12 exactly once: {relative}')
        for relative in ('templates/stack.md', 'templates/stack-audit.md'):
            placeholders = re.findall(r'{{(.*?)}}', self.docs.get(relative, ''))
            self.check(bool(placeholders) and all(re.fullmatch(r'[a-z][a-z0-9_]*', p) for p in placeholders),
                       f'Template placeholders must be descriptive snake_case: {relative}')
        active = '\n'.join(self.docs.get(key, '') for key in ('SKILL.md',) + RUNTIME_RESOURCES).casefold()
        for obsolete in ('every version below was', 'always include some', 'let me decide',
                         'junit 5', 'fastmcp 2.x', 'postgres:17'):
            self.check(obsolete not in active, f'Known contradictory wording returned: {obsolete}')
        scenarios = re.findall(r'^\| (S\d+) \|', self.docs.get('validation/README.md', ''), re.M)
        self.check(scenarios == [f'S{number:02}' for number in range(1, 26)],
                   'Acceptance scenarios must retain S01..S25 exactly once')
        portability = re.findall(r'^\| (U\d+) \|', self.docs.get('validation/README.md', ''), re.M)
        self.check(portability == [f'U{number:02}' for number in range(1, 9)],
                   'Portability scenarios must retain U01..U08 exactly once')

    def workflow(self):
        path = self.root / '.github/workflows/validate.yml'
        if not self.safe_file(path):
            return
        workflow = self.read_resource(path)
        if workflow is None:
            return
        self.check('pull_request_target' not in workflow, 'Privileged PR triggers are outside the validation policy')
        self.check(bool(re.search(r'^permissions:\n  contents: read\n', workflow, re.M)),
                   'Validation workflow must request read-only contents permission')
        self.check('write' not in workflow and 'secrets.' not in workflow,
                   'Validation workflow must not request write access or named secrets')
        self.check('persist-credentials: false' in workflow, 'Checkout must not persist credentials')
        actions = re.findall(r'^\s+uses:\s+(\S+)', workflow, re.M)
        self.check(bool(actions) and all(re.fullmatch(r'[^@\s]+@[0-9a-f]{40}', action) for action in actions),
                   'Workflow actions must use full commit pins')
        self.check('timeout-minutes:' in workflow, 'Validation workflow needs a timeout')
        self.check('validation/check_skill.py' in workflow and 'unittest discover' in workflow,
                   'CI must run the validator and its negative tests')

    def run(self):
        self.read_markdown()
        self.frontmatter()
        self.links()
        self.contracts()
        self.workflow()
        return self


def main():
    if Path.cwd().resolve() != ROOT:
        print('Run from the repository root; no files were inspected.', file=sys.stderr)
        return 2
    result = Validator(ROOT).run()
    if result.errors:
        for error in result.errors:
            print(f'FAIL: {error}', file=sys.stderr)
        print(f'{len(result.errors)} failures / {result.checks} checks', file=sys.stderr)
        return 1
    description_size = len(result.metadata['description'])
    print(f'Frontmatter: stacks, MIT, description {description_size} characters')
    print(f'PASS: {result.checks} static checks across {len(result.docs)} Markdown files')
    print('No network, package installation, project execution, or agent behavior certification.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
