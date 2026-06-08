from fastapi import FastAPI

app = FastAPI(
    title = "Network Intelligence Simulator",
    description = "Python backed for receiving telecom network metrics",
    version = "0.1.0"
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

