"""Exercise validator failure paths using disposable in-repository copies."""

import re
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from check_skill import REQUIRED_FILES, ROOT, Validator


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(
            prefix='.check-test-', dir=ROOT / 'validation',
        )
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        for relative in REQUIRED_FILES:
            source = ROOT / relative
            self.assertTrue(source.is_file() and not source.is_symlink(), relative)
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)

    def append(self, relative, text):
        path = self.root / relative
        path.write_text(path.read_text(encoding='utf-8') + text, encoding='utf-8')

    def replace(self, relative, old, new):
        path = self.root / relative
        text = path.read_text(encoding='utf-8')
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1), encoding='utf-8')

    def assert_invalid(self, message):
        errors = Validator(self.root).run().errors
        self.assertTrue(any(message in error for error in errors), errors)

    def test_current_package_passes(self):
        result = Validator(self.root).run()
        self.assertEqual(result.errors, [])

    def test_missing_runtime_resource_fails(self):
        (self.root / 'references/security.md').unlink()
        self.assert_invalid('Missing or unsafe resource: references/security.md')

    def test_new_markdown_is_discovered(self):
        (self.root / 'new-guide.md').write_text(
            '# Guide\n\n[Missing](not-a-real-file.md)\n', encoding='utf-8',
        )
        self.assert_invalid('Broken or unsafe link in new-guide.md')

    def test_hidden_markdown_is_discovered(self):
        self.append('.github/PULL_REQUEST_TEMPLATE.md', '\n[Missing](missing.md)\n')
        self.assert_invalid('Broken or unsafe link in .github/PULL_REQUEST_TEMPLATE.md')

    def test_external_path_is_rejected(self):
        self.append('README.md', '\n[Unsafe](../../outside-missing.md)\n')
        self.assert_invalid('Link escapes root')

    def test_encoded_external_path_is_rejected(self):
        self.append('README.md', '\n[Unsafe](%2e%2e/%2e%2e/outside-missing.md)\n')
        self.assert_invalid('Link escapes root')

    def test_nul_in_link_path_is_diagnostic(self):
        self.append('README.md', '\n[Invalid](%00.md)\n')
        self.assert_invalid('Invalid character in link path')

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
            self.assert_invalid('Link targets excluded content')

    def test_excluded_tree_anchor_is_not_read(self):
        excluded = self.root / '.aws'
        excluded.mkdir()
        (excluded / 'private.md').write_bytes(b'\xff')
        self.append('README.md', '\n[Private](.aws/private.md#anchor)\n')
        self.assert_invalid('Link targets excluded content')

    def test_binary_fragment_is_rejected_without_decoding(self):
        (self.root / 'image.bin').write_bytes(b'\xff')
        self.append('README.md', '\n[Binary](image.bin#anchor)\n')
        self.assert_invalid('Anchor target is not validated Markdown')

    def test_oversized_markdown_is_not_reopened_for_anchor(self):
        (self.root / 'oversized.md').write_bytes(b'a' * 100_001)
        self.append('README.md', '\n[Large](oversized.md#anchor)\n')
        self.assert_invalid('Resource exceeds the review budget')
        self.assert_invalid('Anchor target is not validated Markdown')

    def test_invalid_utf8_is_diagnostic(self):
        (self.root / 'invalid.md').write_bytes(b'\xff')
        self.append('README.md', '\n[Invalid](invalid.md#anchor)\n')
        self.assert_invalid('Resource is not valid UTF-8')

    def test_large_license_is_bounded(self):
        (self.root / 'LICENSE').write_bytes(b'a' * 100_001)
        self.assert_invalid('Resource exceeds the review budget: LICENSE')

    def test_invalid_workflow_encoding_is_diagnostic(self):
        (self.root / '.github/workflows/validate.yml').write_bytes(b'\xff')
        self.assert_invalid('Resource is not valid UTF-8: .github/workflows/validate.yml')

    def test_external_resource_symlink_is_rejected(self):
        path = self.root / 'references/security.md'
        path.unlink()
        path.symlink_to('../../missing-security.md')
        self.assert_invalid('Missing or unsafe resource: references/security.md')

    def test_symlinked_directory_is_not_walked(self):
        # This points to the real in-repository references, outside the fixture.
        # The validator must reject the link without descending into it.
        (self.root / 'linked-resources').symlink_to(ROOT / 'references', target_is_directory=True)
        self.assert_invalid('Symlinked directory is not distributable')

    def test_symlink_loop_is_reported_without_crashing(self):
        (self.root / 'loop.md').symlink_to('loop.md')
        self.assert_invalid('Unsafe Markdown resource: loop.md')

    def test_unclosed_fence_fails(self):
        self.append('README.md', '\n```text\nunclosed example\n')
        self.assert_invalid('Unclosed fenced block')

    def test_heading_spacing_fails(self):
        self.append('README.md', '\n## Invalid heading\nMissing blank line.\n')
        self.assert_invalid('Heading needs a following blank line')

    def test_duplicate_frontmatter_key_fails(self):
        self.replace('SKILL.md', 'name: stacks\n', 'name: stacks\nname: stacks\n')
        self.assert_invalid('Duplicate frontmatter key: name')

    def test_missing_frontmatter_fails(self):
        self.replace('SKILL.md', '---\n', 'not-frontmatter\n')
        self.assert_invalid('Missing or malformed skill frontmatter')

    def test_frontmatter_errors_do_not_dump_values(self):
        marker = 'synthetic-metadata-value-that-must-not-be-printed'
        self.replace('SKILL.md', 'name: stacks', marker)
        errors = Validator(self.root).run().errors
        self.assertTrue(any('Unsupported frontmatter syntax' in error for error in errors))
        self.assertNotIn(marker, '\n'.join(errors))

    def test_license_mismatch_fails(self):
        self.replace('SKILL.md', 'license: MIT', 'license: unapproved')
        self.assert_invalid('Frontmatter license must be MIT')

    def test_missing_layer_fails(self):
        self.replace('templates/stack.md', '| L12 |', '| Removed |')
        self.assert_invalid('Layer inventory must contain L1..L12 exactly once')

    def test_duplicate_layer_fails(self):
        self.append('templates/stack.md', '\n| L12 | Duplicate |\n')
        self.assert_invalid('Layer inventory must contain L1..L12 exactly once')

    def test_ambiguous_template_placeholder_fails(self):
        self.append('templates/stack.md', '\n{{...}}\n')
        self.assert_invalid('Template placeholders must be descriptive snake_case')

    def test_privileged_workflow_trigger_fails(self):
        self.replace('.github/workflows/validate.yml', 'pull_request:', 'pull_request_target:')
        self.assert_invalid('Privileged PR triggers')

    def test_mutable_action_reference_fails(self):
        relative = '.github/workflows/validate.yml'
        workflow = (self.root / relative).read_text(encoding='utf-8')
        match = re.search(r'actions/checkout@[0-9a-f]{40}', workflow)
        self.assertIsNotNone(match)
        self.replace(relative, match[0], 'actions/checkout@main')
        self.assert_invalid('Workflow actions must use full commit pins')

    def test_removed_acceptance_scenario_fails(self):
        self.replace('validation/README.md', '| S25 |', '| Removed |')
        self.assert_invalid('Acceptance scenarios must retain S01..S25 exactly once')
        self.replace('validation/README.md', '| U08 |', '| Removed |')
        self.assert_invalid('Portability scenarios must retain U01..U08 exactly once')

    def test_fenced_and_inline_link_examples_are_not_followed(self):
        self.append(
            'README.md',
            '\n```markdown\n[Example](missing.md)\n```\n\n'
            'Inline example: `[Example](missing.md)`.\n',
        )
        self.assertEqual(Validator(self.root).run().errors, [])

    def test_duplicate_heading_anchors_are_valid(self):
        self.append(
            'README.md',
            '\n## Repeated heading\n\nFirst.\n\n## Repeated heading\n\n'
            '[Second heading](#repeated-heading-1)\n',
        )
        self.assertEqual(Validator(self.root).run().errors, [])


if __name__ == '__main__':
    unittest.main()
