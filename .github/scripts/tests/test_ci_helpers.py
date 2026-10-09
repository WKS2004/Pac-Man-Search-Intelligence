import importlib.util
import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPTS = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


boundary = load("check_source_boundary")
search = load("run_search_checks")


class ScoreCases(unittest.TestCase):
    def test_full_marks_and_dependencies_pass(self):
        output = 'Provisional grades\nQuestion q4: 3/3\nQuestion q7: 4/4\nTotal: 7/7\n'
        self.assertTrue(search.score_result(output, 'q7', 4, 0)['passed'])

    def test_zero_exit_does_not_hide_failed_or_missing_grades(self):
        for output in ('Provisional grades\nQuestion q1: 0/3\n', 'PASS: test case\n',
                       '### Question q1: 3/3 ###\n'):
            self.assertFalse(search.score_result(output, 'q1', 3, 0)['passed'])

    def test_failed_dependency_invalid_maximum_and_timeout_fail(self):
        for output in ('Provisional grades\nQuestion q4: 0/3\nQuestion q7: 4/4\n',
                       'Provisional grades\nQuestion q7: 3/3\n',
                       'Provisional grades\nQuestion q7: 4/4 program timed out\n',
                       'Provisional grades\nQuestion q7: 4/4\nQuestion q7: 4/4\n'):
            self.assertFalse(search.score_result(output, 'q7', 4, 0)['passed'])

    def test_nonzero_exit_fails_even_with_full_marks(self):
        self.assertFalse(search.score_result('Provisional grades\nQuestion q1: 3/3\n', 'q1', 3, 1)['passed'])


class BoundaryCases(unittest.TestCase):
    def test_only_content_modifications_in_existing_allowed_files_pass(self):
        self.assertFalse(boundary.rejected_changes([
            ('M', 'src/search.py', '100644', '100644'),
            ('M', 'src/searchAgents.py', '100644', '100644'),
        ]))

    def test_framework_changes_and_structural_or_mode_changes_are_rejected(self):
        records = [('M', 'src/util.py', '100644', '100644'),
                   ('A', 'src/helper.py', '000000', '100644'),
                   ('D', 'src/search.py', '100644', '000000'),
                   ('M', 'src/search.py', '100644', '100755'),
                   ('T', 'src/searchAgents.py', '100644', '120000')]
        self.assertEqual(len(boundary.rejected_changes(records)), len(records))

    def test_nul_records_preserve_whitespace_and_newlines_in_paths(self):
        records = boundary.parse_changes(b':100644 100644 aaaaaaa bbbbbbb M\0src/a file\n.py\0')
        self.assertEqual(records[0][1], 'src/a file\n.py')
        with self.assertRaises(ValueError):
            boundary.parse_changes(b':broken\0src/util.py\0')


