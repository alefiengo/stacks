#!/usr/bin/env python3
"""Validate the local skill package without network access or project execution.

This deliberately supports the Markdown, frontmatter and workflow conventions
used by this repository. It is not a general YAML or Markdown parser, and it
is not an agent behavior test. Requires Python 3.11 or later.
"""

import os
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent.parent
PACKAGE = 'skills/stacks'
SKILL = f'{PACKAGE}/SKILL.md'
PACKAGE_RESOURCES = (
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
    'references/stacks/go.md',
    'references/stacks/dotnet.md',
    'templates/stack.md',
    'templates/stack-audit.md',
)
PACKAGE_FILES = ('SKILL.md', 'LICENSE') + PACKAGE_RESOURCES
PACKAGE_ENTRIES = ['LICENSE', 'SKILL.md', 'references', 'templates']
RUNTIME_RESOURCES = tuple(f'{PACKAGE}/{relative}' for relative in PACKAGE_RESOURCES)
MAINTAINER_FILES = (
    'README.md', 'AGENTS.md', 'CONTRIBUTING.md', 'SECURITY.md',
    'CHANGELOG.md', 'LICENSE', '.editorconfig', '.gitattributes',
    '.gitignore', '.github/workflows/validate.yml', '.github/dependabot.yml',
    '.github/PULL_REQUEST_TEMPLATE.md', 'docs/INSTALLATION.md',
    'docs/maintainers/ARCHITECTURE.md',
    'docs/maintainers/RELEASING.md',
    'validation/README.md',
    'validation/check_skill.py', 'validation/test_check_skill.py',
)
REQUIRED_FILES = MAINTAINER_FILES + tuple(f'{PACKAGE}/{relative}' for relative in PACKAGE_FILES)
# Never walked or followed anywhere: version control, caches, credentials, agent state.
ALWAYS_EXCLUDED = {
    '.git', '.hg', '.svn', '__pycache__', '.aws', '.codex', '.agents', '.ssh',
    '.kube', '.gnupg',
}
# Local environments and build output are only expected at the repository root.
ROOT_EXCLUDED = {'.venv', 'venv', 'node_modules', 'vendor', 'dist', 'build'}
TEMP_PREFIXES = ('.trial-', '.checker-negative-', '.check-test-')
MARKDOWN_SUFFIXES = {'.md', '.markdown'}
MAX_RESOURCE_BYTES = 100_000
# Scenario IDs are contiguous from S01; this is the minimum count that must remain.
MIN_SCENARIOS = 48
SCENARIOS = [f'S{number:02}' for number in range(1, MIN_SCENARIOS + 1)]
PORTABILITY_SCENARIOS = [f'U{number:02}' for number in range(1, 9)]
LAYERS = [f'L{number}' for number in range(1, 13)]
LAYER_FILES = (
    f'{PACKAGE}/templates/stack.md', f'{PACKAGE}/templates/stack-audit.md',
    f'{PACKAGE}/references/layers.md',
)
TEMPLATES = (f'{PACKAGE}/templates/stack.md', f'{PACKAGE}/templates/stack-audit.md')
WORKFLOW = '.github/workflows/validate.yml'
DEPENDABOT = '.github/dependabot.yml'
CI_COMMANDS = (
    'python3 -B validation/check_skill.py',
    "python3 -B -m unittest discover -s validation -p 'test_*.py'",
    'git diff --check "$(git hash-object -t tree /dev/null)" HEAD',
)
PLAIN_INDICATORS = set('-?:,[]{}#&*!|>\'"%@`')
FENCE = re.compile(r'^ {0,3}(`{3,}|~{3,})(.*)$')
CODE_SPAN = re.compile(r'(`+)(?!`).+?(?<!`)\1(?!`)')


def secret_filename(name):
    return name == '.env' or (name.startswith('.env.') and name != '.env.example')


