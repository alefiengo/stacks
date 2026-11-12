"""Exercise validator failure paths using disposable in-repository fixtures.

Most tests build small synthetic packages from the validator's own file
enumeration, so they do not depend on the wording of the real documents. One
test copies the real repository through the same enumeration and validates it.
"""

import contextlib
import io
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from check_skill import (
    DEPENDABOT, INPUT_CONTRACT, LAYER_FILES, LAYERS, ORCHESTRATION, ORCHESTRATION_INPUT_CONTRACT,
    ORCHESTRATION_SCENARIOS, ORCHESTRATION_SKILL, ORCHESTRATION_STACK_FIELDS, PACKAGES,
    PORTABILITY_SCENARIOS,
    REQUIRED_FILES, ROOT, RUNTIME_RESOURCES, SCAFFOLD, SCAFFOLD_SCENARIOS, SCAFFOLD_SKILL,
    SCENARIOS, SHARED_BLOCKS, SKILLS_DIR, STACK_FIELDS, STACK_TEMPLATE, STACKS, STACKS_SKILL,
    WORKFLOW, Validator, main,
)

COPIED_FROM_REPOSITORY = {WORKFLOW, DEPENDABOT}
SYNTHETIC_LICENSE = (
    'MIT License\n\nCopyright (c) synthetic fixture\n\n'
    'Permission is hereby granted, free of charge, to any person obtaining a copy.\n\n'
    'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.\n'
)
UNPRIVILEGED = getattr(os, 'geteuid', lambda: 0)() != 0
SHARED_NAME, (SHARED_STACKS, SHARED_SCAFFOLD, SHARED_ORCHESTRATION) = next(iter(SHARED_BLOCKS.items()))
SHARED_START = f'<!-- shared:{SHARED_NAME}:start -->'
SHARED_END = f'<!-- shared:{SHARED_NAME}:end -->'
SHARED_TEXT = f'{SHARED_START}\n- Synthetic shared rule.\n{SHARED_END}\n'
SCAFFOLD_TEMPLATE = f'{SCAFFOLD}/templates/scaffold-report.md'
SCAFFOLD_SCENARIO_MESSAGE = ('Scaffold scenarios must be contiguous from SC01 and include '
                             f'SC01..{SCAFFOLD_SCENARIOS[-1]}')
ORCHESTRATION_SCENARIO_MESSAGE = ('Orchestration scenarios must be contiguous from OR01 and include '
                                  f'OR01..{ORCHESTRATION_SCENARIOS[-1]}')
ORCHESTRATION_TEMPLATE = f'{ORCHESTRATION}/templates/agents.md'


def synthetic_skill(name):
    prefix = f'{SKILLS_DIR}/{name}'
    routes = '\n'.join(
        f'- [{Path(relative).stem}]({Path(relative).relative_to(prefix).as_posix()})'
        for relative in RUNTIME_RESOURCES if relative.startswith(f'{prefix}/')
    )
    return (
        f'---\nname: {name}\nlicense: MIT\ndescription: >\n'
        '  Synthetic skill description for validator tests.\n---\n\n'
        f'# {name.title()}\n\n## Routing\n\n{routes}\n'
    )


def synthetic_text(relative):
    """Return minimal valid content for one required or runtime file."""
    parts = Path(relative).parts
    if len(parts) == 3 and parts[0] == SKILLS_DIR and parts[2] == 'SKILL.md':
        return synthetic_skill(parts[1])
    if relative.endswith('LICENSE'):
        return SYNTHETIC_LICENSE
    if relative == 'README.md':
        return '# Fixture\n\nRead the [license](LICENSE).\n'
    if relative == 'validation/README.md':
        rows = '\n'.join(f'| {identifier} | Synthetic |' for identifier in SCENARIOS)
        scaffold = '\n'.join(f'| {identifier} | Synthetic |' for identifier in SCAFFOLD_SCENARIOS)
        orchestration = '\n'.join(f'| {identifier} | Synthetic |'
                                   for identifier in ORCHESTRATION_SCENARIOS)
        hosts = '\n'.join(f'| {identifier} | Synthetic |' for identifier in PORTABILITY_SCENARIOS)
        return (f'# Validation\n\n| ID | Scenario |\n| --- | --- |\n{rows}\n\n'
                f'## Scaffold\n\n| ID | Scenario |\n| --- | --- |\n{scaffold}\n\n'
                f'## Orchestration\n\n| ID | Scenario |\n| --- | --- |\n{orchestration}\n\n'
                f'## Portability\n\n| ID | Host |\n| --- | --- |\n{hosts}\n')
    template = len(parts) > 3 and parts[0] == SKILLS_DIR and parts[2] == 'templates'
    placeholder = '\nProject: {{project_name}}.\n' if template else ''
    if relative in LAYER_FILES:
        rows = '\n'.join(f'| {layer} | Synthetic |' for layer in LAYERS)
        stack_fields = dict.fromkeys(STACK_FIELDS + ORCHESTRATION_STACK_FIELDS)
        fields = '\n\n'.join(stack_fields) + '\n' if relative == STACK_TEMPLATE else ''
        return f'# Layers\n\n| Layer | Choice |\n| --- | --- |\n{rows}\n{placeholder}\n{fields}'
    if relative in (INPUT_CONTRACT, ORCHESTRATION_INPUT_CONTRACT):
        names = STACK_FIELDS if relative == INPUT_CONTRACT else ORCHESTRATION_STACK_FIELDS
        fields = '\n'.join(f'- `{field}`' for field in names)
        return f'# Input contract\n\n{fields}\n'
    if relative in (SHARED_STACKS, SHARED_SCAFFOLD, SHARED_ORCHESTRATION):
        return f'# {Path(relative).stem}\n\n{SHARED_TEXT}'
    if relative.endswith('.md'):
        return f'# {Path(relative).stem}\n\nSynthetic fixture text.\n{placeholder}'
    return 'synthetic fixture\n'


