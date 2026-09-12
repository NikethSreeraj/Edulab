# Edulab

An educational all-in-one application with a browser workspace, local user data, PCM tools, coding practice, RAG search, and optional Google Drive sync.

## Run locally

```powershell
.\.venv\Scripts\python.exe run_web.py
```

The launcher opens `http://127.0.0.1:5000` automatically. You can also open it manually.

The web layers are organized as **EduLab** (application), **EduCore** (AI),
**EduSim** (HTML5 simulators), **EduCalc** (calculators), and **EduEngine 1**
(shared runtime).

## Build Windows EXE

Run PowerShell from the repository root:

```powershell
.\build_windows.ps1
```

The installer-free executable is created at `dist\Edulab.exe`.

## Google Drive setup

Drive sync is optional. In Google Cloud Console, enable the Google Drive API,
create an OAuth Desktop application, download its client JSON, and save it as
`app\data\google_client_secret.json`. Open Settings in Edulab and choose
**Connect Google Drive**. The OAuth token is stored locally in
`app\data\google_token.json`; do not commit either file.

## EduCore AI

The AI panel is lazy-loaded: the configured model is contacted only after the
student opens EduCore chat. Set `EDULAB_LLM_MODEL` to the quantized Ollama tag
installed on the machine.
EduCore retrieves only relevant knowledge, uses simulator context and
calculators when needed, and searches the web for current or explicitly
requested information. Image reading uses an Ollama vision model through
`EDULAB_VISION_MODEL`. Image generation is provider-neutral and requires
`EDULAB_IMAGE_API_URL`.

## Version

v1.1
