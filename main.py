"""Legacy desktop entrypoint has been retired.

Use the web stack instead:
1) Backend API: uvicorn app.main:app --reload --app-dir backend
2) Frontend UI: npm run dev (from frontend/)
"""


if __name__ == "__main__":
    print("Desktop (tkinter) mode is retired.")
    print("Run backend: uvicorn app.main:app --reload --app-dir backend")
    print("Run frontend: cd frontend && npm run dev")
