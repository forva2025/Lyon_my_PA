from __future__ import annotations

from pathlib import Path

import streamlit as st

from rag_engine import LocalRAGEngine, RAGError
from settings import (
    DOCUMENTS_DIR,
    EMBEDDING_MODEL,
    LLM_MODEL,
    MAX_UPLOAD_MB,
    MAX_TOP_K,
    DEFAULT_TOP_K,
)


st.set_page_config(
    page_title="Lyon My PA",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)


@st.cache_resource(show_spinner=False)
def get_engine() -> LocalRAGEngine:
    return LocalRAGEngine()


def source_key_for(path: Path) -> str:
    return path.relative_to(DOCUMENTS_DIR).as_posix()


def display_sources(sources: list[dict]) -> None:
    if not sources:
        return
    with st.expander("Sources used", expanded=False):
        for source in sources:
            page = f" · page {source['page_number']}" if source.get("page_number", 0) else ""
            st.markdown(
                f"**[{source['number']}]** `{source['source']}`{page}  "
                f"\n<small>Cosine distance: {source['distance']:.3f}</small>",
                unsafe_allow_html=True,
            )
            st.caption(source["text"][:700] + ("…" if len(source["text"]) > 700 else ""))


st.title("📚 Local RAG Assistant")
st.caption("Ask questions about your own documents. Models and vector storage run on this computer.")

try:
    engine = get_engine()
except RAGError as exc:
    st.error(str(exc))
    st.stop()

# Sidebar: local service status and knowledge-base management.
with st.sidebar:
    st.header("System status")
    status = engine.ollama_status()
    if status["online"]:
        st.success("Ollama is running")
    else:
        st.error("Ollama is offline")
        st.caption("Open the Ollama desktop application and refresh this page.")

    installed = set(status.get("models", []))
    llm_ready = LLM_MODEL in installed
    embed_ready = EMBEDDING_MODEL in installed
    st.write(f"{'✅' if llm_ready else '⬜'} Generator: `{LLM_MODEL}`")
    st.write(f"{'✅' if embed_ready else '⬜'} Embeddings: `{EMBEDDING_MODEL}`")
    if status["online"] and not (llm_ready and embed_ready):
        st.warning("One or both models are missing. Run the pull commands in README.md.")

    st.divider()
    st.header("Add documents")
    uploads = st.file_uploader(
        "Choose PDF, DOCX or TXT files",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        help=f"Maximum {MAX_UPLOAD_MB} MB per file.",
    )
    models_ready = status["online"] and llm_ready and embed_ready
    if st.button(
        "Save and index uploads",
        type="primary",
        use_container_width=True,
        disabled=(not uploads) or (not models_ready),
    ):
        oversized = [
            upload.name
            for upload in uploads
            if len(upload.getvalue()) > MAX_UPLOAD_MB * 1024 * 1024
        ]
        if oversized:
            st.error(
                f"These files exceed the {MAX_UPLOAD_MB} MB per-file limit: "
                + ", ".join(oversized)
            )
        else:
            successes = 0
            for upload in uploads:
                safe_name = Path(upload.name).name
                destination = DOCUMENTS_DIR / safe_name
                try:
                    destination.write_bytes(upload.getvalue())
                    with st.spinner(f"Indexing {safe_name}…"):
                        result = engine.index_file(destination, source_key_for(destination))
                    st.success(f"{safe_name}: {result['message']}")
                    successes += 1
                except (OSError, RAGError) as exc:
                    st.error(f"{safe_name}: {exc}")
            if successes:
                st.rerun()

    st.caption("You can also copy files directly into `data/documents`.")
    if st.button(
        "Index / update all folder documents",
        use_container_width=True,
        disabled=not models_ready,
    ):
        files = [
            path for path in DOCUMENTS_DIR.rglob("*")
            if path.is_file() and path.suffix.lower() in {".pdf", ".docx", ".txt"}
        ]
        if not files:
            st.info("No supported documents found in data/documents.")
        else:
            progress = st.progress(0)
            for index, path in enumerate(files, start=1):
                try:
                    with st.spinner(f"Indexing {path.name}…"):
                        result = engine.index_file(path, source_key_for(path))
                    st.write(f"✅ `{path.name}`: {result['message']}")
                except RAGError as exc:
                    st.error(f"{path.name}: {exc}")
                progress.progress(index / len(files))
            st.rerun()

    st.divider()
    st.header("Knowledge base")
    indexed = engine.indexed_sources()
    total_chunks = sum(item["chunks"] for item in indexed)
    col_a, col_b = st.columns(2)
    col_a.metric("Documents", len(indexed))
    col_b.metric("Chunks", total_chunks)

    if indexed:
        selected_source = st.selectbox(
            "Remove an indexed document",
            options=[item["source"] for item in indexed],
        )
        if st.button("Remove selected document", use_container_width=True):
            engine.remove_source(selected_source)
            st.success(f"Removed {selected_source} from the index.")
            st.rerun()

    with st.expander("Advanced / reset"):
        st.caption("Clearing the index removes vectors only. Original files remain in data/documents.")
        confirm_clear = st.checkbox("I understand that all indexed vectors will be deleted")
        if st.button("Clear entire index", disabled=not confirm_clear, use_container_width=True):
            engine.clear_index()
            st.success("The vector index has been cleared.")
            st.rerun()

    st.divider()
    top_k = st.slider(
        "Retrieved chunks per question",
        min_value=1,
        max_value=MAX_TOP_K,
        value=DEFAULT_TOP_K,
        help="More chunks provide more context but use more memory and prompt space.",
    )
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main chat area.
if "messages" not in st.session_state:
    st.session_state.messages = []

if not indexed:
    st.info("Start by adding a PDF, Word document or text file in the sidebar, then index it.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            display_sources(message.get("sources", []))

prompt = st.chat_input("Ask a question about your indexed documents…", disabled=(not status["online"]))
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching your documents and generating an answer…"):
            try:
                result = engine.ask(prompt, top_k=top_k)
                answer = result["answer"]
                sources = result["sources"]
                st.markdown(answer)
                display_sources(sources)
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer, "sources": sources}
                )
            except RAGError as exc:
                st.error(str(exc))
                st.session_state.messages.append(
                    {"role": "assistant", "content": f"I could not complete the request: {exc}", "sources": []}
                )
