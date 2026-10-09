const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');

// Execute the actual inline workflow script with mocked APIs; no duplicate policy.
const workflow = fs.readFileSync(path.resolve(__dirname, '../../workflows/branch-policy.yml'), 'utf8');
const block = workflow.split(/          script: \|\r?\n/)[1];
assert.ok(block, 'The workflow must contain its inline enforcement script.');
const script = block.split(/\r?\n/).map(line => line.replace(/^ {12}/, '')).join('\n');
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
const enforce = new AsyncFunction('context', 'github', 'core', script);

async function run(eventName, payload, options = {}) {
  const deleted = [], failed = [], info = [], warnings = [];
  const github = {
    rest: {
      git: { deleteRef: async value => {
        deleted.push(value);
        if (options.error) throw options.error;
      } },
      repos: { listBranches: function listBranches() {} }
    },
    paginate: async (method, parameters) => {
      assert.equal(method, github.rest.repos.listBranches);
      assert.equal(parameters.per_page, 100);
      return (options.branches || []).map(name => ({ name }));
    }
  };
  const core = {
    setFailed: message => failed.push(message), info: message => info.push(message),
    warning: message => warnings.push(message)
  };
  await enforce({ eventName, payload, repo: { owner: 'owner', repo: 'pacman' } }, github, core);
  return { deleted, failed, info, warnings };
}

test('lowercase names accept any prefix without deleting', async () => {
  for (const ref of ['main', 'dev', 'codex/workflows', 'feature/q1-dfs', 'fix/search', 'student-work']) {
    const result = await run('create', { ref_type: 'branch', ref });
    assert.deepEqual(result.deleted, []);
    assert.deepEqual(result.failed, []);
  }
});

test('uppercase and mixed case branches are deleted, never renamed', async () => {
  for (const ref of ['Feature/dfs', 'feature/Q1', 'UPPERCASE']) {
    const result = await run('create', { ref_type: 'branch', ref });
    assert.deepEqual(result.deleted, [{ owner: 'owner', repo: 'pacman', ref: `heads/${ref}` }]);
    assert.equal(result.failed.length, 1);
  }
});

test('push fallback checks existing invalid branches', async () => {
  const result = await run('push', { ref: 'refs/heads/fix/BFS', deleted: false });
  assert.equal(result.deleted[0].ref, 'heads/fix/BFS');
  assert.ok(result.failed.length);
});

test('tag creation, tag pushes and deleted branches cause no deletion', async () => {
  for (const [event, payload] of [
    ['create', { ref_type: 'tag', ref: 'V1' }],
    ['push', { ref: 'refs/tags/V1' }],
    ['push', { ref: 'refs/heads/UPPER', deleted: true }]
  ]) {
    const result = await run(event, payload);
    assert.deepEqual(result.deleted, []);
    assert.deepEqual(result.failed, []);
  }
});

test('same repository PRs delete invalid head branches', async () => {
  const result = await run('pull_request_target', {
    pull_request: { head: { ref: 'feature/AStar', repo: { full_name: 'OWNER/PacMan' } } }
  });
  assert.equal(result.deleted[0].ref, 'heads/feature/AStar');
});

test('fork PRs fail the check without deleting any base or fork branch', async () => {
  const result = await run('pull_request_target', {
    pull_request: { head: { ref: 'Feature/search', repo: { full_name: 'someone/pacman' } } }
  });
  assert.deepEqual(result.deleted, []);
  assert.ok(result.failed.length);
  assert.match(result.warnings[0], /fork/);
});

test('manual audit paginates all branches and deletes invalid names once', async () => {
  const result = await run('workflow_dispatch', {}, { branches: ['main', 'Feature/one', 'Feature/one', 'dev', 'fix/TWO'] });
  assert.deepEqual(result.deleted.map(item => item.ref), ['heads/Feature/one', 'heads/fix/TWO']);
  assert.equal(result.failed.length, 2);
});

test('already deleted branches still fail the naming check without an API error', async () => {
  const result = await run('create', { ref_type: 'branch', ref: 'Feature/one' },
    { error: { status: 404, message: 'Not Found' } });
  assert.equal(result.failed.length, 1);
  assert.match(result.info[0], /already absent/);
});

test('protected branch or permission refusal fails visibly without bypass attempts', async () => {
  for (const status of [403, 422]) {
    const result = await run('create', { ref_type: 'branch', ref: 'Feature/one' },
      { error: { status, message: 'Deletion refused' } });
    assert.equal(result.failed.length, 2);
    assert.match(result.failed[1], /GitHub refused deletion/);
    assert.equal(result.deleted.length, 1);
  }
});

test('missing PR head or unsupported events fail without deleting anything', async () => {
  for (const event of ['pull_request_target', 'unexpected']) {
    const result = await run(event, {});
    assert.deepEqual(result.deleted, []);
    assert.ok(result.failed.length);
  }
});

test('branch text is API data and never evaluated as code', async () => {
  const ref = 'Feature/${process.exit(99)}';
  const result = await run('create', { ref_type: 'branch', ref });
  assert.equal(result.deleted[0].ref, `heads/${ref}`);
});
