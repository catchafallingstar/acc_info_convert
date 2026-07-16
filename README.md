# Accessible Infographic Converter (Backend)

[![Backend Framework](https://img.shields.io/badge/Backend-Django-092E20?style=flat-square&logo=django)](https://www.djangoproject.com/)
[![AI Engine](https://img.shields.io/badge/AI_Engine-U--M_GPT_Toolkit-00274C?style=flat-square)](https://its.umich.edu/)
[![Security](https://img.shields.io/badge/Security-Protected_Bridge-success?style=flat-square)](#)

The secure, robust backend engine for the Accessible Infographic Converter. This Django application acts as a secure processing gateway, extracting visual content, executing optical character recognition (OCR), prompting advanced AI models for descriptive narratives, and outputting highly structured, screen-reader-compliant PDF files[cite: 1].

---

## 🔒 Security & Backend Architecture

This server is designed to act as a **secure bridge** between user uploads and artificial intelligence APIs[cite: 1]:

*   **API Token Obfuscation:** Under no circumstances are raw API credentials exposed to client browsers[cite: 1]. All validation, handshakes, and secret keys are stored safely on the environment layer behind Django[cite: 1].
*   **Secure Pipelines:** Documents uploaded by users are packaged securely and dispatched through protected connections[cite: 1].
*   **Compliance Ready:** Specifically built to easily shift from private sandbox keys to the **U-M GPT Toolkit** (ITS) to guarantee compliance with University of Michigan data security policies.

---

## ⚙️ How the Backend Works (The 4-Stage Process)

Our Django environment manages Stages 2, 3, and 4 of the accessibility workflow[cite: 1]:

### 1. Data Digitization & OCR (Stage 2)
Upon receiving a file from the frontend, the backend digitizes the document and scans it using OCR (Optical Character Recognition) to parse all embedded raw text[cite: 1].

### 2. Intelligent AI Reconstruction (Stage 3)
The backend securely sends the raw OCR data and structural cues to the AI model[cite: 1].
*   **Complex Flowchart/Decision Tree Support:** The system instructs the model to identify conditional shapes (like diamond decision points) and map them out into strict, navigable logical loops (e.g., *If Yes, do X; If No, do Y*) instead of flattening the text.
*   **Logical Outlining:** The AI determines proper heading structures ($H_1, H_2$, etc.) and writes a clean chronological narrative of the graphic[cite: 1].

### 3. Accessible PDF Generation (Stage 4)
The backend compiles a brand new PDF with the following screen-reader-optimized layout[cite: 1]:
*   **Page 1:** Contains the comprehensive, structured, and bulleted text description of the infographic[cite: 1].
*   **Page 2+:** Houses the original graph tagged with structured alt-text describing the image for screen-reader engines[cite: 1].

---

## 🛠️ Tech Stack
*   **Framework:** Django (Python)
*   **OCR Engine:** Tesseract OCR / PyPDF
*   **AI Integrations:** U-M GPT Toolkit / OpenAI API
*   **PDF Compiler:** ReportLab / Weasyprint

---

## 💻 Local Setup & Installation

Follow these instructions to run the backend server locally:

### Prerequisites
*   Python 3.10+
*   pip (Python package manager)

### 1. Clone & Navigate to Backend
```bash
git clone <your-backend-repository-url>
cd acc_info_convert_backend
