import json
import logging
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import numpy as np
import streamlit as st

from src.chunker import build_chunks
from src.config import DOCUMENTS_DIR, OUTPUT_DIR, VECTOR_STORE_DIR, get_setting
from src.embeddings import generate_embeddings
from src.multimodal_processor import process_documents
from src.qa_engine import answer_question
from src.query_classifier import classify_question
from src.reranker import rerank_evidence
from src.retriever import retrieve_relevant_chunks
from src.theme import render_doculens_theme
from src.utils import write_json
from src.vector_store import FAISSVectorStore

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

NAV_ITEMS = ["Overview", "Ask", "Documents", "Search", "Settings", "Developer"]


@st.cache_resource
def get_store():
    store = FAISSVectorStore()
    index_path = VECTOR_STORE_DIR / "faiss_index.index"
    meta_path = VECTOR_STORE_DIR / "metadata.json"
    if index_path.exists() and meta_path.exists():
        store.load(str(VECTOR_STORE_DIR))
    return store


def summarize_document(document):
    items = document.get("items", [])
    text_count = sum(1 for item in items if item.get("type") in {"text", "ocr"})
    table_count = sum(1 for item in items if item.get("type") == "table")
    visual_count = sum(1 for item in items if item.get("type") == "visual")
    content = " ".join(item.get("content", "") for item in items[:5] if item.get("content"))
    summary = (content[:220] + "...") if len(content) > 220 else content
    return {
        "document": document.get("document"),
        "pages": document.get("pages", 0),
        "tables": table_count,
        "visuals": visual_count,
        "text_blocks": text_count,
        "summary": summary,
    }