def build_fixture(root):
    for relative in REQUIRED_FILES:
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if relative in COPIED_FROM_REPOSITORY:
            shutil.copyfile(ROOT / relative, destination)
        else:
            destination.write_text(synthetic_text(relative), encoding='utf-8')


class FixtureTestCase(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='.check-test-', dir=ROOT / 'validation')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def errors(self):
        return Validator(self.root).run().errors

    def write(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')

    def append(self, relative, text):
        path = self.root / relative
        path.write_text(path.read_text(encoding='utf-8') + text, encoding='utf-8')

    def replace(self, relative, old, new):
        path = self.root / relative
        text = path.read_text(encoding='utf-8')
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1), encoding='utf-8')

    def assert_invalid(self, message):
        errors = self.errors()
        self.assertTrue(any(message in error for error in errors), errors)
        return errors

    def assert_valid(self):
        self.assertEqual(self.errors(), [])


class RepositoryTests(FixtureTestCase):
    def test_current_package_passes(self):
        inventory = Validator(ROOT).inventory()
        missing = [relative for relative in inventory if not (ROOT / relative).exists()]
        self.assertEqual(missing, [], 'Required repository files are not written yet')
        for relative in inventory:
            source = ROOT / relative
            self.assertTrue(source.is_file() and not source.is_symlink(), relative)
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
        self.assert_valid()


