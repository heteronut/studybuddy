# StudyBuddy Library

A simple mini library app to store books and journals along with uploaded files.

## Fitur

- Tambah data buku atau jurnal
- Unggah file seperti PDF, DOCX, atau gambar
- Lihat daftar koleksi di dashboard
- Hapus item dan file yang terkait

## Jalankan aplikasi

1. Install dependency:
   npm install
2. Jalankan server:
   npm start
3. Buka browser ke:
   http://localhost:3000

## Struktur proyek

- `server.js` - server Express
- `public/` - file frontend
- `lib/store.js` - helper penyimpanan data
- `data/library.json` - metadata buku dan jurnal
- `uploads/` - file yang diunggah
