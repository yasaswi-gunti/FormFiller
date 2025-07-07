import streamlit as st
import json
import csv
import tempfile
import os
import zipfile
import io
import time

from src.form_filler import FormFiller
from src.utils import get_output_file_name

@st.cache_resource
def get_form_filler():
    return FormFiller()

st.title("Consent Form Filler")

csv_file = st.file_uploader("Upload Player CSV", type="csv")
with st.expander("⬇️ Upload New Form and Coordiates (optional)"):
    col1, col2 = st.columns(2)
    with col1:
        pdf_file = st.file_uploader("Upload New Form Template", type="pdf")
    with col2:
        coords_file = st.file_uploader("Upload Coordinates JSON", type="json")

if csv_file and pdf_file and coords_file:
    st.success("All files uploaded! Ready to process.")
    # ff.load_statics(pdf_file, coords_file)
elif csv_file:
    st.toast("Csv File Uploaded!")
if csv_file:
    ff = get_form_filler()
    gbcol, dbcol = st.columns(2)
    with gbcol:
        generate_button = st.button("Generate PDFs")
    with dbcol:
        download_button_placeholder = st.empty()

    info_placeholder = st.empty()

    log_container = st.container()

    if generate_button:
        try:
            stringio = io.StringIO(csv_file.getvalue().decode("utf-8-sig"))
            reader = csv.DictReader(stringio)
            rows = list(reader)

            with tempfile.TemporaryDirectory() as tmpdir:
                output_dir = os.path.join(tmpdir, "output")
                for row in rows:
                    batch = row.get('batch', None)
                    playername = row.get('playersname', 'unknown')
                    file_name = get_output_file_name(playername)

                    if batch:
                        output_file_path = os.path.join(output_dir, batch, file_name)
                    else:
                        output_file_path = os.path.join(output_dir, file_name)

                    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
                    ff.fill(row, output_file_path)
                    log_container.write(f'Saved: {batch}/{file_name}')

                # Create ZIP
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zipf:
                    for root, _, files in os.walk(output_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, output_dir)
                            zipf.write(file_path, arcname=arcname)
                zip_buffer.seek(0)


                info_placeholder.success("PDFs generated!")
                download_button_placeholder.download_button("Download All Forms (ZIP)", zip_buffer, "filled_forms.zip", "application/zip")
        except Exception as e:
            st.error(f"Something went wrong: {e}")
