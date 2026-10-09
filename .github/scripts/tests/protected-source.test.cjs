const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');

// Run the exact trusted inline policy; every GitHub request is mocked.
const workflow = fs.readFileSync(path.resolve(__dirname, '../../workflows/protected-source.yml'), 'utf8');
const block = workflow.split(/          script: \|\r?\n/)[1];
assert.ok(block);
const script = block.split(/\r?\n/).map(line => line.replace(/^ {12}/, '')).join('\n');
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
const enforce = new AsyncFunction('context', 'github', 'core', script);
const policy = JSON.parse(fs.readFileSync(path.resolve(__dirname, '../../policies/source-policy.json'), 'utf8'));
const blob = (file, sha = 'original', mode = '100644') => ({ path: file, sha, mode, type: 'blob' });
const original = [blob('search.py'), blob('searchAgents.py'), blob('util.py'),
  { path: 'test_cases', sha: 'directory', mode: '040000', type: 'tree' }, blob('test_cases/CONFIG')];

async function run(options = {}) {
  const closed = [], failed = [], warnings = [], requests = [];
  const pr = { state: 'open', base: { ref: 'main', sha: 'base' },
    head: { sha: 'head', repo: { full_name: 'someone/fork' } }, ...options.pr };
  let refreshes = 0;
  const github = { rest: {
    pulls: {
      get: async args => {
        assert.deepEqual(args, { owner: 'owner', repo: 'pacman', pull_number: 7 });
        return { data: refreshes++ === 0 ? pr : (options.current || pr) };
      },
      update: async args => {
        closed.push(args);
        if (options.closeError) throw new Error(options.closeError);
        return { data: { state: 'closed' } };
      }
    },
    git: {
      getCommit: async args => {
        requests.push(args);
        assert.equal(args.owner, 'owner');
        assert.equal(args.repo, 'pacman');
        if (options.readError) throw new Error(options.readError);
        assert.ok([policy.baselineCommit, 'head'].includes(args.commit_sha));
        return { data: { tree: { sha: args.commit_sha === 'head' ? 'head-root' : 'baseline-root' } } };
      },
      getTree: async args => {
        requests.push(args);
        assert.equal(args.owner, 'owner');
        assert.equal(args.repo, 'pacman');
        const head = args.tree_sha.startsWith('head-');
        if (args.tree_sha.endsWith('-root')) {
          assert.equal(args.recursive, undefined);
          return { data: { truncated: !!options.rootTruncated, tree: head && options.noSrc ? [] :
            [{ path: 'src', mode: '040000', type: 'tree', sha: head ? 'head-src' : 'baseline-src',
              ...(head ? options.srcEntry : {}) }] } };
        }
        assert.equal(args.recursive, '1');
        return { data: { truncated: !!options.sourceTruncated,
          tree: head ? (options.actual || original) : (options.expected || original) } };
      }
    }
  } };
  const core = { setFailed: message => failed.push(message), warning: message => warnings.push(message), info: () => {} };
  await enforce({ repo: { owner: 'owner', repo: 'pacman' }, payload: { pull_request: { number: 7 } } }, github, core);
  return { closed, failed, warnings, requests };
}

const changed = (file, replacement) => original.map(entry => entry.path === file ? { ...entry, ...replacement } : entry);
const assertClosed = result => {
  assert.deepEqual(result.closed, [{ owner: 'owner', repo: 'pacman', pull_number: 7, state: 'closed' }]);
  assert.match(result.failed[0], /Automatically closed/);
};

test('workflow uses trusted baseline, main PR events and only necessary privileges', () => {
  assert.ok(script.includes(`const baseline = '${policy.baselineCommit}'`));
  for (const file of policy.editableFiles) assert.ok(script.includes(`'${file}'`));
  assert.match(workflow, /branches: \[main\]/);
  for (const event of ['opened', 'reopened', 'synchronize', 'edited', 'ready_for_review']) assert.ok(workflow.includes(event));
  assert.match(workflow, /contents: read/);
  assert.match(workflow, /pull-requests: write/);
  assert.doesNotMatch(workflow, /uses: actions\/checkout|contents: write/);
  assert.doesNotMatch(script, /\$\{\{ github\.event\..*\}\}/);
});

test('unchanged source or changes outside source leave the PR open', async () => {
  const result = await run();
  assert.deepEqual(result.closed, []);
  assert.deepEqual(result.failed, []);
});

