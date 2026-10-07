# DocuLens AI

## Product overview

DocuLens AI is a multimodal document intelligence system for PDF-first question answering. It lets users upload one or more PDFs, extract text and tabular data, perform OCR on scanned pages, preserve image and chart context, index the content for search, and answer grounded questions with explicit evidence and page references.

## Core promise

Answer + evidence + source page + confidence.

## Supported workflow

- PDF upload and multi-document processing
- Text extraction and table detection
- OCR fallback for scanned documents
- Page image and visual context preservation
- Chunking and embedding generation
- FAISS-based retrieval over uploaded documents
- Google-style evidence-first Q&A with page and source tracing
- Calculation support for numeric questions
- Follow-up conversation context within the session
- Clean dark glass dashboard for hackathon presentation

## Architecture

PDF -> validation -> extraction -> text/table/OCR/visual capture -> chunking -> embeddings -> vector retrieval -> evidence reranking -> grounded answer -> source preview -> Streamlit dashboard

## Key capabilities

- Multimodal PDF ingestion for text, tables, scans, and page visuals
- Search across document content with evidence-based retrieval
- Question answering grounded in actual document passages and page references
- Multi-document handling for larger PDF bundles
- Numeric calculation support for percentage, average, total, and difference questions
- Clean professional UI with a dark glass design
- Developer debug information for document, chunk, and retrieval metadata

## Technology stack

- Python 3.12
- Streamlit
- PyMuPDF
- pdfplumber
- Pillow
- pytesseract
- sentence-transformers
- FAISS
- NumPy
- python-dotenv

## Run locally

```bash
cd HNX26PSI01
python -m streamlit run app.py --server.port 8555
```

Then open:

- http://localhost:8555

## Environment settings

Use `.env.example` as the template and create a local `.env` if needed. Supported settings include:

- `LLM_PROVIDER`
- `API_KEY`
- `MODEL_NAME`
- `EMBEDDING_MODEL`
- `TOP_K`
- `CHUNK_SIZE`
- `CHUNK_OVERLAP`
- `ENABLE_OCR`
- `ENABLE_VISUAL_REASONING`

If no external API key is configured, the system uses a grounded fallback path instead of guessing.

## Demo flow

1. Open the app dashboard.
2. Upload PDFs to process them.
3. Process the documents.
4. Ask a question about the document content.
5. Review the answer and cited evidence.
6. Inspect the source page preview and page references.
7. Show the question and evidence flow in front of judges.

## Notes

- This project focuses on the required multimodal document intelligence core and keeps the product stable and demo-ready.
- OCR and visual reasoning depend on document quality and available configuration.
- Every answer is backed by retrieved document evidence rather than invented output.
