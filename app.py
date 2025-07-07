import streamlit as st
import json
import csv
import tempfile
import os
import zipfile
import io

st.set_page_config(
    page_title="Consent Form Filler",
    page_icon="💾"
)

from src.form_filler import FormFiller
from src.utils import get_output_file_name

@st.cache_resource
def get_form_filler(pdf_file=None, coords_file=None):
    return FormFiller(pdf_file, coords_file)

st.title("Consent Form Filler")

csv_file = st.file_uploader("Upload Player CSV", type="csv")
with st.expander("⬇️ Upload New Form and Coordiates (optional)"):
    col1, col2 = st.columns(2)
    with col1:
        pdf_file = st.file_uploader("Upload New Form Template", type="pdf")
    with col2:
        coords_file = st.file_uploader("Upload Coordinates JSON", type="json")
if csv_file:
    st.toast("Csv File Uploaded!")
if pdf_file:
    st.toast("New Template File Uploaded!")
if coords_file:
    st.toast("New Coordinates File Uploaded!")

# Initialize session state variables
if 'generation_complete' not in st.session_state:
    st.session_state['generation_complete'] = False
if 'zip_buffer' not in st.session_state:
    st.session_state['zip_buffer'] = None
    

if csv_file:
    gbcol, dbcol = st.columns(2)
    with gbcol:
        generate_button = st.button("Generate PDFs")
    with dbcol:
        download_button_placeholder = st.empty()
    
    info_placeholder = st.empty()

    current_file_col, progress_col = st.columns(2)
    with current_file_col:
        current_file = st.empty()
    with progress_col:
        progress_holder = st.empty()

    if generate_button:
        st.session_state['generation_complete'] = False
        if csv_file and pdf_file and coords_file:
            ff = get_form_filler(pdf_file.getvalue(), coords_file.getvalue())
        elif csv_file:
            ff = get_form_filler()
        try:
            stringio = io.StringIO(csv_file.getvalue().decode("utf-8-sig"))
            reader = csv.DictReader(stringio)
            rows = list(reader)

            with tempfile.TemporaryDirectory() as tmpdir:
                output_dir = os.path.join(tmpdir, "output")
                files_count, total_files = 0, len(rows)

                for row in rows:
                    batch = row.get('batch', None)
                    playername = row.get('playersname', 'unknown')
                    file_name = get_output_file_name(playername)

                    if batch:
                        output_file_path = os.path.join(output_dir, batch, file_name)
                        log_path = f"{batch}/{file_name}"
                    else:
                        output_file_path = os.path.join(output_dir, file_name)
                        log_path = file_name

                    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
                    current_file.write(f'Filling: {log_path}')
                    ff.fill(row, output_file_path)
                    files_count += 1
                    progress_holder.write(f"Forms Filled : **{files_count} / {total_files}**")
                
                current_file.write('')
                progress_holder.write('')

                # Create ZIP
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zipf:
                    for root, _, files in os.walk(output_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, output_dir)
                            zipf.write(file_path, arcname=arcname)
                zip_buffer.seek(0)

                st.session_state['generation_complete'] = True
                st.session_state['zip_buffer'] = zip_buffer.getvalue()

        except Exception as e:
            st.error(f"Something went wrong: {e}")

    if st.session_state.get('generation_complete'):
        info_placeholder.success("Forms Filled Successfully! Download the zip file")

        download_button_placeholder.download_button(
            "Download All Forms (ZIP)",
            st.session_state['zip_buffer'],
            "filled_forms.zip",
            "application/zip"
        )