def heading_anchor(heading):
    """Return the base GitHub-style anchor for the repository's heading subset."""
    heading = re.sub(r'!?\[([^]]*)\]\([^)]*\)', r'\1', heading)
    heading = heading.strip().lower()
    heading = ''.join(
        char for char in heading
        if char in ' -' or unicodedata.category(char)[0] in 'LMN'
        or unicodedata.category(char) == 'Pc'
    )
    return heading.replace(' ', '-')


def mask_code_spans(line):
    """Replace inline code with spaces so its text is not read as syntax."""
    return CODE_SPAN.sub(lambda match: ' ' * len(match[0]), line)


def visible_markdown(content):
    """Return Markdown views that keep line numbers, and open block locations.

    `rendered` blanks frontmatter, fenced blocks and HTML comments: it is the
    text a reader sees. `linkable` blanks frontmatter and fenced blocks only,
    because agents read raw Markdown and follow links in comments too.
    """
    lines = content.split('\n')
    rendered, linkable = list(lines), list(lines)
    start = 0
    if lines[0].removeprefix('\ufeff') == '---' and '---' in lines[1:]:
        start = lines.index('---', 1) + 1
        for index in range(start):
            rendered[index] = linkable[index] = ''
    fence = comment = None
    for index in range(start, len(lines)):
        line, number = lines[index], index + 1
        match = FENCE.match(line) if comment is None else None
        if fence is not None:
            if (match and match[1][0] == fence[0] and len(match[1]) >= fence[1]
                    and not match[2].strip()):
                fence = None
            rendered[index] = linkable[index] = ''
            continue
        if match and not (match[1][0] == '`' and '`' in match[2]):
            fence = (match[1][0], len(match[1]), number)
            rendered[index] = linkable[index] = ''
            continue
        masked, kept, position = mask_code_spans(line), [], 0
        while position <= len(line):
            if comment is None:
                found = masked.find('<!--', position)
                if found < 0:
                    kept.append(line[position:])
                    break
                kept.append(line[position:found] + ' ' * 4)
                comment, position = number, found + 4
            else:
                found = masked.find('-->', position)
                if found < 0:
                    kept.append(' ' * (len(line) - position))
                    break
                kept.append(' ' * (found + 3 - position))
                comment, position = None, found + 3
        rendered[index] = ''.join(kept)
    return '\n'.join(rendered), '\n'.join(linkable), fence, comment


def headings(lines):
    """Yield (first line index, last line index, text) for ATX and setext headings."""
    for index, line in enumerate(lines):
        atx = re.match(r'^ {0,3}#{1,6}[ \t]+(.*)$', line)
        if atx:
            yield index, index, re.sub(r'(?:^|[ \t]+)#+[ \t]*$', '', atx[1]).strip()
            continue
        previous = lines[index - 1] if index else ''
        if (re.match(r'^ {0,3}(?:=+|-+)[ \t]*$', line) and previous.strip()
                and not re.match(r'^(?: {4}| {0,3}(?:#|[-*+>|]|\d+[.)])|\s*$)', previous)
                and not re.match(r'^ {0,3}(?:=+|-+)[ \t]*$', previous)):
            yield index - 1, index, previous.strip()


def link_destination(text, start):
    """Parse an inline link destination and optional title; return (target, end)."""
    position = start
    while position < len(text) and text[position] in ' \t':
        position += 1
    if text.startswith('<', position):
        end = text.find('>', position)
        if end < 0 or '\n' in text[position:end]:
            return None
        target, position = text[position + 1:end], end + 1
    else:
        depth, begin = 0, position
        while position < len(text):
            char = text[position]
            if char == '\\':
                position += 2
                continue
            if char.isspace():
                break
            if char == '(':
                depth += 1
            elif char == ')':
                if depth == 0:
                    break
                depth -= 1
            position += 1
        target = text[begin:position]
    while position < len(text) and text[position] in ' \t':
        position += 1
    if position < len(text) and text[position] in '"\'(':
        closing = ')' if text[position] == '(' else text[position]
        end = text.find(closing, position + 1)
        if end < 0:
            return None
        position = end + 1
        while position < len(text) and text[position] in ' \t':
            position += 1
    if position >= len(text) or text[position] != ')':
        return None
    return target, position + 1


