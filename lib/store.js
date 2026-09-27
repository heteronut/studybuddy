import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const defaultDataFile = path.join(__dirname, '..', 'data', 'library.json');

export async function readLibrary(filePath = defaultDataFile) {
  try {
    const raw = await fs.readFile(filePath, 'utf8');
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch (error) {
    if (error && error.code === 'ENOENT') {
      return [];
    }

    throw error;
  }
}

export async function writeLibrary(data, filePath = defaultDataFile) {
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await fs.writeFile(filePath, JSON.stringify(data, null, 2), 'utf8');
  return data;
}

export async function addLibraryEntry(entry, filePath = defaultDataFile) {
  const library = await readLibrary(filePath);
  library.push(entry);
  await writeLibrary(library, filePath);
  return entry;
}

export async function removeLibraryEntry(id, filePath = defaultDataFile) {
  const library = await readLibrary(filePath);
  const filtered = library.filter((item) => item.id !== id);
  await writeLibrary(filtered, filePath);
  return filtered;
}
