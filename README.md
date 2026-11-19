# Local RAG Assistant

A small, local Retrieval-Augmented Generation (RAG) project for Windows. It lets you upload PDF, DOCX and TXT documents, stores their embeddings in a local ChromaDB database, retrieves relevant chunks, and asks a local Ollama model to answer questions using that context.

**No paid LLM API, API key or cloud vector database is required.** After downloading the models, document indexing and question answering run on your computer.

## 1. What is included

- `app.py` - Streamlit chat interface and document manager.
- `rag_engine.py` - document parsing, chunking, local embeddings, Chroma retrieval and local generation.
- `settings.py` - model names, local paths and low-memory settings.
- `data/documents/` - place your PDF, DOCX and TXT files here. A fictional sample file is included.
- `data/chroma_db/` - persistent local vector database. It is created automatically.
- `install_windows.bat` - creates a Python virtual environment and installs dependencies.
- `run_windows.bat` - starts the app.
- `download_models.bat` - downloads the two Ollama models after Ollama is installed.

## 2. Requirements

- Windows 10 or Windows 11, 64-bit.
- Python 3.11, 64-bit recommended.
- Ollama for Windows: <https://ollama.com/download>
- About 8 GB RAM and free SSD space. Your available 10 GB should be workable for this small setup, but leave several GB free for Python packages, model downloads, temporary files and documents.
- Internet is needed for the initial Ollama/Python/model downloads. The RAG application can then run offline, provided Ollama is running and the models are installed.

With 8 GB RAM, close other memory-heavy applications while indexing or chatting. The defaults use a small model, short context and small embedding batches. Performance depends on your CPU and other running programs.

## 3. Install Ollama and download the models

1. Install Ollama from <https://ollama.com/download>.
2. Open the Ollama desktop app. It normally starts the local service at `http://127.0.0.1:11434`.
3. Double-click `download_models.bat`, or open PowerShell and run:

```powershell
ollama pull qwen3:1.7b
ollama pull nomic-embed-text
```

4. Check the models are present:

```powershell
ollama list
```

The project uses `qwen3:1.7b` to generate answers and `nomic-embed-text` to embed documents and questions.

## 4. Install the Python project

1. Extract this project folder to a location with enough free space, such as `C:\Projects\local_rag_assistant`.
2. Double-click `install_windows.bat`.
3. Wait for the Python dependencies to install. This step needs an internet connection.

Alternatively, from PowerShell in the project folder:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks virtual-environment activation, you can use `run_windows.bat` instead; it activates the environment for you.

## 5. Run the application

Double-click `run_windows.bat`, or run:

```powershell
.venv\Scripts\python.exe -m streamlit run app.py
```

Streamlit will open the app in your browser, usually at `http://localhost:8501`.

On first launch, the app should show Ollama as running and both models as installed. If it does not, open Ollama and verify the model names with `ollama list`.

## 6. Add documents and ask questions

1. Use the sidebar uploader to choose PDF, DOCX or TXT files.
2. Click **Save and index uploads**.
3. Wait for each document to be processed. The app reports how many chunks were stored.
4. Ask a question in the chat box.
5. Expand **Sources used** under an answer to see the files, PDF page numbers where available, and retrieved text excerpts.

You can also copy supported files directly into `data/documents/` and click **Index / update all folder documents**.

The app detects whether a file has changed. If its contents are unchanged, it skips embedding it again. If it has changed, the updated chunks replace the previous version after the new version has been indexed.

## 7. Remove documents and reset the database

- **Remove selected document** deletes that document's vectors from ChromaDB. It does not delete the original file from `data/documents/`.
- **Clear entire index** deletes all vectors but preserves your source documents. You must confirm the action in the sidebar.
- To delete an uploaded original file, close the app and delete it from `data/documents/` in File Explorer.

## 8. Low-memory settings

The defaults in `settings.py` are intentionally conservative:

- Generator: `qwen3:1.7b`
- Embedding model: `nomic-embed-text`
- Context window: 2,048 tokens
- Retrieved chunks: 4 per question by default
- Embedding batch size: 8
- Chunk size: 1,000 characters with 150 characters of overlap
- Generated answer: maximum 512 tokens

To reduce memory further, set `NUM_CTX = 1536`, `EMBED_BATCH_SIZE = 4` and `DEFAULT_TOP_K = 3` in `settings.py`. This may reduce answer quality or make retrieval less comprehensive. If you switch models, update the relevant setting in `settings.py` and pull that model with Ollama.

The app asks Ollama to unload each model after its operation (`keep_alive: "0"`) so the embedding model and generator do not need to remain loaded together. Model reloads can add waiting time.

## 9. Troubleshooting

**Ollama is offline**

Open the Ollama desktop app. In PowerShell, try `ollama list`. The local service should respond at `http://127.0.0.1:11434`.

**Model missing**

Run the two `ollama pull` commands above. The model names in `settings.py` must match the installed tags.

**Not enough memory / model fails to load**

Close browsers and other applications, reduce `NUM_CTX` and `EMBED_BATCH_SIZE`, and try again. You can try `qwen3:0.6b` by pulling it and changing `LLM_MODEL` in `settings.py` to `qwen3:0.6b`.

**A PDF produces no text**

The PDF may be scanned images rather than selectable text. This starter project does not include OCR. Convert it to a searchable PDF with an OCR tool before indexing it.

**Chroma database cannot open**

Close any other running copy of this app. Do not manually edit files inside `data/chroma_db/`. If the database is corrupted and you are comfortable rebuilding it, stop the app, delete that folder, then restart and re-index your documents.

**Port 8501 is already in use**

Run `python -m streamlit run app.py --server.port 8502` from the activated environment.

## 10. Run the small local tests

After installing dependencies:

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The tests check the text chunking helper. A full integration test requires Ollama to be running with both models downloaded.

## Architecture and official references

```text
PDF / DOCX / TXT
       |
       v
Text extraction + chunking
       |
       v
Ollama embedding endpoint (nomic-embed-text)
       |
       v
Persistent ChromaDB collection
       |
       v
Question -> query embedding -> similarity search
       |
       v
Retrieved chunks + question
       |
       v
Ollama chat endpoint (qwen3:1.7b)
       |
       v
Answer with source labels
```

- Ollama embeddings API: <https://docs.ollama.com/api/embed>
- Ollama chat API: <https://docs.ollama.com/api/chat>
- Chroma persistent Python client: <https://docs.trychroma.com/reference/python/client>
- Streamlit: <https://docs.streamlit.io/>

## Important limitation

This is a local development and learning project, not a production-secured multi-user service. It does not include authentication, OCR, advanced reranking, hybrid keyword search, background processing or automated RAG evaluation. Those can be added after the first version works on your computer.