class ValidatorTests(FixtureTestCase):
    def setUp(self):
        super().setUp()
        build_fixture(self.root)

    def restrict(self, path):
        os.chmod(path, 0)
        self.addCleanup(os.chmod, path, 0o755)

    def test_fixture_baseline_passes(self):
        self.assert_valid()

    def test_inventory_includes_discovered_markdown(self):
        self.write('docs/extra.markdown', '# Extra\n')
        inventory = Validator(self.root).inventory()
        self.assertIn('docs/extra.markdown', inventory)
        self.assertTrue(set(REQUIRED_FILES) <= set(inventory))

    # Reading resources

    @unittest.skipUnless(UNPRIVILEGED, 'file permissions do not restrict this user')
    def test_unreadable_resource_is_diagnostic(self):
        self.restrict(self.root / 'docs/INSTALLATION.md')
        self.assert_invalid('Cannot read resource: docs/INSTALLATION.md')

    def test_oversized_markdown_is_not_reopened_for_anchor(self):
        (self.root / 'oversized.md').write_bytes(b'a' * 100_001)
        self.append('README.md', '\n[Large](oversized.md#anchor)\n')
        self.assert_invalid('Resource exceeds the review budget: oversized.md')
        self.assert_invalid('Anchor target is not validated Markdown in README.md')

    def test_large_license_is_bounded(self):
        (self.root / 'LICENSE').write_bytes(b'a' * 100_001)
        self.assert_invalid('Resource exceeds the review budget: LICENSE')

    def test_invalid_utf8_is_diagnostic(self):
        (self.root / 'invalid.md').write_bytes(b'\xff')
        self.assert_invalid('Resource is not valid UTF-8: invalid.md')

    def test_invalid_workflow_encoding_is_diagnostic(self):
        (self.root / WORKFLOW).write_bytes(b'\xff')
        self.assert_invalid(f'Resource is not valid UTF-8: {WORKFLOW}')

    def test_byte_order_mark_has_its_own_message(self):
        path = self.root / STACKS_SKILL
        path.write_bytes(b'\xef\xbb\xbf' + path.read_bytes())
        self.assertEqual(self.errors(), [f'Byte order mark in {STACKS_SKILL}'])

    def test_crlf_has_its_own_message(self):
        for relative in (STACKS_SKILL, WORKFLOW):
            with self.subTest(relative=relative):
                build_fixture(self.root)
                path = self.root / relative
                path.write_bytes(path.read_bytes().replace(b'\n', b'\r\n'))
                self.assertEqual(self.errors(),
                                 [f'Carriage return in {relative}; use LF line endings'])

    # Discovery

    @unittest.skipUnless(UNPRIVILEGED, 'directory permissions do not restrict this user')
    def test_unreadable_directory_is_reported(self):
        self.write('private/guide.md', '# Guide\n')
        self.restrict(self.root / 'private')
        self.assert_invalid('Cannot list directory: private')

    def test_symlinked_directory_is_not_walked(self):
        (self.root / 'linked').symlink_to(self.root / STACKS / 'references', target_is_directory=True)
        self.assert_invalid('Symlinked directory is not distributable: linked')

    def test_markdown_extension_and_nested_build_folder_are_discovered(self):
        self.write('guide.markdown', '# Guide\n\n[Missing](missing.md)\n')
        self.write('docs/build/notes.md', '# Notes\n\n[Missing](missing.md)\n')
        self.assert_invalid('Broken or unsafe link in guide.markdown: missing.md')
        self.assert_invalid('Broken or unsafe link in docs/build/notes.md: missing.md')

    def test_root_build_folder_and_temporary_fixtures_are_skipped(self):
        self.write('build/notes.md', '[Missing](missing.md)\n')
        self.write('validation/.check-test-other/notes.md', '[Missing](missing.md)\n')
        self.assert_valid()

    def test_hidden_markdown_is_discovered(self):
        self.append('.github/PULL_REQUEST_TEMPLATE.md', '\n[Missing](missing.md)\n')
        self.assert_invalid('Broken or unsafe link in .github/PULL_REQUEST_TEMPLATE.md')

    # Markdown hygiene

    def test_missing_runtime_resource_fails(self):
        (self.root / STACKS / 'references/security.md').unlink()
        message = f'Missing or unsafe resource: {STACKS}/references/security.md'
        errors = self.assert_invalid(message)
        self.assertEqual(errors.count(message), 1, errors)

    def test_external_resource_symlink_is_rejected(self):
        path = self.root / STACKS / 'references/security.md'
        path.unlink()
        path.symlink_to('../../../../missing-security.md')
        errors = self.assert_invalid(f'Missing or unsafe resource: {STACKS}/references/security.md')
        self.assertFalse(any('Unsafe Markdown resource' in error for error in errors), errors)

    def test_symlink_loop_is_reported_without_crashing(self):
        (self.root / 'loop.md').symlink_to('loop.md')
        self.append('README.md', '\n[Loop](loop.md)\n')
        self.assert_invalid('Unsafe Markdown resource: loop.md')
        errors = self.assert_invalid('Broken or unsafe link in README.md: loop.md')
        self.assertFalse(any('escapes root' in error for error in errors), errors)

    def test_missing_final_newline_fails(self):
        self.write('README.md', '# Fixture\n\nRead the [license](LICENSE).')
        self.assert_invalid('Missing final newline: README.md')

    def test_nul_byte_fails(self):
        self.append('README.md', '\nNUL \x00 byte\n')
        self.assert_invalid('NUL byte in Markdown: README.md')

    def test_trailing_whitespace_and_form_feed_fail(self):
        for text in ('\nTrailing space \n', '\nForm feed\x0c\n'):
            with self.subTest(text=text):
                build_fixture(self.root)
                self.append('README.md', text)
                self.assert_invalid('Trailing whitespace: README.md')

    def test_unclosed_fence_fails(self):
        self.append('README.md', '\n```text\nunclosed example\n')
        self.assert_invalid('Unclosed fenced block: README.md')

    def test_fence_is_not_closed_by_an_info_string(self):
        self.append('README.md', '\n```text\n```python\n[Example](missing.md)\n')
        self.assert_invalid('Unclosed fenced block: README.md')

    def test_unclosed_html_comment_fails(self):
        self.append('README.md', '\n<!-- unclosed comment\n')
        self.assert_invalid('Unclosed HTML comment: README.md')

    def test_heading_spacing_fails(self):
        self.append('README.md', 'Text before.\n## Invalid heading\n\nText.\n')
        self.assert_invalid('Heading needs a preceding blank line: README.md:5')
        build_fixture(self.root)
        self.append('README.md', '\n## Invalid heading\nMissing blank line.\n')
        self.assert_invalid('Heading needs a following blank line: README.md:5')

    def test_setext_heading_spacing_fails(self):
        self.append('README.md', '\nSetext heading\n--------------\nMissing blank line.\n')
        self.assert_invalid('Heading needs a following blank line: README.md:5')

    def test_headings_in_comments_and_frontmatter_are_ignored(self):
        self.append('README.md', '\n<!--\n# Not a heading\n[Hidden](#not-a-heading)\n-->\n')
        self.assert_invalid('Broken anchor in README.md: #not-a-heading')
        errors = self.errors()
        self.assertFalse(any('Heading needs' in error for error in errors), errors)

    # Frontmatter

    def test_missing_frontmatter_fails(self):
        self.replace(STACKS_SKILL, '---\n', 'not-frontmatter\n')
        self.assert_invalid('Missing or malformed skill frontmatter')

    def test_folded_strip_description_is_accepted(self):
        self.replace(STACKS_SKILL, 'description: >\n', 'description: >-\n')
        validator = Validator(self.root).run()
        self.assertEqual(validator.errors, [])
        self.assertEqual(validator.metadata['stacks']['description'],
                         'Synthetic skill description for validator tests.')

    def test_blank_line_in_folded_description_is_rejected(self):
        self.replace(STACKS_SKILL, '  Synthetic', '\n  Synthetic')
        self.assert_invalid('Blank line in the folded description on line 5')

    def test_frontmatter_errors_do_not_dump_values(self):
        marker = 'synthetic-metadata-value-that-must-not-be-printed'
        self.replace(STACKS_SKILL, 'name: stacks', marker)
        errors = self.assert_invalid('Unsupported frontmatter syntax on line 2')
        self.assertNotIn(marker, '\n'.join(errors))

    def test_duplicate_frontmatter_key_fails(self):
        self.replace(STACKS_SKILL, 'name: stacks\n', 'name: stacks\nname: stacks\n')
        self.assert_invalid(f'Duplicate frontmatter key: name in {STACKS_SKILL}')

    def test_unknown_frontmatter_key_fails(self):
        self.replace(STACKS_SKILL, 'license: MIT\n', 'license: MIT\nversion: one\n')
        self.assert_invalid('Unsupported frontmatter key on line 4')

    def test_unsupported_frontmatter_scalars_fail(self):
        cases = (
            ('name: stacks', 'name: "stacks"'),
            ('license: MIT', 'license: MIT # comment'),
            ('license: MIT', 'license:'),
            ('description: >\n  Synthetic', 'description: Use when: asked\n  Synthetic'),
            ('description: >', 'description: |'),
        )
        for old, new in cases:
            with self.subTest(new=new):
                build_fixture(self.root)
                self.replace(STACKS_SKILL, old, new)
                self.assert_invalid('Unsupported frontmatter')

    def test_skill_name_must_match_directory(self):
        self.replace(STACKS_SKILL, 'name: stacks', 'name: stack')
        self.assert_invalid(f'Skill name must equal its directory name: {STACKS_SKILL}')

    def test_description_length_is_bounded(self):
        self.replace(STACKS_SKILL, '  Synthetic', '  ' + 'a' * 1025 + '\n  Synthetic')
        self.assert_invalid('Description must be 1..1024 characters')

    def test_license_mismatch_fails(self):
        self.replace(STACKS_SKILL, 'license: MIT', 'license: unapproved')
        self.assert_invalid(f'Frontmatter license must be MIT: {STACKS_SKILL}')

    def test_core_workflow_line_budget(self):
        self.append(STACKS_SKILL, '\nLine.\n' * 130)
        self.assert_invalid(f'Core workflow exceeds its 250-line budget: {STACKS_SKILL}')

    # License and package contents

    def test_license_identity_and_terms(self):
        self.replace('LICENSE', 'MIT License', 'Other License')
        self.assert_invalid('LICENSE must identify the approved MIT terms')
        build_fixture(self.root)
        self.replace('LICENSE', 'Permission is hereby granted', 'Permission is withheld')
        self.assert_invalid('LICENSE must retain the permission and disclaimer text')

    def test_packaged_license_must_match_root_license(self):
        self.append(f'{STACKS}/LICENSE', 'Extra term.\n')
        self.assert_invalid(f'{STACKS}/LICENSE must be identical to LICENSE')

    def test_obsolete_license_draft_fails(self):
        self.write('LICENSE.proposed', 'draft\n')
        self.assert_invalid('Remove the obsolete adopted license draft')

    def test_package_rejects_extra_top_level_entries(self):
        (self.root / STACKS / 'scripts').mkdir()
        self.assert_invalid(f'{STACKS} must contain only SKILL.md, LICENSE, references/, and templates/')

    def test_package_rejects_unlisted_files_without_opening_them(self):
        self.write(f'{STACKS}/references/notes.txt', 'maintenance notes\n')
        self.write(f'{STACKS}/templates/.env', 'synthetic test data\n')
        self.assert_invalid(f'Unexpected file in the installed package: {STACKS}/references/notes.txt')
        self.assert_invalid(f'Unexpected file in the installed package: {STACKS}/templates/.env')

    # Links

    def test_new_markdown_is_discovered(self):
        self.write('new-guide.md', '# Guide\n\n[Missing](not-a-real-file.md)\n')
        self.assert_invalid('Broken or unsafe link in new-guide.md: not-a-real-file.md')

    def test_reference_links_are_checked(self):
        self.append('README.md', '\n[Guide][ref]\n\n[ref]: missing-file.md\n')
        self.assert_invalid('Broken or unsafe link in README.md: missing-file.md')

    def test_undefined_reference_fails(self):
        self.append('README.md', '\n[Guide][undefined label]\n')
        self.assert_invalid('Undefined link reference in README.md: undefined label')

    def test_nested_brackets_are_checked(self):
        self.append('README.md', '\n[a [b] c](missing-file.md)\n')
        self.assert_invalid('Broken or unsafe link in README.md: missing-file.md')

    def test_titles_parentheses_references_and_directories_are_valid(self):
        self.write('docs/a(b).md', '# A\n')
        self.append(
            'README.md',
            '\n[Title](LICENSE "License") [Paren](docs/a(b).md) [Angle](<docs/a(b).md>)\n'
            '[Folder](docs/) [Ref][license] [Image](LICENSE)\n\n[license]: LICENSE\n',
        )
        self.assert_valid()

    def test_malformed_link_is_diagnostic(self):
        self.append('README.md', '\n[Bad](http://[::1)\n')
        self.assert_invalid('Malformed link in README.md: http://[::1')

    def test_nonportable_link_fails(self):
        self.append('README.md', '\n[Absolute](/etc/hosts) [File](file:///etc/hosts)\n')
        self.assert_invalid('Nonportable link in README.md: /etc/hosts')
        self.assert_invalid('Nonportable link in README.md: file:///etc/hosts')

    def test_nul_in_link_path_is_diagnostic(self):
        self.append('README.md', '\n[Invalid](%00.md)\n')
        self.assert_invalid('Invalid character in link path: README.md')

    def test_external_path_is_rejected(self):
        self.append('README.md', '\n[Unsafe](../../outside-missing.md)\n')
        self.assert_invalid('Link escapes root in README.md: ../../outside-missing.md')

    def test_encoded_external_path_is_rejected(self):
        self.append('README.md', '\n[Unsafe](%2e%2e/%2e%2e/outside-missing.md)\n')
        self.assert_invalid('Link escapes root in README.md')

    def test_secret_link_is_not_opened(self):
        secret = self.root / '.env'
        secret.write_text('synthetic test data\n', encoding='utf-8')
        self.append('README.md', '\n[Secret](.env#anchor)\n')
        original_open = Path.open

        def guarded_open(path, *args, **kwargs):
            if path == secret:
                raise AssertionError('The validator attempted to open a secret file')
            return original_open(path, *args, **kwargs)

        with patch.object(Path, 'open', guarded_open):
            self.assert_invalid('Link targets excluded content in README.md: .env#anchor')

    def test_excluded_tree_anchor_is_not_read(self):
        self.write('.aws/private.md', '# Private\n')
        (self.root / '.aws/private.md').write_bytes(b'\xff')
        self.append('README.md', '\n[Private](.aws/private.md#anchor)\n')
        errors = self.assert_invalid('Link targets excluded content')
        self.assertFalse(any('UTF-8' in error for error in errors), errors)

    def test_link_case_must_match_file_name(self):
        self.write('docs/Guide.md', '# Guide\n')
        self.append('README.md', '\n[Guide](docs/guide.md)\n')
        self.assert_invalid('Link path letter case differs from the file in README.md: docs/guide.md')

    def test_directory_fragment_is_not_validated_markdown(self):
        self.append('README.md', '\n[Docs](docs/#anchor)\n')
        self.assert_invalid('Anchor target is not validated Markdown in README.md: docs/#anchor')

    def test_binary_fragment_is_rejected_without_decoding(self):
        (self.root / 'image.bin').write_bytes(b'\xff')
        self.append('README.md', '\n[Binary](image.bin#anchor)\n')
        self.assert_invalid('Anchor target is not validated Markdown in README.md: image.bin#anchor')

    def test_long_link_name_is_diagnostic(self):
        self.append('README.md', '\n[Long](' + 'a' * 300 + '.md#anchor)\n')
        self.assert_invalid('Broken or unsafe link in README.md')

    def test_broken_anchor_fails(self):
        self.append('README.md', '\n[Missing](#no-such-heading)\n')
        self.assert_invalid('Broken anchor in README.md: #no-such-heading')

    def test_links_in_comments_are_still_checked(self):
        self.append('README.md', '\n<!-- [Missing](missing-in-comment.md) -->\n')
        self.assert_invalid('Broken or unsafe link in README.md: missing-in-comment.md')

    def test_fenced_and_inline_link_examples_are_not_followed(self):
        self.append(
            'README.md',
            '\n```markdown\n[Example](missing.md)\n```\n\n'
            'Inline example: `[Example](missing.md)` and ``[Example](missing.md)``.\n',
        )
        self.assert_valid()

    def test_heading_anchor_variants_are_valid(self):
        self.append(
            'README.md',
            '\n## Repeated heading\n\nFirst.\n\n## Repeated heading\n\nSecond.\n\n'
            '## Closing hashes ##\n\nText.\n\nSetext title\n============\n\n'
            '## Snake_case and `code` [link](LICENSE)\n\n'
            '[A](#repeated-heading-1) [B](#closing-hashes) [C](#setext-title) '
            '[D](#snake_case-and-code-link)\n',
        )
        self.assert_valid()

    # Repository contracts

    def test_routing_requires_a_visible_link(self):
        link = '](references/security.md)'
        self.replace(STACKS_SKILL, link, '] references/security.md')
        self.append(STACKS_SKILL, f'\n<!-- [Security]{link} -->\n\n```text\n[Security]{link}\n```\n')
        self.assert_invalid(f'Runtime resource is not routed from SKILL.md: {STACKS}/references/security.md')

    def test_readme_license_link_must_be_visible(self):
        self.write('README.md', '# Fixture\n\n<!-- [license](LICENSE) -->\n')
        self.assert_invalid('README must link the active license')

    def test_layer_inventory_is_exact(self):
        relative = f'{STACKS}/templates/stack.md'
        self.replace(relative, '| L12 |', '| Removed |')
        self.assert_invalid(f'Layer inventory must contain L1..L12 exactly once: {relative}')
        build_fixture(self.root)
        self.append(relative, '\n| L12 | Duplicate |\n')
        self.assert_invalid(f'Layer inventory must contain L1..L12 exactly once: {relative}')

    def test_ambiguous_template_placeholder_fails(self):
        relative = f'{STACKS}/templates/stack.md'
        self.append(relative, '\n{{...}}\n')
        self.assert_invalid(f'Template placeholders must be descriptive snake_case: {relative}')

    def test_contradictory_wording_fails(self):
        self.append(f'{STACKS}/references/stacks/java.md', '\nUse JUnit 5.\n')
        self.assert_invalid('Known contradictory wording returned: junit 5')

    def test_acceptance_scenarios_are_contiguous(self):
        message = f'Acceptance scenarios must be contiguous from S01 and include S01..{SCENARIOS[-1]}'
        self.replace('validation/README.md', f'| {SCENARIOS[-1]} |', '| Removed |')
        self.assert_invalid(message)
        build_fixture(self.root)
        self.append('validation/README.md', f'\n| S{len(SCENARIOS) + 2:02} | Gap |\n')
        self.assert_invalid(message)
        build_fixture(self.root)
        self.append('validation/README.md', f'\n| {SCENARIOS[0]} | Duplicate |\n')
        self.assert_invalid(message)

    def test_appended_scenario_passes(self):
        self.append('validation/README.md', f'\n| S{len(SCENARIOS) + 1:02} | Appended |\n')
        self.assert_valid()

    def test_portability_scenarios_are_exact(self):
        self.replace('validation/README.md', '| U08 |', '| Removed |')
        self.assert_invalid('Portability scenarios must list U01..U08 exactly once and in order')

    # Package set and per-package rules

    def test_skills_directory_must_hold_exactly_the_packages(self):
        message = f'{SKILLS_DIR}/ must contain exactly the packages: {", ".join(PACKAGES)}'
        (self.root / SKILLS_DIR / 'draft').mkdir()
        self.assert_invalid(message)
        (self.root / SKILLS_DIR / 'draft').rmdir()
        shutil.rmtree(self.root / SCAFFOLD)
        self.assert_invalid(message)

    def test_missing_scaffold_resource_fails(self):
        (self.root / SCAFFOLD / 'references/verification.md').unlink()
        self.assert_invalid(f'Missing or unsafe resource: {SCAFFOLD}/references/verification.md')

    def test_scaffold_frontmatter_is_validated(self):
        cases = (
            ('---\n', 'not-frontmatter\n', f'Missing or malformed skill frontmatter: {SCAFFOLD_SKILL}'),
            ('name: scaffold', 'name: stacks', f'Skill name must equal its directory name: {SCAFFOLD_SKILL}'),
            ('license: MIT', 'license: unapproved', f'Frontmatter license must be MIT: {SCAFFOLD_SKILL}'),
            ('## Routing', '## Routing\n' + 'Line.\n' * 250,
             f'Core workflow exceeds its 250-line budget: {SCAFFOLD_SKILL}'),
        )
        for old, new, message in cases:
            with self.subTest(message=message):
                build_fixture(self.root)
                self.replace(SCAFFOLD_SKILL, old, new)
                self.assert_invalid(message)

    def test_scaffold_license_must_match_root_license(self):
        self.append(f'{SCAFFOLD}/LICENSE', 'Extra term.\n')
        self.assert_invalid(f'{SCAFFOLD}/LICENSE must be identical to LICENSE')

    def test_scaffold_package_rejects_extra_entries_and_files(self):
        self.write(f'{SCAFFOLD}/README.md', '# Notes\n')
        self.write(f'{SCAFFOLD}/references/notes.txt', 'maintenance notes\n')
        self.assert_invalid(f'{SCAFFOLD} must contain only SKILL.md, LICENSE, references/, and templates/')
        self.assert_invalid(f'Unexpected file in the installed package: {SCAFFOLD}/README.md')
        self.assert_invalid(f'Unexpected file in the installed package: {SCAFFOLD}/references/notes.txt')

    def test_discovered_package_markdown_must_be_routed(self):
        relative = f'{SCAFFOLD}/references/extra.md'
        self.write(relative, '# Extra\n')
        self.assert_invalid(f'Runtime resource is not routed from SKILL.md: {relative}')
        self.append(SCAFFOLD_SKILL, '- [extra](references/extra.md)\n')
        self.assert_valid()

    def test_scaffold_routing_requires_a_visible_link(self):
        link = '](references/execution-safety.md)'
        self.replace(SCAFFOLD_SKILL, link, '] references/execution-safety.md')
        self.append(SCAFFOLD_SKILL, f'\n<!-- [Safety]{link} -->\n')
        self.assert_invalid(
            f'Runtime resource is not routed from SKILL.md: {SCAFFOLD}/references/execution-safety.md')

    def test_scaffold_templates_need_snake_case_placeholders(self):
        message = f'Template placeholders must be descriptive snake_case: {SCAFFOLD_TEMPLATE}'
        self.append(SCAFFOLD_TEMPLATE, '\n{{Report Name}}\n')
        self.assert_invalid(message)
        build_fixture(self.root)
        self.replace(SCAFFOLD_TEMPLATE, '{{project_name}}', 'project name')
        self.assert_invalid(message)
        build_fixture(self.root)
        relative = f'{SCAFFOLD}/templates/extra.md'
        self.write(relative, '# Extra\n')
        self.append(SCAFFOLD_SKILL, '- [extra](templates/extra.md)\n')
        self.assert_invalid(f'Template placeholders must be descriptive snake_case: {relative}')

    def test_contradictory_wording_in_scaffold_fails(self):
        self.append(f'{SCAFFOLD}/references/stacks/python.md', '\nRun postgres:17 locally.\n')
        self.assert_invalid('Known contradictory wording returned: postgres:17')

    # Contracts between packages

    def test_shared_block_must_appear_exactly_once(self):
        for relative in (SHARED_STACKS, SHARED_SCAFFOLD, SHARED_ORCHESTRATION):
            message = f'Shared block {SHARED_NAME} must appear exactly once: {relative}'
            cases = (
                (SHARED_START + '\n', ''),
                (SHARED_END + '\n', ''),
                (SHARED_TEXT, SHARED_TEXT + '\n' + SHARED_TEXT),
                (SHARED_TEXT, SHARED_TEXT.replace(SHARED_START, '@').replace(SHARED_END, SHARED_START)
                 .replace('@', SHARED_END)),
                (SHARED_START, f'  {SHARED_START}'),
            )
            for old, new in cases:
                with self.subTest(relative=relative, new=new):
                    build_fixture(self.root)
                    self.replace(relative, old, new)
                    errors = self.assert_invalid(message)
                    self.assertFalse(any('differs' in error for error in errors), errors)

    def test_shared_block_must_be_identical(self):
        for relative in (SHARED_SCAFFOLD, SHARED_ORCHESTRATION):
            message = f'Shared block {SHARED_NAME} differs between {SHARED_STACKS} and {relative}'
            for new in ('- Synthetic shared rules.', '- Synthetic shared rule. ',
                        '- Synthetic shared rule.\n'):
                with self.subTest(relative=relative, new=new):
                    build_fixture(self.root)
                    self.replace(relative, '- Synthetic shared rule.', new)
                    errors = self.assert_invalid(message)
                    self.assertEqual(len([error for error in errors if 'differs' in error]), 1, errors)

    def test_text_outside_shared_block_may_differ(self):
        self.append(SHARED_SCAFFOLD, '\nScaffold-only guidance.\n')
        self.assert_valid()

    def test_stack_template_keeps_fields_read_by_scaffold(self):
        field = '| Execution status |'
        message = f'Field read by scaffold is missing from {STACK_TEMPLATE}: {field}'
        self.replace(STACK_TEMPLATE, field, '| Run status |')
        self.assert_invalid(message)
        self.append(STACK_TEMPLATE, f'\n<!-- {field} -->\n')
        self.assert_invalid(message)

    def test_input_contract_names_fields_read_by_scaffold(self):
        field = STACK_FIELDS[-1]
        self.replace(INPUT_CONTRACT, field, 'Open decisions')
        self.assert_invalid(f'Field read by scaffold is not named in {INPUT_CONTRACT}: {field}')

    def test_stack_template_keeps_fields_read_by_orchestration(self):
        field = '## 8. Security checklist'
        self.assertNotIn(field, STACK_FIELDS)
        self.replace(STACK_TEMPLATE, field, '## 8. Controls')
        self.assert_invalid(f'Field read by orchestration is missing from {STACK_TEMPLATE}: {field}')

    def test_input_contract_names_fields_read_by_orchestration(self):
        field = ORCHESTRATION_STACK_FIELDS[0]
        self.replace(ORCHESTRATION_INPUT_CONTRACT, field, 'Project profile')
        self.assert_invalid(
            f'Field read by orchestration is not named in {ORCHESTRATION_INPUT_CONTRACT}: {field}')

    def test_orchestration_scenarios_are_contiguous(self):
        last = ORCHESTRATION_SCENARIOS[-1]
        cases = (
            (f'| {last} |', '| Removed |'),
            (f'| {last} | Synthetic |',
             f'| {last} | Synthetic |\n| OR{len(ORCHESTRATION_SCENARIOS) + 2:02} | Gap |'),
            (f'| {last} | Synthetic |',
             f'| {last} | Synthetic |\n| {ORCHESTRATION_SCENARIOS[0]} | Duplicate |'),
        )
        for old, new in cases:
            with self.subTest(new=new):
                build_fixture(self.root)
                self.replace('validation/README.md', old, new)
                errors = self.assert_invalid(ORCHESTRATION_SCENARIO_MESSAGE)
                self.assertFalse(any('Scaffold scenarios' in error for error in errors), errors)

    def test_appended_orchestration_scenario_passes(self):
        self.append('validation/README.md',
                    f'\n| OR{len(ORCHESTRATION_SCENARIOS) + 1:02} | Appended |\n')
        self.assert_valid()

    def test_contract_constants_are_pinned(self):
        self.assertEqual(ORCHESTRATION_STACK_FIELDS, (
            '## 1. Project profile',
            '## 2. Stack summary',
            '| # | Layer | Decision | Version | Status |',
            '## 3. Decisions and rationale',
            '**Authority and implementation state:**',
            '## 5. Local development',
            '| Commands |',
            '| Execution status |',
            '## 6. CI/CD pipeline',
            '## 8. Security checklist',
            '## 10. Open decisions, assumptions and next steps',
        ))
        self.assertEqual(ORCHESTRATION_SCENARIOS, [f'OR{number:02}' for number in range(1, 36)])
        self.assertEqual(
            sorted(relative for relative in RUNTIME_RESOURCES if relative.startswith(f'{ORCHESTRATION}/')),
            sorted(f'{ORCHESTRATION}/{relative}' for relative in (
                'references/input-contract.md', 'references/design.md', 'references/safety.md',
                'references/hosts/claude-code.md', 'references/hosts/codex.md',
                'templates/agents.md', 'templates/materialization-report.md')))

    def test_orchestration_scenario_ids_need_two_digits(self):
        self.append('validation/README.md', '\n| OR100 | Three digits |\n')
        self.assert_invalid(ORCHESTRATION_SCENARIO_MESSAGE)

    def test_missing_orchestration_resource_fails(self):
        relative = f'{ORCHESTRATION}/references/hosts/codex.md'
        (self.root / relative).unlink()
        self.assert_invalid(f'Missing or unsafe resource: {relative}')

    def test_orchestration_frontmatter_and_templates_are_validated(self):
        self.replace(ORCHESTRATION_SKILL, 'name: orchestration', 'name: agents')
        self.assert_invalid(f'Skill name must equal its directory name: {ORCHESTRATION_SKILL}')
        build_fixture(self.root)
        self.append(ORCHESTRATION_TEMPLATE, '\n{{Role Name}}\n')
        self.assert_invalid(
            f'Template placeholders must be descriptive snake_case: {ORCHESTRATION_TEMPLATE}')

    def test_scaffold_scenarios_are_contiguous(self):
        cases = (
            (f'| {SCAFFOLD_SCENARIOS[-1]} |', '| Removed |'),
            (f'| {SCAFFOLD_SCENARIOS[-1]} | Synthetic |',
             f'| {SCAFFOLD_SCENARIOS[-1]} | Synthetic |\n| SC{len(SCAFFOLD_SCENARIOS) + 2:02} | Gap |'),
            (f'| {SCAFFOLD_SCENARIOS[-1]} | Synthetic |',
             f'| {SCAFFOLD_SCENARIOS[-1]} | Synthetic |\n| {SCAFFOLD_SCENARIOS[0]} | Duplicate |'),
        )
        for old, new in cases:
            with self.subTest(new=new):
                build_fixture(self.root)
                self.replace('validation/README.md', old, new)
                errors = self.assert_invalid(SCAFFOLD_SCENARIO_MESSAGE)
                self.assertFalse(any('Acceptance scenarios' in error for error in errors), errors)

    def test_appended_scaffold_scenario_passes(self):
        self.append('validation/README.md', f'\n| SC{len(SCAFFOLD_SCENARIOS) + 1:02} | Appended |\n')
        self.assert_valid()

    # Workflow and Dependabot policy

    def test_privileged_workflow_triggers_fail(self):
        for trigger in ('pull_request_target:', 'workflow_run:'):
            with self.subTest(trigger=trigger):
                build_fixture(self.root)
                self.replace(WORKFLOW, '  workflow_dispatch:\n', f'  workflow_dispatch:\n  {trigger}\n')
                self.assert_invalid('Privileged or cross-workflow triggers')

    def test_push_must_be_limited_to_main(self):
        self.replace(WORKFLOW, '    branches: [main]\n', '')
        self.assert_invalid('Push validation must be limited to main')

    def test_only_pull_requests_cancel_in_progress(self):
        self.replace(WORKFLOW, "${{ github.event_name == 'pull_request' }}", 'true')
        self.assert_invalid('Only pull request runs may cancel validation in progress')

    def test_permissions_must_stay_read_only(self):
        for old, new in (('  contents: read\n', '  contents: write\n'),
                         ('    timeout-minutes:', '    permissions: write-all\n    timeout-minutes:')):
            with self.subTest(new=new):
                build_fixture(self.root)
                self.replace(WORKFLOW, old, new)
                self.assert_invalid('Validation workflow must request only read-only contents permission')

    def test_secrets_and_tokens_fail(self):
        for value in ("${{ secrets['TOKEN'] }}", '${{ github.token }}'):
            with self.subTest(value=value):
                build_fixture(self.root)
                self.replace(WORKFLOW, '        run: python3 -B validation/check_skill.py\n',
                             '        run: python3 -B validation/check_skill.py\n'
                             f'        env:\n          TOKEN: {value}\n')
                self.assert_invalid('Validation workflow must not use secrets or tokens')

    def test_steps_must_not_be_skipped_or_allowed_to_fail(self):
        for key in ('continue-on-error: true', "if: github.event_name == 'push'"):
            with self.subTest(key=key):
                build_fixture(self.root)
                self.replace(WORKFLOW, '        run: python3 -B validation/check_skill.py\n',
                             f'        run: python3 -B validation/check_skill.py\n        {key}\n')
                self.assert_invalid('Validation steps must not be conditional or allowed to fail')

    def test_mutable_action_references_fail(self):
        for old, new in (('actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1', 'actions/checkout@v7'),
                         ('    steps:\n', '    steps:\n      - uses: actions/setup-python@v7 # v7.1.0\n')):
            with self.subTest(new=new):
                build_fixture(self.root)
                self.replace(WORKFLOW, old, new)
                self.assert_invalid('Workflow actions must use full commit pins')

    def test_action_pins_need_version_comments(self):
        self.replace(WORKFLOW, ' # v7.0.1', '')
        self.assert_invalid('Workflow action pins need a trailing # vX.Y.Z comment')

    def test_checkout_must_not_persist_credentials(self):
        for new in ('persist-credentials: true', 'persist-credentials: true # persist-credentials: false'):
            with self.subTest(new=new):
                build_fixture(self.root)
                self.replace(WORKFLOW, 'persist-credentials: false', new)
                self.assert_invalid('Checkout must not persist credentials')

    def test_workflow_needs_a_timeout(self):
        self.replace(WORKFLOW, '    timeout-minutes: 5\n', '')
        self.assert_invalid('Validation workflow needs a job timeout')

    def test_python_matrix_is_exact(self):
        self.replace(WORKFLOW, '"3.11", "3.x"', '"3.12", "3.x"')
        self.assert_invalid('CI must test Python 3.11 and the latest 3.x')

    def test_ci_commands_are_exact(self):
        for new in ('run: echo skip  # validation/check_skill.py',
                    'run: python3 -B validation/check_skill.py || true'):
            with self.subTest(new=new):
                build_fixture(self.root)
                self.replace(WORKFLOW, 'run: python3 -B validation/check_skill.py', new)
                self.assert_invalid('CI must run exactly the maintainer validation commands')

    def test_workflow_comments_names_and_quotes_do_not_mislead(self):
        self.replace(WORKFLOW, 'Check whitespace across the tree',
                     'Check whitespace and overwrite nothing # secrets pull_request_target')
        self.replace(WORKFLOW, 'uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 #',
                     "uses: 'actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1' #")
        self.assert_valid()

    def test_dependabot_needs_a_cooldown(self):
        self.replace(DEPENDABOT, '    cooldown:\n      default-days: 7\n', '')
        self.assert_invalid('Dependabot must update GitHub Actions after a cooldown')

    # Command line

    def run_main(self, *args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with (contextlib.chdir(self.root), contextlib.redirect_stdout(stdout),
              contextlib.redirect_stderr(stderr)):
            status = main(*args)
        return status, stdout.getvalue(), stderr.getvalue()

    def test_main_requires_the_repository_root(self):
        status, stdout, stderr = self.run_main()
        self.assertEqual(status, 2)
        self.assertEqual(stdout, '')
        self.assertEqual(stderr, 'Run from the repository root; no files were inspected.\n')

    def test_main_reports_success(self):
        status, stdout, stderr = self.run_main(self.root)
        self.assertEqual((status, stderr), (0, ''))
        size = len('Synthetic skill description for validator tests.')
        self.assertRegex(stdout, rf'\AFrontmatter: orchestration, MIT, description {size} characters\n'
                                 rf'Frontmatter: scaffold, MIT, description {size} characters\n'
                                 rf'Frontmatter: stacks, MIT, description {size} characters\n'
                                 r'PASS: \d+ static checks across \d+ Markdown files\n'
                                 r'No network, package installation, project execution, '
                                 r'or agent behavior certification\.\n\Z')

    def test_main_reports_failures(self):
        self.replace(STACKS_SKILL, 'license: MIT', 'license: unapproved')
        status, stdout, stderr = self.run_main(self.root)
        self.assertEqual((status, stdout), (1, ''))
        self.assertRegex(stderr, rf'\AFAIL: Frontmatter license must be MIT: {STACKS_SKILL}\n'
                                 r'1 failures / \d+ checks\n\Z')


if __name__ == '__main__':
    unittest.main()
