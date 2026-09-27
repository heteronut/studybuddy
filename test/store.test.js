import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';

import { readLibrary, writeLibrary } from '../lib/store.js';

test('readLibrary returns empty array when file is missing', async () => {
  const tempDir = await fs.mkdtemp(path.join(os.tmpdir(), 'studybuddy-library-'));
  const tempFile = path.join(tempDir, 'library.json');

  const result = await readLibrary(tempFile);

  assert.deepEqual(result, []);
});

test('writeLibrary persists data to disk', async () => {
  const tempDir = await fs.mkdtemp(path.join(os.tmpdir(), 'studybuddy-library-'));
  const tempFile = path.join(tempDir, 'library.json');
  const mockData = [{ id: '1', title: 'Jurnal AI', type: 'journal' }];

  await writeLibrary(mockData, tempFile);
  const raw = await fs.readFile(tempFile, 'utf8');

  assert.equal(JSON.parse(raw)[0].title, 'Jurnal AI');
});