test('content edits to both existing allowed files leave the PR open', async () => {
  const actual = original.map(entry => policy.editableFiles.includes(`src/${entry.path}`) ? { ...entry, sha: 'new' } : entry);
  const result = await run({ actual });
  assert.deepEqual(result.closed, []);
  assert.deepEqual(result.failed, []);
});

test('protected top-level and nested content edits automatically close fork PRs in the base repository', async () => {
  for (const file of ['util.py', 'test_cases/CONFIG']) assertClosed(await run({ actual: changed(file, { sha: 'new' }) }));
});

test('new source files automatically close the PR', async () => {
  assertClosed(await run({ actual: [...original, blob('nested/new.py')] }));
});

test('deletions reject both protected and normally editable files', async () => {
  for (const file of ['util.py', 'search.py']) assertClosed(await run({ actual: original.filter(entry => entry.path !== file) }));
});

test('renames including source moves out of src or into src close the PR', async () => {
  assertClosed(await run({ actual: changed('search.py', { path: 'renamed.py' }) }));
  assertClosed(await run({ actual: original.filter(entry => entry.path !== 'util.py') }));
  assertClosed(await run({ actual: [...original, blob('moved-from-root.md')] }));
});

test('chmod, symlink and submodule replacements are rejected even for allowed files', async () => {
  for (const replacement of [{ mode: '100755' }, { mode: '120000' }, { mode: '160000', type: 'commit' }]) {
    assertClosed(await run({ actual: changed('search.py', replacement) }));
  }
});

test('removing or replacing the entire src directory closes the PR', async () => {
  assertClosed(await run({ noSrc: true }));
  assertClosed(await run({ srcEntry: { type: 'blob', mode: '120000' } }));
});

test('directory hashes may change when only an allowed file changes', async () => {
  const actual = changed('search.py', { sha: 'new' }).map(entry => entry.type === 'tree' ? { ...entry, sha: 'new-tree' } : entry);
  assert.deepEqual((await run({ actual })).failed, []);
});

test('source inventory does not rely on the PR file-list 3000-file limit', async () => {
  const additions = Array.from({ length: 3001 }, (_, index) => blob(`new-${index}.py`));
  assertClosed(await run({ actual: [...original, ...additions] }));
});

test('closed and non-main PRs are skipped without reading source or closing anything', async () => {
  for (const pr of [{ state: 'closed' }, { base: { ref: 'dev', sha: 'base' } }]) {
    const result = await run({ pr });
    assert.deepEqual(result.closed, []);
    assert.deepEqual(result.requests, []);
    assert.deepEqual(result.failed, []);
  }
});

test('corrected, retargeted, merged or otherwise stale PRs are not closed', async () => {
  for (const current of [
    { state: 'open', head: { sha: 'corrected' }, base: { ref: 'main', sha: 'base' } },
    { state: 'open', head: { sha: 'head' }, base: { ref: 'dev', sha: 'base' } },
    { state: 'closed', head: { sha: 'head' }, base: { ref: 'main', sha: 'base' } },
    { state: 'open', head: { sha: 'head' }, base: { ref: 'main', sha: 'updated-base' } }
  ]) {
    const result = await run({ actual: changed('util.py', { sha: 'new' }), current });
    assert.deepEqual(result.closed, []);
    assert.match(result.failed[0], /changed during inspection/);
  }
});

test('truncated trees and read errors fail without approving or guessing a closure', async () => {
  for (const options of [{ rootTruncated: true }, { sourceTruncated: true }, { readError: 'GitHub unavailable' }]) {
    const result = await run(options);
    assert.deepEqual(result.closed, []);
    assert.match(result.failed[0], /could not finish/);
  }
});

test('invalid baseline fails without closing a PR', async () => {
  const result = await run({ expected: original.filter(entry => entry.path !== 'search.py') });
  assert.deepEqual(result.closed, []);
  assert.match(result.failed[0], /trusted baseline/);
});

test('GitHub closure refusal is reported and never treated as a successful closure', async () => {
  const result = await run({ actual: changed('util.py', { sha: 'new' }), closeError: '403 permission refused' });
  assert.equal(result.closed.length, 1);
  assert.match(result.failed[0], /403 permission refused/);
  assert.doesNotMatch(result.failed[0], /Automatically closed/);
});

test('malicious filenames are API data, logged as escaped strings and never executed', async () => {
  const result = await run({ actual: [...original, blob('evil\n::error::${process.exit(99)}.py')] });
  assertClosed(result);
  assert.ok(result.warnings.some(message => message.includes('\\n::error::')));
});
