# Accessible Infographic Converter (Backend)

[![Backend Framework](https://img.shields.io/badge/Backend-Django-092E20?style=flat-square&logo=django)](https://www.djangoproject.com/)
[![AI Engine](https://img.shields.io/badge/AI_Engine-U--M_GPT_Toolkit-00274C?style=flat-square)](https://its.umich.edu/)
[![Security](https://img.shields.io/badge/Security-Protected_Bridge-success?style=flat-square)](#)

The secure, robust backend engine for the Accessible Infographic Converter. This Django application acts as a secure processing gateway, extracting visual content, executing optical character recognition (OCR), prompting advanced AI models for descriptive narratives, and outputting highly structured, screen-reader-compliant PDF files.

---

## 🔒 Security & Backend Architecture

This server is designed to act as a **secure bridge** between user uploads and artificial intelligence APIs:

*   **API Token Obfuscation:** Under no circumstances are raw API credentials exposed to client browsers. All validation, handshakes, and secret keys are stored safely on the environment layer behind Django.
*   **Secure Pipelines:** Documents uploaded by users are packaged securely and dispatched through protected connections.
*   **Compliance Ready:** Specifically built to easily shift from private sandbox keys to the **U-M GPT Toolkit** (ITS) to guarantee compliance with University of Michigan data security policies.

---

## ⚙️ How the Backend Works

The platform operates as a cohesive **four-stage processing system** to seamlessly turn inaccessible visuals into screen-reader-friendly documents:

### 1. 📥 User Input & Platform Start (Frontend)
*   **Upload:** The user uploads an infographic image (PNG, JPG, WEBP) or an inaccessible PDF.
*   **Validation:** The frontend interface instantly validates the file type and registers it for processing.

### 2. 🔒 Secure Transit & Text Extraction (Backend)
*   **Encrypted Dispatch:** The file is safely dispatched over an encrypted HTTPS connection to our Django backend.
*   **OCR Parsing:** The backend parses the file and executes OCR (Optical Character Recognition) to extract the raw embedded text.

### 3. 🧠 Intelligent AI Reconstruction (Backend - Silent)
*   **Contextual Prompting:** The backend securely prompts the AI (such as the U-M GPT Toolkit) with the extracted raw text and custom structural rules.
*   **Logical Analysis:** The AI dynamically analyzes the layout, converting complex visuals (like flowchart decision trees or timelines) into logical, descriptive prose instead of flattening them into a confusing list of words.

### 4. 📄 Accessible PDF Generation & Delivery (Frontend/Backend)
*   **PDF Compilation:** The backend compiles a clean, tagged PDF featuring the logical text description on Page 1, and the original graphic (safely tagged with alt-text) on Page 2.
*   **Polished Interface:** The frontend receives the completed document and displays a polished, high-contrast, UM-themed download button for the user.

---

## 🛠️ Tech Stack
*   **Framework:** Django (Python)
*   **OCR Engine:** Tesseract OCR / PyPDF
*   **AI Integrations:** U-M GPT Toolkit / Gemini API
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