def normalize_label(label):
    return ' '.join(label.split()).casefold()


def markdown_links(view):
    """Return (link targets, undefined reference labels) found in a Markdown view."""
    lines = [mask_code_spans(line) for line in view.split('\n')]
    definitions, targets = {}, []
    for index, line in enumerate(lines):
        match = re.match(r'^ {0,3}\[([^]^][^]]*)\]:[ \t]*(<[^>]*>|\S+)', line)
        if match:
            definitions[normalize_label(match[1])] = match[2].strip('<>')
            targets.append(match[2].strip('<>'))
            lines[index] = ''
    text = '\n'.join(lines)
    for match in re.finditer(r'\]\(', text):
        parsed = link_destination(text, match.end())
        if parsed is not None:
            targets.append(parsed[0])
    undefined = []
    for match in re.finditer(r'\[([^]\n]*)\]\[([^]\n]*)\]', text):
        label = normalize_label(match[2] or match[1])
        if label not in definitions:
            undefined.append(label)
    return targets, undefined


def yaml_code(line):
    """Return a YAML line without its comment, keeping quoted '#' characters."""
    quote = None
    for index, char in enumerate(line):
        if quote:
            if char == quote:
                quote = None
        elif char in '\'"':
            quote = char
        elif char == '#' and (index == 0 or line[index - 1] in ' \t'):
            return line[:index].rstrip()
    return line.rstrip()


def plain_scalar(value):
    """Accept only plain YAML scalars that cannot change meaning or type."""
    return (bool(value) and value[0] not in PLAIN_INDICATORS
            and ': ' not in value and ' #' not in value and not value.endswith(':'))


