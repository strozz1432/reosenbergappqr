# Fixed port so bookmarks like http://192.168.x.x:8000/teacher stay valid.
Set-Location $PSScriptRoot
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
