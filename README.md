# SiPHY Protocol Assistant

SiPHY is a multi-mode protocol assistant for Ethernet (and other protocols like PCIe, UCIe). It’s built to help silicon designers, system integrators, and verification engineers explore tradeoffs, understand clause behavior, and debug protocol issues.

## Supported Modes

- **Strict Clause Mode**  
  Exact clause-level summaries. No added commentary.

- **Smart Designer Mode**  
  Explains tradeoffs, caveats, and real-world industry practices using clause metadata and annotated summaries.

- **Expert Context Mode**  
  Includes clause insights, vendor behavior, and broader architectural context. Suitable for advanced design queries and competitive debugging.

---

## Example Use Cases

- “What happens during lane deskew in 25GBASE-R?”
- “Compare 64b/66b to 8b/10b encoding in 10G Ethernet.”
- “Why does RS-FEC reduce packet drops in PAM4 links?”
- “Can I bypass Clause 74 if I only need short reach?”
- “Explain what breaks when BER is too high for Clause 78 FEC”

---

## Setup Instructions

1. **Clone this repo** or extract the `.zip` archive.
2. **Install dependencies** (Python 3.10+ required):
   ```bash
   pip install -r requirements.txt
   ```
3. **Add your OpenAI key** to `.env`:
   ```
   OPENAI_API_KEY=sk-...
   ```
4. **Launch the app**:
   ```bash
   streamlit run streamlit_app.py
   ```

Or use the `.bat` launcher (Windows):
```
run_siphy.bat
```

---

## Folder Structure

- `streamlit_app.py` – Launches the UI and coordinates chat logic
- `utils.py` – Clause parser, PDF logic, OpenAI interaction
- `ethernet_bot.py` – Query-to-answer transformer
- `metadata.json` – Clause summaries and annotations
- `vectorstore/` – FAISS index and embeddings
- `screenshots/` – UI examples for documentation
- `exports/` – PDF history exports
- `run_siphy.bat` – One-click Windows launcher
- `requirements.txt` – Dependency list

---

© Siemens Internal Demo Tool | Created by Siemens EDA CLS team

