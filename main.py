import streamlit as st
import json
import whisper

st.set_page_config(page_title="Flexible RUBRIC Scoring Tool", layout="wide")
st.title("Flexible RUBRIC Scoring Tool")


# Load Model Whisper
@st.cache_resource
def load_model_whisper(model_name:str = "tiny"):
    model = whisper.load_model(model_name)
    return model

model = load_model_whisper()

# ===================== UPLOAD FILE =====================
uploaded_files = st.file_uploader(
    "Upload files (audio / video / dokumen)",
    accept_multiple_files=True
)

# ===================== DEFAULT RUBRIC =====================
DEFAULT_LABELS = {
    1: "Sangat baik",
    2: "Baik",
    3: "Cukup",
    4: "Kurang",
    5: "Sangat kurang"
}

# ===================== CONFIG SKOR =====================
max_score = st.number_input(
    "Jumlah skor maksimal",
    min_value=1,
    value=5,
    step=1
)

use_custom_rubric = st.checkbox("Input RUBRIC sendiri?", value=False)

# ===================== SESSION STATE INIT =====================
if "rubric_data" not in st.session_state:
    st.session_state.rubric_data = {}

if "questions" not in st.session_state:
    st.session_state.questions = {}

# ===================== MAIN PROCESS =====================
if uploaded_files:

    st.markdown("## Input Penilaian Per Video")

    for idx, file in enumerate(uploaded_files, start=1):
        filename = file.name

        with st.expander(f"🎥 Video {idx} - {filename}", expanded=False):

            # =====================
            # RUBRIC PER VIDEO
            # =====================
            st.markdown("### 📋 Input RUBRIC")

            if idx not in st.session_state.rubric_data:
                st.session_state.rubric_data[idx] = {}

            cols = st.columns(max_score)
            for score in range(1, max_score + 1):
                with cols[score - 1]:
                    default_value = DEFAULT_LABELS.get(score, f"Score {score}")

                    if use_custom_rubric:
                        label = st.text_input(
                            f"Score {score}",
                            value=st.session_state.rubric_data[idx].get(score, default_value),
                            key=f"rubric_{idx}_{score}"
                        )
                    else:
                        label = default_value
                        st.text(f"{score} - {label}")

                    st.session_state.rubric_data[idx][score] = label

            st.divider()

            # =====================
            # INPUT SOAL PER VIDEO
            # =====================
            st.markdown("### 📝 Input Soal")

            soal_text = st.text_area(
                f"Soal untuk video {idx}",
                value=st.session_state.questions.get(filename, ""),
                key=f"soal_{idx}",
                height=120
            )

            st.session_state.questions[filename] = soal_text

            st.divider()

            # =====================
            # PENILAIAN
            # =====================
            st.markdown("### ✅ Penilaian")

            rubric_for_video = st.session_state.rubric_data[idx]

            label_options = {
                score: f"{score} - {desc}"
                for score, desc in rubric_for_video.items()
            }

            selected_score = st.selectbox(
                "Pilih Skor",
                options=list(label_options.keys()),
                format_func=lambda x: label_options[x],
                key=f"select_{idx}"
            )

            st.session_state.rubric_data[idx]["selected_score"] = selected_score

    # ===================== PREVIEW =====================
    st.markdown("## 📊 Preview Hasil")

    final_result = {}

    for idx, file in enumerate(uploaded_files, start=1):
        filename = file.name
        rubric = st.session_state.rubric_data[idx]
        selected = rubric.get("selected_score")

        if selected:
            final_result[filename] = {
                "score": selected,
                "description": rubric[selected],
                "question": st.session_state.questions.get(filename, "")
            }

    st.json(final_result)

    # ===================== SIMPAN =====================
    if st.button("💾 Simpan ke JSON"):
        with open("scoring_result.json", "w") as f:
            json.dump(final_result, f, indent=4, ensure_ascii=False)
        st.success("Hasil berhasil disimpan ke scoring_result.json")