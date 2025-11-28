# Embeddings Folder

Folder ini digunakan untuk menyimpan file embedding face recognition (`.pkl` files).

## Cara Penggunaan:
1. Copy file `.pkl` dari folder `API_FR2/embeddings/` atau `Backend_api_dani/embeddings/`
2. Paste ke folder ini
3. File akan otomatis dibaca oleh API face recognition

## Contoh File:
- `Alfian.pkl`
- `202010370311001.pkl` (format NIM)
- dll.

## Format File:
File `.pkl` berisi:
- `embedding`: numpy array (512 dimensions) dari FaceNet
- Nama file: username/NIM mahasiswa
