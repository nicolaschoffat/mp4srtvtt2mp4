import streamlit as st
import subprocess
from io import BytesIO
import os
import tempfile

# Cette ligne doit être tout en haut
st.set_page_config(page_title="Convertisseur MP4 avec Sous-titres", page_icon="🎬")

def burn_subtitles_into_video(video_file, subtitle_file):
    # Créer des fichiers temporaires pour la vidéo, les sous-titres et la sortie
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        temp_video.write(video_file.read())
        temp_video_path = temp_video.name

    subtitle_ext = os.path.splitext(subtitle_file.name)[1].lower()
    if subtitle_ext not in ['.srt', '.vtt']:
        raise ValueError("Format de sous-titres non pris en charge : .srt ou .vtt uniquement")

    subtitle_suffix = subtitle_ext
    with tempfile.NamedTemporaryFile(delete=False, suffix=subtitle_suffix) as temp_sub:
        temp_sub.write(subtitle_file.read())
        temp_sub_path = temp_sub.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_output:
        temp_output_path = temp_output.name

    # Construire la commande ffmpeg
    command = [
        "ffmpeg", "-y",
        "-i", temp_video_path,
        "-vf", f"subtitles='{temp_sub_path}'",
        "-c:a", "copy",
        temp_output_path
    ]

    subprocess.run(command, check=True)

    # Lire la vidéo modifiée dans un buffer
    with open(temp_output_path, "rb") as f:
        result_bytes = f.read()

    # Nettoyage
    os.remove(temp_video_path)
    os.remove(temp_sub_path)
    os.remove(temp_output_path)

    return BytesIO(result_bytes)

# Interface Streamlit
st.image("logo_googleworkspace.png", width=200)
st.title("Convertisseur MP4 avec Sous-titres Incrustés 🎬")

uploaded_video = st.file_uploader("Téléversez une vidéo MP4", type=["mp4"])
uploaded_subs = st.file_uploader("Téléversez un fichier de sous-titres (.srt ou .vtt)", type=["srt", "vtt"])

if uploaded_video is not None and uploaded_subs is not None:
    st.video(uploaded_video)
    if st.button("Incruster les sous-titres"):
        with st.spinner("Traitement de la vidéo en cours..."):
            try:
                final_video = burn_subtitles_into_video(uploaded_video, uploaded_subs)
                st.success("Sous-titres incrustés avec succès !")
                st.download_button(
                    label="Télécharger la vidéo MP4",
                    data=final_video,
                    file_name="video_avec_soustitres.mp4",
                    mime="video/mp4"
                )
            except subprocess.CalledProcessError as e:
                st.error("Erreur lors de l'exécution de ffmpeg. Détails :")
                st.code(e)
            except Exception as e:
                st.error("Une erreur s'est produite pendant le traitement :")
                st.code(str(e))
