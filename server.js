import express from 'express';
import multer from 'multer';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { randomUUID } from 'node:crypto';
import { readLibrary, writeLibrary, removeLibraryEntry } from './lib/store.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const uploadsDir = path.join(__dirname, 'uploads');
const publicDir = path.join(__dirname, 'public');
const app = express();
const port = process.env.PORT || 3000;

if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
}

const storage = multer.diskStorage({
  destination: (_req, _file, cb) => {
    cb(null, uploadsDir);
  },
  filename: (_req, file, cb) => {
    const safeName = file.originalname.replace(/[^a-zA-Z0-9._-]/g, '_');
    const uniqueName = `${Date.now()}-${safeName}`;
    cb(null, uniqueName);
  }
});

const upload = multer({ storage });

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use('/uploads', express.static(uploadsDir));
app.use(express.static(publicDir));

app.get('/api/library', async (_req, res) => {
  try {
    const items = await readLibrary();
    res.json(items);
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Gagal memuat daftar perpustakaan.' });
  }
});

app.post('/api/library', upload.single('file'), async (req, res) => {
  const { title, author, type, year, description } = req.body;

  if (!title || !author || !type) {
    return res.status(400).json({
      message: 'Judul, penulis, dan tipe harus diisi.'
    });
  }

  try {
    const library = await readLibrary();
    const newItem = {
      id: randomUUID(),
      title: title.trim(),
      author: author.trim(),
      type: type.trim().toLowerCase(),
      year: Number(year) || new Date().getFullYear(),
      description: description ? description.trim() : '',
      fileName: req.file ? req.file.originalname : '',
      fileUrl: req.file ? `/uploads/${req.file.filename}` : '',
      createdAt: new Date().toISOString()
    };

    library.push(newItem);
    await writeLibrary(library);
    res.status(201).json(newItem);
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Gagal menyimpan data buku atau jurnal.' });
  }
});

app.delete('/api/library/:id', async (req, res) => {
  const { id } = req.params;

  try {
    const library = await readLibrary();
    const item = library.find((entry) => entry.id === id);

    if (!item) {
      return res.status(404).json({ message: 'Data tidak ditemukan.' });
    }

    if (item.fileUrl) {
      const filePath = path.join(__dirname, item.fileUrl.replace(/^\//, ''));
      if (fs.existsSync(filePath)) {
        fs.unlinkSync(filePath);
      }
    }

    const remaining = await removeLibraryEntry(id);
    res.json({ success: true, data: remaining });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Gagal menghapus data.' });
  }
});

app.get('*', (_req, res) => {
  res.sendFile(path.join(publicDir, 'index.html'));
});

app.listen(port, () => {
  console.log(`Library app running at http://localhost:${port}`);
});
