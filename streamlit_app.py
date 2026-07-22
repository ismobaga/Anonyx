"""
Anonyx — a small Streamlit app that anonymizes personal data (PII)
found in free text, using the pii-process / PIISA toolchain.
"""

from collections import Counter

import altair as alt
import pandas as pd
import streamlit as st

from pii_process.api import PiiTextProcessor
from pii_data.types.doc import DocumentChunk

# --------------------------------------------------------------------------
# Page setup
# --------------------------------------------------------------------------

st.set_page_config(
    page_title="Anonyx — Anonymiseur de texte",
    page_icon="🕵️",
    layout="centered",
)

LANGUAGES = {"Français": "fr", "English": "en"}

POLICIES = {
    "label": "Remplace chaque donnée par son type, ex. <PERSON>",
    "redact": "Remplace chaque donnée par <PII>",
    "placeholder": "Remplace chaque donnée par un texte de substitution réaliste",
    "annotate": "Garde la valeur d'origine et l'annote, ex. <PERSON:Jean Dupont>",
    "passthrough": "Ne modifie rien (utile pour vérifier la détection seule)",
}

EXAMPLES = {
    "fr": (
        "Bonjour, je m'appelle Jean Dupont. Vous pouvez me joindre au "
        "06 12 34 56 78 ou par mail à jean.dupont@example.com. "
        "J'habite au 12 rue de la Paix, Paris. Mon numéro de carte est "
        "4539 1488 0343 6467."
    ),
    "en": (
        "Hello, my name is John Smith. You can reach me at "
        "(415) 555-0198 or john.smith@example.com. I live at "
        "221B Baker Street, London. My card number is "
        "4539 1488 0343 6467."
    ),
}


# --------------------------------------------------------------------------
# Cached processor — building it loads NLP models, so we only want to
# pay that cost once per (language, policy) combination.
# --------------------------------------------------------------------------

@st.cache_resource(show_spinner=False)
def get_processor(lang: str, policy: str) -> PiiTextProcessor:
    return PiiTextProcessor(lang=lang, default_policy=policy)


def anonymize(text: str, lang: str, policy: str):
    """Run detection + transformation, returning (clean_text, entities)."""
    proc = get_processor(lang, policy)
    chunk = DocumentChunk(id=1, data=text, context={"lang": lang})
    out_chunk, piic = proc.process(chunk)
    entities = [p.fields for p in piic]
    return out_chunk.data, entities


# --------------------------------------------------------------------------
# Sidebar controls
# --------------------------------------------------------------------------

with st.sidebar:
    st.header("⚙️ Paramètres")

    lang_label = st.selectbox("Langue du texte", list(LANGUAGES.keys()))
    lang = LANGUAGES[lang_label]

    policy = st.selectbox(
        "Politique d'anonymisation",
        list(POLICIES.keys()),
        format_func=lambda p: p,
        help="Détermine comment chaque donnée détectée est remplacée.",
    )
    st.caption(POLICIES[policy])

    st.divider()
    st.caption(
        "Propulsé par [pii-process](https://pypi.org/project/pii-process/), "
        "basé sur des modèles Transformers pour la détection."
    )


# --------------------------------------------------------------------------
# Main UI
# --------------------------------------------------------------------------

st.title("🕵️ Anonyx")
st.subheader("Anonymisez les données personnelles dans vos textes")
st.write(
    "Collez un texte contenant des informations personnelles (noms, emails, "
    "téléphones, adresses…) et laissez Anonyx les détecter et les remplacer."
)

if "text_input" not in st.session_state:
    st.session_state.text_input = ""

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("📋 Charger un exemple"):
        st.session_state.text_input = EXAMPLES.get(lang, EXAMPLES["fr"])
with col2:
    if st.button("🗑️ Effacer"):
        st.session_state.text_input = ""

message = st.text_area(
    "Texte à anonymiser",
    key="text_input",
    height=180,
    placeholder="Tapez ou collez votre texte ici...",
)

uploaded_file = st.file_uploader("…ou importez un fichier .txt", type=["txt"])
if uploaded_file is not None:
    message = uploaded_file.read().decode("utf-8", errors="ignore")
    st.text_area("Contenu importé", message, height=150, disabled=True)

run = st.button("🔍 Anonymiser", type="primary", use_container_width=True)

if run:
    if not message or not message.strip():
        st.warning("Veuillez saisir ou importer du texte avant de continuer.")
    else:
        with st.spinner(
            "Analyse en cours… (le premier lancement peut télécharger des "
            "modèles et prendre un peu plus de temps)"
        ):
            try:
                clean_text, entities = anonymize(message, lang, policy)
            except Exception as exc:  # surface a friendly error instead of a raw traceback
                st.error(f"Une erreur est survenue pendant le traitement : {exc}")
            else:
                st.subheader("✅ Texte anonymisé")
                st.text_area("Résultat", clean_text, height=180)
                st.download_button(
                    "⬇️ Télécharger le résultat",
                    data=clean_text,
                    file_name="texte_anonymise.txt",
                    mime="text/plain",
                )

                st.subheader("📊 Données détectées")
                if not entities:
                    st.info("Aucune donnée personnelle détectée dans ce texte.")
                else:
                    counts = Counter(e["type"] for e in entities)
                    df = pd.DataFrame(
                        {"type": list(counts.keys()), "occurrences": list(counts.values())}
                    ).sort_values("occurrences", ascending=False)

                    chart = (
                        alt.Chart(df)
                        .mark_bar()
                        .encode(
                            x=alt.X("occurrences:Q", title="Occurrences"),
                            y=alt.Y("type:N", sort="-x", title="Type de donnée"),
                            tooltip=["type", "occurrences"],
                        )
                    )
                    st.altair_chart(chart, use_container_width=True)

                    with st.expander("Voir le détail des entités détectées"):
                        st.dataframe(
                            pd.DataFrame(entities)[["type", "value"]],
                            use_container_width=True,
                            hide_index=True,
                        )

st.divider()
st.caption(
    "Anonyx traite le texte localement dans cette session ; rien n'est "
    "envoyé ailleurs que ce processus. Projet : "
    "[ismobaga/anonymizer](https://github.com/ismobaga/anonymizer)."
)