class IsolatedRunnerCases(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='pacman-ci-helper-test-')
        self.root = Path(temporary.name).resolve()
        self.assertTrue(self.root.is_relative_to(Path(tempfile.gettempdir()).resolve()))
        self.addCleanup(temporary.cleanup)
        (self.root / 'src/test_cases/q1').mkdir(parents=True)
        (self.root / 'src/test_cases/q1/CONFIG').write_text('max_points: "3"\n', encoding='utf-8')
        (self.root / 'src/util.py').write_bytes(b'pre-existing USER bytes\r\n')
        self.results = self.root / 'results'
        self.results.mkdir()

    def grader(self, extra='', score=3):
        code = f"{extra}\nprint('Provisional grades\\nQuestion q1: {score}/3\\nTotal: {score}/3')\n"
        (self.root / 'src/autograder.py').write_text(code, encoding='utf-8')

    def test_actual_zero_exit_failed_score_is_rejected(self):
        self.grader(score=0)
        result = search.run_question(self.root, 'q1', self.results, 10)
        self.assertEqual(result['returncode'], 0)
        self.assertFalse(result['passed'])
        self.assertTrue((self.results / 'q1.log').is_file())

    def test_grader_overwrite_is_rejected_and_original_bytes_restored(self):
        self.grader("from pathlib import Path\nPath('util.py').write_text('agent violation')")
        result = search.run_question(self.root, 'q1', self.results, 10)
        self.assertFalse(result['passed'])
        self.assertEqual(result['sourceIntegrity']['restored'], ['src/util.py'])
        self.assertEqual((self.root / 'src/util.py').read_bytes(), b'pre-existing USER bytes\r\n')

    def test_generated_file_is_removed_even_if_all_grades_pass(self):
        self.grader("from pathlib import Path\nPath('generated.txt').write_text('output')")
        result = search.run_question(self.root, 'q1', self.results, 10)
        self.assertFalse(result['passed'])
        self.assertFalse((self.root / 'src/generated.txt').exists())

    def test_log_hard_link_cannot_overwrite_protected_source_or_report_pass(self):
        self.grader()
        source = self.root / 'src/util.py'
        os.link(source, self.results / 'q1.log')
        result = search.run_question(self.root, 'q1', self.results, 10)
        self.assertFalse(result['passed'])
        self.assertIn('outputError', result)
        self.assertEqual(source.read_bytes(), b'pre-existing USER bytes\r\n')

    def test_existing_log_is_preserved_and_run_rejected(self):
        self.grader()
        log = self.results / 'q1.log'
        log.write_text('USER diagnostic evidence', encoding='utf-8')
        result = search.run_question(self.root, 'q1', self.results, 10)
        self.assertFalse(result['passed'])
        self.assertEqual(log.read_text(encoding='utf-8'), 'USER diagnostic evidence')

    def test_diagnostic_side_effects_are_checked_and_restored(self):
        self.grader()
        source = self.root / 'src/util.py'
        def bad_writer(*arguments):
            source.write_bytes(b'accidental diagnostic overwrite')
        with patch.object(search, 'write_report', side_effect=bad_writer):
            result = search.run_question(self.root, 'q1', self.results, 10)
        self.assertFalse(result['passed'])
        self.assertEqual(result['sourceIntegrity']['restored'], ['src/util.py'])
        self.assertEqual(source.read_bytes(), b'pre-existing USER bytes\r\n')

    def test_score_report_alias_cannot_overwrite_source(self):
        source = self.root / 'src/util.py'
        alias = self.results / 'scores.json'
        os.link(source, alias)
        with self.assertRaises(search.OutputSafetyError):
            search.write_report(self.root, alias, '[]')
        self.assertEqual(source.read_bytes(), b'pre-existing USER bytes\r\n')

    def test_step_summary_hard_link_cannot_append_to_source(self):
        source = self.root / 'src/util.py'
        alias = self.results / 'step-summary.md'
        os.link(source, alias)
        with self.assertRaises(search.OutputSafetyError):
            search.append_step_summary(self.root, alias, 'CI summary')
        self.assertEqual(source.read_bytes(), b'pre-existing USER bytes\r\n')

    def test_regular_step_summary_preserves_prior_step_content(self):
        summary = self.results / 'step-summary.md'
        summary.write_text('Prior step\n', encoding='utf-8')
        search.append_step_summary(self.root, summary, 'Search grades\n')
        self.assertEqual(summary.read_text(encoding='utf-8'), 'Prior step\nSearch grades\n')

    def test_existing_reports_are_rejected_before_running_questions(self):
        (self.results / 'scores.json').write_text('USER evidence', encoding='utf-8')
        with patch.object(search, 'ROOT', self.root), patch.object(search, 'run_question') as run:
            with patch.object(sys, 'argv', ['runner', '--results-dir', str(self.results)]):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(search.main(), 1)
                    run.assert_not_called()
        self.assertEqual((self.results / 'scores.json').read_text(encoding='utf-8'), 'USER evidence')

    def test_complete_runner_writes_seven_results_and_step_summary(self):
        for question in search.QUESTIONS:
            directory = self.root / 'src/test_cases' / question
            directory.mkdir(exist_ok=True)
            (directory / 'CONFIG').write_text('max_points: "3"\n', encoding='utf-8')
        (self.root / 'src/autograder.py').write_text(
            "import sys\nquestion = sys.argv[sys.argv.index('-q') + 1]\n"
            "print(f'Provisional grades\\nQuestion {question}: 3/3\\nTotal: 3/3')\n",
            encoding='utf-8',
        )
        summary = self.root / 'github-step-summary.md'
        with patch.object(search, 'ROOT', self.root), patch.dict(os.environ, {'GITHUB_STEP_SUMMARY': str(summary)}):
            with patch.object(sys, 'argv', ['runner', '--results-dir', str(self.results)]):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(search.main(), 0)
        records = json.loads((self.results / 'scores.json').read_text(encoding='utf-8'))
        self.assertEqual([record['question'] for record in records], list(search.QUESTIONS))
        self.assertTrue(all(record['passed'] for record in records))
        self.assertTrue(all((self.results / f'{question}.log').is_file() for question in search.QUESTIONS))
        self.assertEqual(summary.read_text(encoding='utf-8'), (self.results / 'summary.md').read_text(encoding='utf-8'))
        self.assertEqual((self.root / 'src/util.py').read_bytes(), b'pre-existing USER bytes\r\n')

    def test_timeout_reports_failure_and_checks_source(self):
        self.grader('import time\ntime.sleep(2)')
        result = search.run_question(self.root, 'q1', self.results, 1)
        self.assertFalse(result['passed'])
        self.assertFalse(result['sourceIntegrity']['unresolved'])

    def test_unverifiable_source_halts_the_gate(self):
        self.grader()
        with patch.object(search.GUARD, 'capture', side_effect=ValueError('untrusted baseline')):
            with self.assertRaises(search.SourceIntegrityError):
                search.run_question(self.root, 'q1', self.results, 10)

    def test_summary_output_cannot_overwrite_source(self):
        self.grader()
        path = self.root / 'src/util.py'
        with patch.object(search, 'ROOT', self.root), patch.dict(os.environ, {'GITHUB_STEP_SUMMARY': str(path)}):
            with patch.object(sys, 'argv', ['runner', '--results-dir', str(self.results)]):
                with patch.object(search, 'run_question') as run, contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(search.main(), 1)
                    run.assert_not_called()
        self.assertEqual(path.read_bytes(), b'pre-existing USER bytes\r\n')


if __name__ == '__main__':
    unittest.main()
