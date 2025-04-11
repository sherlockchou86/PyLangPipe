import os, fitz, sqlite3, re
import faiss
import numpy as np
from docx import Document
from tqdm import tqdm
from ollama import embed

"""
基于tests/files文件夹下的docx/pdf文件，模拟构建一个知识库。脚本生成两个文件，一个为faiss.db，一个为faiss.index
供12-vector_rag.py 使用。
"""

DB_PATH = "faiss.db"
INDEX_PATH = "faiss.index"
EMBED_MODEL = 'granite-embedding:278m'

def extract_text_from_file(filepath):
    if filepath.endswith(".pdf"):
        doc = fitz.open(filepath)
        return "\n".join([page.get_text() for page in doc])
    elif filepath.endswith(".docx"):
        doc = Document(filepath)
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        raise ValueError("Unsupported file type.")

def split_text(text, max_length=300, overlap=50):
    # 按中英文标点切句
    sentences = re.split(r'(?<=[。！？!?；;．.])', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_length:
            current_chunk += sentence
        else:
            # 添加当前段落
            chunks.append(current_chunk)
            # 保留 overlap 的结尾部分作为下段开头
            current_chunk = current_chunk[-overlap:] + sentence

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS faiss_meta (
        id INTEGER PRIMARY KEY,
        chunk_text TEXT,
        source_file TEXT
    )
    """)
    conn.commit()
    return conn

def index_documents(folder):
    conn = init_db()
    cur = conn.cursor()
    all_chunks = []

    for fname in tqdm(os.listdir(folder)):
        fpath = os.path.join(folder, fname)
        try:
            text = extract_text_from_file(fpath)
            chunks = split_text(text)
            for chunk in chunks:
                cur.execute("INSERT INTO faiss_meta (chunk_text, source_file) VALUES (?, ?)", (chunk, fname))
                all_chunks.append(chunk)
        except Exception as e:
            print(f"Failed to process {fname}: {e}")

    conn.commit()

    # 向量化并构建 faiss
    print("Embedding and indexing...")
    response = embed(model=EMBED_MODEL, input=all_chunks)

    dim = len(response['embeddings'][0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(response['embeddings']))
    faiss.write_index(index, INDEX_PATH)
    conn.close()
    print("Index and metadata saved.")

if __name__ == "__main__":
    index_documents("./files")  # 替换为你的文档目录路径
