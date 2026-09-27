import json
import mimetypes
import uuid
from datetime import datetime
from pathlib import Path

import streamlit as st

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover
    genai = None

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = BASE_DIR / "uploads"
DATA_FILE = DATA_DIR / "library.json"

DATA_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)


def load_library() -> list:
    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]", encoding="utf-8")
        return []

    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def save_library(items: list) -> None:
    DATA_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def remove_file_if_exists(file_path: str | None) -> None:
    if not file_path:
        return

    target = BASE_DIR / file_path
    if target.exists():
        target.unlink()


def build_library_context(items: list) -> str:
    if not items:
        return "Belum ada referensi buku atau jurnal di library."

    lines = []
    for item in items:
        title = item.get("title", "Judul tidak tersedia")
        author = item.get("author", "Penulis tidak tersedia")
        kind = item.get("type", "book")
        year = item.get("year", "-")
        description = item.get("description", "")
        file_name = item.get("file_name", "")

        lines.append(
            f"- {title} oleh {author} ({kind}, tahun {year}). "
            f"Deskripsi: {description or 'Tidak ada deskripsi.'}. "
            f"File: {file_name if file_name else 'tidak ada file'}"
        )

    return "\n".join(lines)


def build_chat_prompt(question: str, items: list) -> str:
    context = build_library_context(items)
    return (
        "Anda adalah guru tutor dan pustakawan pada StudyBuddy Library. "
        "Bantulah pengguna memahami buku dan jurnal menggunakan referensi yang ada di library. "
        "Gunakan bahasa akademis, mudah dipahami, dan tidak berbelit-belit. "
        "Jawaban harus berfokus pada isi buku/jurnal, inti materi, poin penting, dan cara belajar. "
        "Jika informasi tidak ada di library, jelaskan bahwa referensi belum tersedia dan sarankan cara belajar yang aman.\n\n"
        f"Referensi library:\n{context}\n\n"
        f"Pertanyaan user:\n{question}"
    )


def ask_gemini(question: str, api_key: str, model_name: str, temperature: float, items: list) -> str:
    if not api_key:
        return "Masukkan API key Gemini terlebih dahulu di sidebar agar chatbot dapat menjawab."

    if genai is None:
        return "Paket google-generativeai belum terpasang. Instal ulang requirements.txt agar fitur chatbot aktif."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={
                "temperature": min(max(float(temperature), 0.0), 1.0),
                "top_p": 0.95,
            },
        )
        response = model.generate_content(build_chat_prompt(question, items))
        return getattr(response, "text", "Maaf, chatbot tidak dapat menghasilkan jawaban saat ini.")
    except Exception as exc:  # pragma: no cover - runtime API issue
        return f"Chatbot gagal menjawab: {exc}"


st.set_page_config(page_title="StudyBuddy Library", page_icon="📚", layout="wide")

st.title("📚 StudyBuddy Library")
st.caption("Aplikasi perpustakaan mini untuk buku dan jurnal yang bisa dideploy ke Streamlit")

items = load_library()

with st.form("library_form", clear_on_submit=True):
    col1, col2 = st.columns(2)

    with col1:
        title = st.text_input("Judul", placeholder="Contoh: Dasar Pemrograman")
        author = st.text_input("Penulis", placeholder="Nama penulis")
        library_type = st.selectbox("Tipe", ["book", "journal"])

    with col2:
        year = st.number_input("Tahun", min_value=1900, max_value=2100, value=datetime.now().year)
        description = st.text_area("Deskripsi", placeholder="Ringkasan singkat...")
        uploaded_file = st.file_uploader(
            "Upload file buku/jurnal",
            type=["pdf", "doc", "docx", "txt", "ppt", "pptx", "png", "jpg", "jpeg"],
        )

    submitted = st.form_submit_button("Simpan data")

    if submitted:
        if not title.strip() or not author.strip():
            st.error("Judul dan penulis wajib diisi.")
        else:
            items = load_library()
            entry = {
                "id": str(uuid.uuid4()),
                "title": title.strip(),
                "author": author.strip(),
                "type": library_type,
                "year": int(year),
                "description": description.strip(),
                "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
                "file_name": "",
                "file_path": "",
            }

            if uploaded_file is not None:
                safe_name = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in uploaded_file.name)
                timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
                saved_name = f"{timestamp}-{safe_name}"
                saved_path = UPLOAD_DIR / saved_name
                saved_path.write_bytes(uploaded_file.getvalue())
                entry["file_name"] = safe_name
                entry["file_path"] = str(saved_path.relative_to(BASE_DIR)).replace("\\", "/")

            items.append(entry)
            save_library(items)
            st.success("Data berhasil disimpan ke library.")
            st.rerun()

st.subheader("Daftar koleksi")
items = load_library()

if not items:
    st.info("Belum ada buku atau jurnal yang tersimpan.")
else:
    for item in reversed(items):
        with st.container():
            st.markdown("---")
            col_title, col_action = st.columns([4, 1])

            with col_title:
                st.markdown(f"### {item.get('title', 'Judul tidak tersedia')}")
                st.write(f"Penulis: **{item.get('author', '-')}**")
                st.write(f"Tipe: **{item.get('type', '-')}** | Tahun: **{item.get('year', '-')}**")
                if item.get("description"):
                    st.write(item.get("description"))

            with col_action:
                if item.get("file_path"):
                    file_path = BASE_DIR / item["file_path"]
                    if file_path.exists():
                        st.download_button(
                            label="Download",
                            data=file_path.read_bytes(),
                            file_name=item.get("file_name") or file_path.name,
                            mime=mimetypes.guess_type(file_path.name)[0] or "application/octet-stream",
                            key=f"download-{item.get('id')}",
                        )

                if st.button("Hapus", key=f"delete-{item.get('id')}"):
                    current_items = load_library()
                    filtered = [entry for entry in current_items if entry.get("id") != item.get("id")]
                    save_library(filtered)
                    remove_file_if_exists(item.get("file_path"))
                    st.success("Item berhasil dihapus.")
                    st.rerun()

st.sidebar.header("AI Tutor Library")
st.sidebar.caption("Guru tutor dan pustakawan yang menjawab berdasarkan referensi library")

def get_api_key() -> str:
    if "GOOGLE_API_KEY" in st.secrets:
        return st.secrets["GOOGLE_API_KEY"]
    return ""

api_key = st.sidebar.text_input("Gemini API Key", type="password", value=get_api_key(), help="Bisa diisi manual atau lewat st.secrets")
model_name = st.sidebar.text_input("Model Gemini", value="gemini-1.5-flash", help="Contoh: gemini-1.5-flash")
temperature = st.sidebar.slider("Temperature", min_value=0.0, max_value=5.0, value=5.0, step=0.1, help="Nilai di API akan dibatasi ke rentang valid (0-1) untuk Gemini")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.sidebar.write(f"Total item library: {len(items)}")

st.subheader("Chatbot Tutor")

for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

prompt = st.chat_input("Tanya tentang isi buku/jurnal dari library...", key="library_chat")

if prompt:
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    answer = ask_gemini(prompt, api_key, model_name, temperature, items)
    st.session_state.chat_history.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)

st.sidebar.write("Catatan: user dapat menambahkan API key sendiri untuk chatbot.")