def process_uploaded_pdfs(files, chunk_size, chunk_overlap, enable_ocr):
    file_paths = []
    rejected = []

    for uploaded_file in files:
        if uploaded_file is None or getattr(uploaded_file, "size", 0) <= 0:
            rejected.append(uploaded_file.name if uploaded_file else "unknown")
            continue

        destination = DOCUMENTS_DIR / uploaded_file.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        with open(destination, "wb") as handle:
            handle.write(uploaded_file.getvalue())
        file_paths.append(str(destination))

    processed = process_documents(file_paths, enable_ocr=enable_ocr)
    flat_items = []
    for document in processed:
        flat_items.extend(document["items"])

    if not processed:
        return {"processed": [], "chunks": [], "store": None, "rejected": rejected}

    all_chunks = build_chunks(flat_items, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    write_json(str(OUTPUT_DIR / "chunks.json"), all_chunks)

    embeddings, chunk_payload = generate_embeddings(all_chunks, model_name=get_setting("EMBEDDING_MODEL", "all-MiniLM-L6-v2"))
    embedding_matrix = np.asarray(embeddings, dtype="float32")
    if embedding_matrix.size == 0:
        embedding_matrix = np.zeros((1, 384), dtype="float32")
    vector_store = FAISSVectorStore(dimension=embedding_matrix.shape[1])
    vector_store.add(embedding_matrix, chunk_payload)
    vector_store.save(str(VECTOR_STORE_DIR))

    return {"processed": processed, "chunks": all_chunks, "store": vector_store, "rejected": rejected}


def ensure_session_defaults():
    defaults = {
        "chat_history": [],
        "current_page": "Overview",
        "last_answer": None,
        "last_question": "",
        "question_input": "",
        "ask_question_input": "",
        "current_answer": None,
        "current_evidence": [],
        "selected_documents": [],
        "processed_documents": [],
        "processing_status": ["UPLOAD", "PDF ANALYSIS", "TEXT EXTRACTION", "TABLE EXTRACTION", "OCR", "PAGE RENDERING", "CHUNKING", "EMBEDDINGS", "VECTOR INDEX", "READY"],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def run_question(question: str):
    text = (question or "").strip()
    if not text:
        return None

    if "processed_result" not in st.session_state or not st.session_state["processed_result"]:
        st.warning("Upload and process a document before asking questions.")
        st.session_state.current_answer = None
        st.session_state.current_evidence = []
        return None

    st.session_state.current_page = "Ask"
    st.session_state.last_question = text
    allowed_documents = st.session_state.get("selected_documents") or [doc["document"] for doc in st.session_state["processed_result"]["processed"]]
    st.session_state.selected_documents = allowed_documents

    if not any(msg.get("role") == "user" and msg.get("text") == text for msg in st.session_state.chat_history):
        st.session_state.chat_history.append({"role": "user", "text": text})

    vector_store = st.session_state["processed_result"]["store"]
    retrieved = retrieve_relevant_chunks(
        text,
        vector_store,
        top_k=st.session_state.get("top_k", int(get_setting("TOP_K", 5))),
        model_name=get_setting("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
    )
    if allowed_documents:
        retrieved = [item for item in retrieved if str(item.get("document")) in {str(doc) for doc in allowed_documents}]

    if not retrieved:
        response = {
            "answer": "No relevant evidence was found in the selected documents.",
            "sources": [],
            "question_type": "no_evidence",
            "confidence": "Low",
            "confidence_value": 0.0,
        }
        st.session_state.last_answer = response
        st.session_state.current_answer = response
        st.session_state.current_evidence = []
        st.session_state.chat_history.append({"role": "assistant", "text": response["answer"]})
        return response

    reranked = rerank_evidence(text, retrieved, top_k=st.session_state.get("top_k", int(get_setting("TOP_K", 5))))
    answer_result = answer_question(
        text,
        reranked,
        model_name=get_setting("MODEL_NAME", "gpt-4o-mini"),
        query_type=classify_question(text),
    )

    st.session_state.last_answer = answer_result
    st.session_state.current_answer = answer_result
    st.session_state.current_evidence = answer_result.get("sources", [])
    st.session_state.chat_history.append({"role": "assistant", "text": answer_result["answer"]})
    write_json(str(OUTPUT_DIR / "answers.json"), {"question": text, "answer": answer_result})
    return answer_result


@st.cache_data
def get_demo_questions():
    return [
        "What was the highest revenue?",
        "Which quarter had the highest sales?",
        "What was the percentage increase from Q1 to Q4?",
        "Which page contains operating expenses?",
    ]


def make_widget_key(prefix: str, value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() else "_" for ch in value).strip("_")
    return f"{prefix}_{cleaned.lower()}"


def render_sidebar_nav(selected_page):
    with st.sidebar:
        st.markdown(
            """
            <div style='padding: 1.15rem 0 0.35rem 0;'>
                <div style='display:flex; align-items:center; gap: 0.7rem;'>
                    <span class='logo-mark' style='width:18px; height:18px; display:inline-block;'></span>
                    <div>
                        <div style='font-family: Rajdhani, sans-serif; font-size: 1.65rem; font-weight: 700; letter-spacing: 0.10em; text-transform: uppercase;'>DOCULENS AI</div>
                        <div style='font-size: 0.62rem; color: #756B88; letter-spacing: 0.22em; text-transform: uppercase;'>Multimodal Intelligence</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div class='side-label'>Workspace</div>", unsafe_allow_html=True)
        for item in NAV_ITEMS:
            icon = "◉" if item == "Ask" else "⌂" if item == "Overview" else "▣" if item == "Documents" else "⌕" if item == "Search" else "⚙" if item == "Settings" else "⌘"
            active = selected_page == item
            if st.button(f"{icon} {item.upper()}", key=f"sidebar_{item}", use_container_width=True):
                st.session_state.current_page = item
                st.rerun()

        st.markdown("<div class='side-label'>System</div>", unsafe_allow_html=True)
        system = get_system_status()
        for label, status in system.items():
            color = "#4ADE80" if status in {"ONLINE", "READY", "ENABLED"} else "#F5C451"
            st.markdown(
                f"<div style='display:flex; justify-content:space-between; align-items:center; padding: 0.3rem 0;'><span style='color:#B8AFCB; font-size:0.72rem; letter-spacing:0.12em; text-transform:uppercase;'>{label}</span><span style='color:{color}; font-size:0.65rem; letter-spacing:0.12em; text-transform:uppercase;'>{status}</span></div>",
                unsafe_allow_html=True,
            )

        st.markdown("<div style='margin-top: 1rem; padding-top: 0.8rem; border-top: 1px solid rgba(245,196,81,0.18);'></div>", unsafe_allow_html=True)
        st.subheader("Upload")
        uploaded_files = st.file_uploader("Drop PDF files here", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed")
        if st.button("Process documents", key="sidebar_process", use_container_width=True):
            if uploaded_files:
                with st.spinner("Processing documents..."):
                    try:
                        st.session_state["processed_result"] = process_uploaded_pdfs(uploaded_files, chunk_size=700, chunk_overlap=100, enable_ocr=True)
                        st.session_state["top_k"] = int(get_setting("TOP_K", 5))
                        if not st.session_state["processed_result"].get("processed"):
                            st.error("ERROR // DOCUMENT PROCESSING\nUnable to process this document.")
                        else:
                            st.session_state.current_page = "Overview"
                            st.success("Document processing complete.")
                    except Exception:
                        st.error("ERROR // DOCUMENT PROCESSING\nUnable to process this document.")
            else:
                st.warning("Select one or more PDF files to process.")


def get_active_documents():
    result = st.session_state.get("processed_result") or {}
    return result.get("processed", [])


def get_system_status():
    docs = get_active_documents()
    store = st.session_state.get("processed_result", {}).get("store")
    has_index = bool(store and getattr(store, "index", None) is not None and store.index.ntotal > 0)
    return {
        "AI Engine": "ONLINE" if docs else "STANDBY",
        "Vector Search": "READY" if has_index else "WAITING",
        "OCR": "ENABLED" if docs else "OFFLINE",
        "Vision": "AVAILABLE" if get_setting("VISION_MODEL", "") else "FALLBACK",
    }


def get_page_header(text):
    return f"<div class='section-kicker'>DocuLens AI</div><h2 style='margin:0 0 0.2rem 0; font-size: clamp(2rem, 3vw, 3.4rem);'>{text}</h2>"


def render_topbar(selected_page):
    st.markdown('<div class="hud-shell">', unsafe_allow_html=True)
    brand_col, nav_col, status_col = st.columns([2.2, 5.4, 1.8])
    with brand_col:
        st.markdown(
            """
            <div class='logo-lockup'>
                <span class='logo-mark'></span>
                <div>
                    <div class='brand-title'>DOCULENS</div>
                    <div class='brand-subtitle'>AI</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with nav_col:
        nav_buttons = st.columns(len(NAV_ITEMS))
        for idx, item in enumerate(NAV_ITEMS):
            with nav_buttons[idx]:
                label = item
                if st.button(label.upper(), key=f"topnav_{item.lower()}", use_container_width=True):
                    st.session_state.current_page = item
                    st.rerun()
    with status_col:
        st.markdown(
            """
            <div class='status-panel'>
                <span class='status-dot'></span>
                <span>Systems Online</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)


def render_overview_page(docs):
    total_pages = sum(doc.get("pages", 0) for doc in docs)
    total_tables = sum(1 for doc in docs for item in doc.get("items", []) if item.get("type") == "table")
    total_visuals = sum(1 for doc in docs for item in doc.get("items", []) if item.get("type") == "visual")

    st.markdown(get_page_header("Document Intelligence"), unsafe_allow_html=True)
    st.markdown(
        "<div class='hero-panel hud-panel'>"
        "<div class='section-kicker'>Document Analysis // Active</div>"
        "<div class='hero-title'>Understand <span class='accent'>Every Document.</span></div>"
        "<div class='hero-copy'>Ask questions across text, tables, scanned pages, and visual content with evidence-backed answers.</div>"
        "<div class='tag-row'><span class='tag'>Text</span><span class='tag'>Tables</span><span class='tag'>OCR</span><span class='tag'>Vision</span></div>"
        "</div>",
        unsafe_allow_html=True,
    )

    metric_cols = st.columns(4)
    metric_values = [
        ("Documents", len(docs), "Indexed"),
        ("Pages", total_pages, "Extracted"),
        ("Tables", total_tables, "Detected"),
        ("Visuals", total_visuals, "Indexed"),
    ]
    for col, (label, value, status) in zip(metric_cols, metric_values):
        with col:
            st.markdown(
                f"<div class='metric-card'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div><div class='metric-foot'>{status}</div></div>",
                unsafe_allow_html=True,
            )

    content_left, content_right = st.columns([2, 1])
    with content_left:
        st.markdown("<div class='section-kicker' style='margin-top: 1.5rem;'>Recent Documents</div>", unsafe_allow_html=True)
        if docs:
            for doc in docs:
                summary = summarize_document(doc)
                st.markdown(
                    f"""
                    <div class='document-card' style='margin-top: 0.7rem; margin-bottom: 0.7rem;'>
                        <div class='card-header'>
                            <div class='card-title'>{summary['document']}</div>
                            <span class='status-badge'>Ready</span>
                        </div>
                        <div class='muted-note'>{summary['pages']} pages • {summary['tables']} tables • {summary['visuals']} visuals</div>
                        <div style='margin-top: 0.7rem; color: #B8AFCB; line-height: 1.5;'>{summary['summary']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown("<div class='empty-state'>UPLOAD A DOCUMENT TO BEGIN.</div>", unsafe_allow_html=True)

    with content_right:
        st.markdown("<div class='section-kicker' style='margin-top: 1.5rem;'>Suggested Queries</div>", unsafe_allow_html=True)
        for prompt in get_demo_questions():
            if st.button(prompt, key=f"overview_{make_widget_key('suggested', prompt)}", use_container_width=True):
                st.session_state.current_page = "Ask"
                run_question(prompt)
                st.rerun()

        st.markdown("<div class='section-kicker' style='margin-top: 1.5rem;'>Processing Status</div>", unsafe_allow_html=True)
        if docs:
            steps = ["PDF Analysis", "Text Extraction", "Table Extraction", "OCR", "Visual Indexing", "Embeddings", "Vector Index", "Ready"]
            for step in steps:
                st.markdown(f"<div style='display:flex; align-items:center; gap:0.5rem; color:#B8AFCB; padding:0.18rem 0;'><span style='width:8px; height:8px; border-radius:50%; background:#4ADE80; display:inline-block; box-shadow:0 0 10px rgba(74,222,128,0.6);'></span>{step}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='empty-state'>PROCESS YOUR DOCUMENTS BEFORE ASKING QUESTIONS.</div>", unsafe_allow_html=True)


def render_ask_page(docs):
    st.markdown(get_page_header("Ask Documents"), unsafe_allow_html=True)
    if not docs:
        st.markdown("<div class='empty-state'>UPLOAD A DOCUMENT TO BEGIN.</div>", unsafe_allow_html=True)
        return

    doc_names = [doc["document"] for doc in docs]
    st.markdown("<div class='muted-note' style='margin-top:0.8rem; margin-bottom:0.7rem;'>Active documents</div>", unsafe_allow_html=True)
    selected_doc = st.selectbox("Active documents", doc_names, index=0, label_visibility="collapsed")
    active_docs = [selected_doc] if selected_doc else doc_names
    st.session_state.selected_documents = active_docs

    def clear_ask_input():
        st.session_state["ask_question_input"] = ""
        st.session_state.last_answer = None

    st.markdown("<div class='hud-panel answer-panel'>", unsafe_allow_html=True)
    question = st.text_area("Ask anything about your documents...", height=110, key="ask_question_input")
    ask_col, clear_col = st.columns([4, 1])
    with ask_col:
        if st.button("ASK →", key="ask_question_button", use_container_width=True):
            st.session_state.selected_documents = active_docs
            run_question(question)
    with clear_col:
        if st.button("CLEAR", key="clear_question_button", use_container_width=True, on_click=clear_ask_input):
            pass
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-kicker' style='margin-top: 1.3rem;'>Suggested Queries</div>", unsafe_allow_html=True)
    suggestion_cols = st.columns(2)
    for idx, prompt in enumerate(get_demo_questions()):
        with suggestion_cols[idx % 2]:
            if st.button(prompt, key=f"ask_prompt_{idx}", use_container_width=True):
                st.session_state.selected_documents = active_docs
                run_question(prompt)

    if st.session_state.get("last_answer"):
        answer = st.session_state.last_answer
        st.markdown(
            f"""
            <div class='hud-panel answer-panel' style='margin-top: 1.5rem;'>
                <div class='section-kicker'>Analysis Result</div>
                <div style='font-size: clamp(1.4rem, 2vw, 2.1rem); line-height: 1.2; color: #F8F5FF; font-weight: 700;'>{answer.get('answer','')}</div>
                <div class='evidence-block'>
                    <span class='evidence-pill'>Evidence verified</span>
                    <span class='evidence-pill'>{answer.get('question_type', 'factual').replace('_', ' ').upper()}</span>
                    <span class='evidence-pill'>{answer.get('confidence', 'Medium').upper()}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        sources = answer.get("sources", [])
        if sources:
            st.markdown("<div class='section-kicker' style='margin-top: 1.4rem;'>Evidence</div>", unsafe_allow_html=True)
            for idx, source in enumerate(sources[:5], start=1):
                with st.expander(f"{source.get('document')} — PAGE {source.get('page')} — {source.get('type', 'text').upper()}", expanded=(idx == 1)):
                    st.write(f"Document: {source.get('document')}")
                    st.write(f"Page: {source.get('page')}")
                    st.write(f"Type: {source.get('type')}")
                    st.write(f"Relevance: {source.get('score', 'n/a')}")
                    st.write(f"Evidence: {source.get('content')}")
                    if source.get("image_path") and Path(source["image_path"]).exists():
                        st.image(str(source["image_path"]), caption=f"Source image for {source.get('document')} page {source.get('page')}")
        else:
            st.markdown("<div class='empty-state'>NO RELEVANT EVIDENCE FOUND.</div>", unsafe_allow_html=True)

    if st.session_state.chat_history:
        st.markdown("<div class='section-kicker' style='margin-top: 1.5rem;'>Conversation</div>", unsafe_allow_html=True)
        for entry in st.session_state.chat_history[-6:]:
            role = entry.get("role", "assistant")
            bubble_cls = "user" if role == "user" else "assistant"
            st.markdown(
                f"<div class='chat-bubble {bubble_cls}' style='margin-bottom: 0.6rem;'><div class='chat-role'>{role.upper()}</div><div>{entry.get('text','')}</div></div>",
                unsafe_allow_html=True,
            )


def render_documents_page(docs):
    st.markdown(get_page_header("Documents // Library"), unsafe_allow_html=True)
    if not docs:
        st.markdown("<div class='empty-state'>UPLOAD A DOCUMENT TO BEGIN.</div>", unsafe_allow_html=True)
        return

    grid = st.columns(2)
    for idx, doc in enumerate(docs):
        with grid[idx % 2]:
            summary = summarize_document(doc)
            st.markdown(
                f"""
                <div class='document-card' style='margin-bottom: 1rem;'>
                    <div class='card-header'>
                        <div class='card-title'>{summary['document']}</div>
                        <span class='status-badge'>READY</span>
                    </div>
                    <div class='muted-note'>{summary['pages']} pages • {summary['tables']} tables • {summary['visuals']} visuals</div>
                    <div style='margin-top:0.8rem; color:#B8AFCB; line-height:1.6;'>{summary['summary']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_search_page(docs):
    st.markdown(get_page_header("Document Search // Index"), unsafe_allow_html=True)
    if not docs:
        st.markdown("<div class='empty-state'>UPLOAD A DOCUMENT TO BEGIN.</div>", unsafe_allow_html=True)
        return

    query = st.text_input("Search your indexed documents...", key="search_query")
    if not query:
        st.markdown("<div class='empty-state'>SEARCH YOUR INDEXED DOCUMENTS.</div>", unsafe_allow_html=True)
        return

    results = retrieve_relevant_chunks(query, st.session_state["processed_result"]["store"], top_k=5, model_name=get_setting("EMBEDDING_MODEL", "all-MiniLM-L6-v2"))
    if not results:
        st.markdown("<div class='empty-state'>NO RELEVANT EVIDENCE FOUND.</div>", unsafe_allow_html=True)
        return

    for idx, hit in enumerate(results, start=1):
        with st.expander(f"{hit.get('document')} — PAGE {hit.get('page')} — {hit.get('type', 'text').upper()}", expanded=(idx == 1)):
            st.write(f"Document: {hit.get('document')}")
            st.write(f"Page: {hit.get('page')}")
            st.write(f"Type: {hit.get('type')}")
            st.write(hit.get("content"))
            if hit.get("image_path") and Path(hit["image_path"]).exists():
                st.image(str(hit["image_path"]), caption=f"Source page for {hit.get('document')}")


def render_settings_page():
    st.markdown(get_page_header("Settings"), unsafe_allow_html=True)
    settings = {
        "Embedding Model": get_setting("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
        "Chunk Size": int(get_setting("CHUNK_SIZE", 700)),
        "Chunk Overlap": int(get_setting("CHUNK_OVERLAP", 100)),
        "Top K": int(get_setting("TOP_K", 5)),
        "OCR": "Enabled" if get_setting("ENABLE_OCR", True) else "Disabled",
        "Vision": "Enabled" if get_setting("VISION_MODEL", "") else "Fallback",
        "LLM Model": get_setting("MODEL_NAME", "gpt-4o-mini"),
    }
    for label, value in settings.items():
        st.markdown(
            f"<div style='display:flex; justify-content:space-between; align-items:center; padding:0.8rem 1rem; margin-bottom:0.6rem; border:1px solid rgba(245,196,81,0.18); border-radius:14px; background: rgba(22,16,37,0.9);'><span style='color:#B8AFCB; text-transform:uppercase; letter-spacing:0.12em; font-size:0.68rem;'>{label}</span><span style='color:#F8F5FF; font-weight:700;'>{value}</span></div>",
            unsafe_allow_html=True,
        )


def render_developer_page(docs):
    st.markdown(get_page_header("Developer Console"), unsafe_allow_html=True)
    if not docs:
        st.markdown("<div class='empty-state'>UPLOAD A DOCUMENT TO INSPECT DEBUG METADATA.</div>", unsafe_allow_html=True)
        return
    result = st.session_state.get("processed_result", {})
    st.json({
        "document_count": len(docs),
        "documents": [doc.get("document") for doc in docs],
        "last_question": st.session_state.get("last_question", ""),
        "current_answer": st.session_state.get("last_answer", {}),
        "chunk_count": len(result.get("chunks", [])),
        "vector_store_size": getattr(result.get("store"), "index", None).ntotal if getattr(result.get("store"), "index", None) else 0,
    })


def main():
    render_doculens_theme()
    st.set_page_config(page_title="DocuLens AI", page_icon="📄", layout="wide")
    ensure_session_defaults()
    render_sidebar_nav(st.session_state.get("current_page", "Overview"))
    selected_page = st.session_state.get("current_page", "Overview")
    render_topbar(selected_page)

    documents = get_active_documents()

    if selected_page == "Overview":
        render_overview_page(documents)
    elif selected_page == "Ask":
        render_ask_page(documents)
    elif selected_page == "Documents":
        render_documents_page(documents)
    elif selected_page == "Search":
        render_search_page(documents)
    elif selected_page == "Settings":
        render_settings_page()
    elif selected_page == "Developer":
        render_developer_page(documents)


if __name__ == "__main__":
    main()
