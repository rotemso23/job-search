# Portfolio Projects

## Project A: SNN Research Assistant — RAG Pipeline ✅ DONE
**Deployed:** HuggingFace Spaces

**What it is:** A RAG pipeline that lets users ask questions over academic papers on SNNs, neuromorphic computing, and low-power deep learning — the domain of Rotem's M.Sc. thesis.

**Tech stack:** LangChain · HuggingFace sentence-transformers · ChromaDB · Claude API · Streamlit · RAGAS · HuggingFace Spaces

**Gaps closed:**
- RAG pipeline design and implementation
- Embeddings and vector search (ChromaDB)
- HuggingFace sentence-transformers
- LangChain orchestration
- RAGAS evaluation methodology
- HuggingFace Spaces deployment
- End-to-end system ownership

---

## Project B: Fine-Tune a Small LLM on a Domain Task
**Status:** Next up

**What it is:** Fine-tune a small pre-trained language model (e.g., Mistral 7B or similar) on a domain-specific task — biomedical Q&A, EEG report summarization, or signal annotation generation. Rotem already understands training loops and optimization from the thesis; this is mostly learning the HuggingFace + LoRA layer on top of that.

**Tech stack:** HuggingFace Transformers · LoRA / PEFT · HuggingFace Trainer API · MLflow (experiment tracking) · PyTorch · HuggingFace Hub (model hosting)

**Gaps closed:**
- LLM fine-tuning (LoRA, PEFT)
- HuggingFace Transformers ecosystem
- Experiment tracking (MLflow)
- Pre-trained model adaptation
- HuggingFace Hub model publishing

---

## Project C: End-to-End ML Pipeline with SQL + Serving
**Status:** Planned

**What it is:** Pick a public time-series or sensor dataset (similar to thesis domain), build a full pipeline: raw data → SQL storage → feature engineering → model training → REST API serving → Docker. The goal is demonstrating end-to-end production-oriented ownership, not just model training.

**Tech stack:** PostgreSQL or SQLite · FastAPI · Docker · MLflow · Scikit-learn or PyTorch · HuggingFace or AWS for deployment

**Gaps closed:**
- SQL (widely missing from CV analyses)
- Docker / containerization
- REST API model serving (FastAPI)
- MLflow experiment tracking
- Production deployment mindset
- Cloud deployment (AWS or HuggingFace)

---

## Project D: NLP Classification / Extraction Pipeline
**Status:** Lower priority — do if specifically targeting NLP roles

**What it is:** An applied NLP pipeline — e.g., classify biomedical abstracts by topic, extract key findings from papers, or build a clinical note analyzer. Gives a real NLP project to talk about in interviews.

**Tech stack:** HuggingFace Transformers · tokenization · fine-tuning for classification or NER · proper NLP evaluation metrics (F1, precision, recall)

**Gaps closed:**
- NLP domain experience
- Text classification or NER
- Tokenization and sequence modeling concepts
- NLP evaluation methodology

---

## Recommended order
1. ✅ Project A — done
2. Project B — closes LLM fine-tuning + HuggingFace ecosystem
3. Project C — closes SQL + Docker + production serving
4. Project D — only if targeting NLP-heavy roles
