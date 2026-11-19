"""Root entry so `streamlit run streamlit_app.py` and Streamlit Cloud both find the app."""

from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).resolve().parent / "app" / "streamlit_app.py"), run_name="__main__")
