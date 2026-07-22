# 🕵️ Anonyx

**Anonyx** anonymizes personal data (PII) in free-form text — names, emails,
phone numbers, addresses, credit card numbers, and more — through a simple
Streamlit interface. It's built on top of the [PIISA](https://github.com/piisa)
toolchain via the [`pii-process`](https://pypi.org/project/pii-process/)
library, which combines rule-based and Transformer-based detection.

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/streamlit-app-red)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- 🔍 **Detects PII** in French or English text — names, emails, phone
  numbers, addresses, IDs, credit card numbers, and more.
- 🛡️ **Multiple anonymization policies** — replace with a type label
  (`<PERSON>`), fully redact, generate a realistic placeholder, or annotate
  the original value in place.
- 📁 **Paste text or upload a `.txt` file.**
- 📊 **Detection summary** — a chart and table of what was found and how
  often.
- ⬇️ **Download the anonymized result** as a text file.
- 💻 **Runs locally** — text is processed in your own session and isn't
  sent anywhere else.

## Demo


![Anonyx screenshot](/screenshot.png) 

## Getting started

### Prerequisites

- Python 3.9+

### Installation

```bash
git clone https://github.com/ismobaga/anonymizer.git
cd anonymizer
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

`pii-process[transformers]` needs PyTorch, which `pip install` fetches as a
large GPU-enabled build by default. If you don't have a GPU, install the
much smaller CPU-only build instead (do this *before or after*
`pip install -r requirements.txt`, it will replace the default one):

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

> The `transformers`-based detection models are downloaded automatically
> the first time you run the app, so the first analysis may take a bit
> longer.

### Run the app

This is a Streamlit app, so it must be started with the `streamlit` CLI —
running it with `python streamlit_app.py` will fail:

```bash
streamlit run streamlit_app.py
```

Then open the local URL Streamlit prints in your terminal (usually
`http://localhost:8501`).

## How it works

Anonyx wraps [`pii-process`](https://pypi.org/project/pii-process/), which
runs the full PIISA pipeline end to end:

1. **Detect** — extract candidate PII instances using regex and Transformer
   models (`pii-extract`).
2. **Decide** — reconcile and de-duplicate overlapping detections
   (`pii-decide`).
3. **Transform** — substitute each detected instance according to the
   chosen policy (`pii-transform`).

## Project structure

```
anonymizer/
├── streamlit_app.py   # Streamlit UI and processing logic
├── requirements.txt   # Python dependencies
└── README.md
```

## Roadmap

- [ ] Support for additional languages
- [ ] PDF / DOCX file input
- [ ] Configurable entity types to detect
- [ ] Deploy a public demo (Streamlit Community Cloud)

## Contributing

Issues and pull requests are welcome. If you find a bug or have an idea for
an improvement, feel free to open an issue.

## License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for details.