class Validator:
    """Collect bounded diagnostics instead of failing on the first defect."""

    def __init__(self, root):
        self.root = Path(root).resolve()
        self.errors = []
        self.checks = 0
        self.docs = {}
        self.metadata = {}
        self.link_paths = {}

    def check(self, condition, message):
        self.checks += 1
        if not condition:
            self.errors.append(message)
        return bool(condition)

    def relative(self, path):
        return Path(os.path.normpath(path)).relative_to(self.root).as_posix()

    def inside(self, path):
        try:
            return path.resolve().is_relative_to(self.root)
        except (OSError, RuntimeError, ValueError):
            return False

    def safe_file(self, path):
        try:
            return self.inside(path) and not path.is_symlink() and path.is_file()
        except (OSError, ValueError):
            return False

    def safe_dir(self, path):
        try:
            return self.inside(path) and not path.is_symlink() and path.is_dir()
        except (OSError, ValueError):
            return False

    def read_resource(self, path):
        """Read a bounded UTF-8 resource without dumping its contents on error.

        Callers report missing or unsafe paths; this method only reads safe files.
        """
        if not self.safe_file(path):
            return None
        relative = self.relative(path)
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
            text = data.decode('utf-8')
        except UnicodeError:
            self.check(False, f'Resource is not valid UTF-8: {relative}')
            return None
        self.check(not text.startswith('\ufeff'), f'Byte order mark in {relative}')
        self.check('\r' not in text, f'Carriage return in {relative}; use LF line endings')
        return text

    def excluded(self, parts):
        return (any(part in ALWAYS_EXCLUDED or secret_filename(part) for part in parts)
                or (bool(parts) and parts[0] in ROOT_EXCLUDED)
                or (len(parts) > 1 and parts[0] == 'validation'
                    and parts[1].startswith(TEMP_PREFIXES)))

    def lexical_parts(self, path):
        """Return path components below the root as written, or None if it escapes."""
        try:
            return Path(os.path.normpath(path)).relative_to(self.root).parts
        except ValueError:
            return None

    def excluded_link(self, path):
        """Check the written path and, when resolvable, its symlink-resolved target."""
        if self.excluded(self.lexical_parts(path)):
            return True
        try:
            return self.excluded(path.resolve().relative_to(self.root).parts)
        except (OSError, RuntimeError, ValueError):
            return False

    def walk(self, top, exclude=True):
        """Yield files below top without following symlinks.

        The excluding walk is the repository discovery: it skips caches,
        credentials and agent state, and reports unreadable or symlinked
        folders. The non-excluding walk lists names only, never opens files,
        and leaves those reports to the discovery walk.
        """
        def unreadable(error):
            if exclude:
                self.check(False, f'Cannot list directory: {self.relative(error.filename)}')

        for directory, folders, files in os.walk(top, onerror=unreadable, followlinks=False):
            parent = Path(directory)
            retained = []
            for folder in sorted(folders):
                path = parent / folder
                if exclude and self.excluded(path.relative_to(self.root).parts):
                    continue
                if not path.is_symlink():
                    retained.append(folder)
                elif exclude:
                    self.check(False, f'Symlinked directory is not distributable: {self.relative(path)}')
            folders[:] = retained
            for filename in sorted(files):
                path = parent / filename
                if not (exclude and self.excluded(path.relative_to(self.root).parts)):
                    yield path

    def discover_markdown(self):
        for path in self.walk(self.root):
            if path.suffix.lower() in MARKDOWN_SUFFIXES:
                yield path

    def inventory(self):
        """Return every repository path this validator reads, for test fixtures."""
        found = set(REQUIRED_FILES)
        found.update(self.relative(path) for path in self.discover_markdown())
        return sorted(found)

    def read_markdown(self):
        for relative in REQUIRED_FILES:
            self.check(self.safe_file(self.root / relative),
                       f'Missing or unsafe resource: {relative}')
        for path in self.discover_markdown():
            relative = self.relative(path)
            if relative in REQUIRED_FILES:
                if not self.safe_file(path):
                    continue
            elif not self.check(self.safe_file(path), f'Unsafe Markdown resource: {relative}'):
                continue
            content = self.read_resource(path)
            if content is None:
                continue
            self.docs[relative] = content
            self.check(content.endswith('\n'), f'Missing final newline: {relative}')
            self.check('\x00' not in content, f'NUL byte in Markdown: {relative}')
            self.check(not any(line.rstrip('\r').rstrip() != line.rstrip('\r')
                               for line in content.split('\n')),
                       f'Trailing whitespace: {relative}')
            rendered, _, fence, comment = visible_markdown(content)
            self.check(fence is None, f'Unclosed fenced block: {relative}')
            self.check(comment is None, f'Unclosed HTML comment: {relative}')
            lines = rendered.split('\n')
            for first, last, _ in headings(lines):
                self.check(first == 0 or not lines[first - 1].strip(),
                           f'Heading needs a preceding blank line: {relative}:{first + 1}')
                self.check(last + 1 == len(lines) or not lines[last + 1].strip(),
                           f'Heading needs a following blank line: {relative}:{first + 1}')

    def frontmatter(self):
        # Encoding defects are reported once by read_resource; parse the rest anyway.
        skill = self.docs.get(SKILL, '').removeprefix('\ufeff').replace('\r\n', '\n')
        match = re.match(r'\A---\n(.*?)\n---\n', skill, re.S)
        if not self.check(match is not None, 'Missing or malformed skill frontmatter'):
            return
        field, block, fields = None, False, {}
        for number, line in enumerate(match[1].split('\n'), 2):
            if block and line.startswith('  '):
                fields[field].append(line.strip())
                continue
            if block and not line.strip():
                self.check(False, f'Blank line in the folded description on line {number}')
                continue
            item = re.fullmatch(r'([a-z]+):(?: (.*))?', line)
            if not self.check(item is not None, f'Unsupported frontmatter syntax on line {number}'):
                block = False
                continue
            field, value = item[1], (item[2] or '').strip()
            block = field == 'description' and value in {'>', '>-'}
            self.check(field not in fields, f'Duplicate frontmatter key: {field}')
            self.check(field in {'name', 'description', 'license'},
                       f'Unsupported frontmatter key on line {number}')
            self.check(block or plain_scalar(value),
                       f'Unsupported frontmatter value on line {number}')
            fields[field] = [] if block else [value]
        self.metadata = {key: ' '.join(values) for key, values in fields.items()}
        name = self.metadata.get('name', '')
        self.check(name == Path(PACKAGE).name, 'Skill name must equal its directory name')
        self.check(1 <= len(self.metadata.get('description', '')) <= 1024,
                   'Description must be 1..1024 characters')
        self.check(self.metadata.get('license') == 'MIT', 'Frontmatter license must be MIT')
        self.check(len(skill.splitlines()) <= 250, 'Core workflow exceeds its 250-line budget')

    def license(self):
        text = self.read_resource(self.root / 'LICENSE')
        if text is not None:
            self.check(text.startswith('MIT License\n'), 'LICENSE must identify the approved MIT terms')
            self.check('Permission is hereby granted' in text and 'THE SOFTWARE IS PROVIDED "AS IS"' in text,
                       'LICENSE must retain the permission and disclaimer text')
        packaged = self.read_resource(self.root / PACKAGE / 'LICENSE')
        if text is not None and packaged is not None:
            self.check(packaged == text, f'{PACKAGE}/LICENSE must be identical to LICENSE')
        self.check(not (self.root / 'LICENSE.proposed').exists(), 'Remove the obsolete adopted license draft')

    def package(self):
        """The installed package must hold only runtime files."""
        package = self.root / PACKAGE
        if not self.safe_dir(package):
            return
        try:
            entries = sorted(os.listdir(package))
        except OSError:
            entries = None
        self.check(entries == PACKAGE_ENTRIES,
                   f'{PACKAGE} must contain only SKILL.md, LICENSE, references/, and templates/')
        expected = {f'{PACKAGE}/{relative}' for relative in PACKAGE_FILES}
        for path in self.walk(package, exclude=False):
            relative = self.relative(path)
            self.check(relative in expected, f'Unexpected file in the installed package: {relative}')

    def case_mismatch(self, path):
        """Report a link whose path exists only with different letter case."""
        current = self.root
        for part in self.lexical_parts(path):
            try:
                names = os.listdir(current)
            except OSError:
                return False
            if part not in names:
                return part.casefold() in {name.casefold() for name in names}
            current = current / part
        return False

    def links(self):
        for relative, content in self.docs.items():
            rendered, linkable, _, _ = visible_markdown(content)
            visible_targets, _ = markdown_links(rendered)
            targets, undefined = markdown_links(linkable)
            for label in undefined:
                self.check(False, f'Undefined link reference in {relative}: {label}')
            visible = set()
            for target in targets:
                path = self.link_path(relative, target)
                if path is not None and target in visible_targets:
                    visible.add(path)
            self.link_paths[relative] = visible

    def link_path(self, relative, target):
        """Validate one link; return the root-relative target path when it is local."""
        target = target.strip()
        try:
            parsed = urlsplit(target)
        except ValueError:
            self.check(False, f'Malformed link in {relative}: {target}')
            return None
        if parsed.scheme in {'https', 'http', 'mailto'}:
            return None
        portable = not parsed.scheme and not parsed.netloc and not parsed.path.startswith('/')
        if not self.check(portable, f'Nonportable link in {relative}: {target}'):
            return None
        decoded_path = unquote(parsed.path)
        if not self.check('\x00' not in decoded_path, f'Invalid character in link path: {relative}'):
            return None
        path = self.root / relative
        if parsed.path:
            path = path.parent / decoded_path
        if not self.check(self.lexical_parts(path) is not None,
                          f'Link escapes root in {relative}: {target}'):
            return None
        if not self.check(not self.excluded_link(path),
                          f'Link targets excluded content in {relative}: {target}'):
            return None
        if not self.check(not self.case_mismatch(path),
                          f'Link path letter case differs from the file in {relative}: {target}'):
            return None
        if self.safe_dir(path) and parsed.path:
            if parsed.fragment:
                self.check(False, f'Anchor target is not validated Markdown in {relative}: {target}')
            return self.relative(path)
        if not self.check(self.safe_file(path), f'Broken or unsafe link in {relative}: {target}'):
            return None
        normalized = self.relative(path)
        if parsed.fragment:
            text = self.docs.get(normalized)
            if text is None:
                self.check(False, f'Anchor target is not validated Markdown in {relative}: {target}')
            else:
                self.check(unquote(parsed.fragment) in self.anchors(text),
                           f'Broken anchor in {relative}: {target}')
        return normalized

    def anchors(self, content):
        rendered, _, _, _ = visible_markdown(content)
        counts, anchors = {}, set()
        for _, _, heading in headings(rendered.split('\n')):
            base = heading_anchor(heading)
            count = counts.get(base, 0)
            anchors.add(base if count == 0 else f'{base}-{count}')
            counts[base] = count + 1
        return anchors

    def rendered(self, relative):
        return visible_markdown(self.docs.get(relative, ''))[0]

    def contracts(self):
        routed = self.link_paths.get(SKILL, set())
        for relative in RUNTIME_RESOURCES:
            self.check(relative in routed,
                       f'Runtime resource is not routed from SKILL.md: {relative}')
        self.check('LICENSE' in self.link_paths.get('README.md', set()),
                   'README must link the active license')
        for relative in LAYER_FILES:
            layers = re.findall(r'^\| (L\d+)\b', self.rendered(relative), re.M)
            self.check(layers == LAYERS, f'Layer inventory must contain L1..L12 exactly once: {relative}')
        for relative in TEMPLATES:
            placeholders = re.findall(r'{{(.*?)}}', self.docs.get(relative, ''))
            self.check(bool(placeholders) and all(re.fullmatch(r'[a-z][a-z0-9_]*', p) for p in placeholders),
                       f'Template placeholders must be descriptive snake_case: {relative}')
        active = '\n'.join(self.docs.get(key, '') for key in (SKILL,) + RUNTIME_RESOURCES).casefold()
        for obsolete in ('every version below was', 'always include some', 'let me decide',
                         'junit 5', 'fastmcp 2.x', 'postgres:17'):
            self.check(obsolete not in active, f'Known contradictory wording returned: {obsolete}')
        scenarios = self.rendered('validation/README.md')
        found = re.findall(r'^\| (S\d+) \|', scenarios, re.M)
        self.check(len(found) >= MIN_SCENARIOS
                   and found == [f'S{number:02}' for number in range(1, len(found) + 1)],
                   f'Acceptance scenarios must be contiguous from S01 and include S01..S{MIN_SCENARIOS:02}')
        self.check(re.findall(r'^\| (U\d+) \|', scenarios, re.M) == PORTABILITY_SCENARIOS,
                   'Portability scenarios must list U01..U08 exactly once and in order')

    def yaml(self, relative):
        """Return (original lines, comment-free lines) of a safe YAML resource."""
        text = self.read_resource(self.root / relative)
        if text is None:
            return None, None
        lines = [line.removesuffix('\r') for line in text.split('\n')]
        return lines, [yaml_code(line) for line in lines]

    def workflow(self):
        lines, code = self.yaml(WORKFLOW)
        if code is None:
            return
        text = '\n'.join(code)
        self.check(not re.search(r'\b(?:pull_request_target|workflow_run)\b', text),
                   'Privileged or cross-workflow triggers are outside the validation policy')
        self.check(re.search(r'^  push:\n    branches: \[main\]\n  pull_request:\n', text, re.M),
                   'Push validation must be limited to main, with pull requests validated')
        self.check(code.count("  cancel-in-progress: ${{ github.event_name == 'pull_request' }}") == 1
                   and text.count('cancel-in-progress:') == 1,
                   'Only pull request runs may cancel validation in progress')
        self.check(re.search(r'^permissions:\n  contents: read\n(?! )', text, re.M)
                   and text.count('permissions:') == 1,
                   'Validation workflow must request only read-only contents permission')
        self.check(not re.search(r'\bsecrets\b|github\.token|GITHUB_TOKEN', text),
                   'Validation workflow must not use secrets or tokens')
        self.check(not re.search(r'^\s*(?:-\s+)?(?:continue-on-error|if):', text, re.M),
                   'Validation steps must not be conditional or allowed to fail')
        uses = [(lines[index], re.sub(r'^\s*(?:-\s+)?uses:\s*', '', line).strip('\'"'))
                for index, line in enumerate(code)
                if re.match(r'^\s*(?:-\s+)?uses:', line)]
        self.check(bool(uses) and all(re.fullmatch(r'[\w.-]+/[\w.-]+(?:/[\w./-]+)?@[0-9a-f]{40}', action)
                                      for _, action in uses),
                   'Workflow actions must use full commit pins')
        self.check(all(re.search(r'\S # v\d+\.\d+\.\d+$', line) for line, _ in uses),
                   'Workflow action pins need a trailing # vX.Y.Z comment')
        checkouts = sum(action.startswith('actions/checkout@') for _, action in uses)
        persisted = re.findall(r'^\s+persist-credentials:\s*(.*)$', text, re.M)
        self.check(checkouts >= 1 and persisted == ['false'] * checkouts,
                   'Checkout must not persist credentials')
        self.check(re.search(r'^    timeout-minutes: [1-9]\d?$', text, re.M),
                   'Validation workflow needs a job timeout')
        self.check(re.search(r'^        python-version: \["3\.11", "3\.x"\]$', text, re.M)
                   and '          python-version: ${{ matrix.python-version }}' in code,
                   'CI must test Python 3.11 and the latest 3.x')
        runs = [re.sub(r'^\s+(?:-\s+)?run:\s*', '', line) for line in code
                if re.match(r'^\s+(?:-\s+)?run:', line)]
        self.check(sorted(runs) == sorted(CI_COMMANDS),
                   'CI must run exactly the maintainer validation commands')

    def dependabot(self):
        _, code = self.yaml(DEPENDABOT)
        if code is None:
            return
        self.check(re.search(r'^  - package-ecosystem: github-actions\n(?:    .*\n)*?'
                             r'    cooldown:\n      default-days: [1-9]\d*$', '\n'.join(code), re.M),
                   'Dependabot must update GitHub Actions after a cooldown')

    def run(self):
        self.read_markdown()
        self.frontmatter()
        self.license()
        self.package()
        self.links()
        self.contracts()
        self.workflow()
        self.dependabot()
        return self


def main(root=ROOT):
    root = Path(root).resolve()
    if Path.cwd().resolve() != root:
        print('Run from the repository root; no files were inspected.', file=sys.stderr)
        return 2
    result = Validator(root).run()
    if result.errors:
        for error in result.errors:
            print(f'FAIL: {error}', file=sys.stderr)
        print(f'{len(result.errors)} failures / {result.checks} checks', file=sys.stderr)
        return 1
    metadata = result.metadata
    print(f"Frontmatter: {metadata['name']}, {metadata['license']}, "
          f"description {len(metadata['description'])} characters")
    print(f'PASS: {result.checks} static checks across {len(result.docs)} Markdown files')
    print('No network, package installation, project execution, or agent behavior certification.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
