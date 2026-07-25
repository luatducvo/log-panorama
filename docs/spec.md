# Spec: Panorama Location Log Sheet

## Objective
Build a mobile-friendly Streamlit app for managing 360 panorama location logs. Users can create, edit, delete, search, and view records with these fields: place code, place name, hotspot, and destination hotspot. Data is persisted to Google Sheets through a service account.

## Tech Stack
- Python 3.12
- Streamlit for UI
- gspread and google-auth for Google Sheets API
- pandas for table display
- pytest for unit tests
- uv for dependency management

## Commands
- Install/sync: `uv sync`
- Dev: `uv run streamlit run app.py`
- Test: `uv run pytest`

## Project Structure
- `app.py`: Streamlit entrypoint
- `log_panorama/models.py`: record model and validation
- `log_panorama/sheets.py`: Google Sheets gateway
- `tests/`: unit tests
- `.streamlit/secrets.example.toml`: example Streamlit secrets

## Code Style
```python
record = PanoramaLocation.from_form(
    place_code="PANO-001",
    place_name="Main Lobby",
    hotspot="door-east",
    connects_to="hallway-west",
)
```
Use explicit names, small functions, and keep Google Sheets I/O out of UI code.

## Testing Strategy
Unit-test pure validation and Google Sheet row mapping with fake worksheets. Do not call the real Google API in automated tests.

## Boundaries
- Always: validate required inputs, preserve secrets outside source control, run tests before completion.
- Ask first: changing the Google Sheet schema or adding authentication beyond Streamlit secrets.
- Never: commit real service account keys or private spreadsheet data.

## Success Criteria
- Users can add or update a panorama hotspot record from a mobile-friendly form.
- Users can view, search, and delete records.
- Data persists to the configured Google Sheet worksheet.
- Project dependencies are managed by `uv`.
- `uv run pytest` passes.
