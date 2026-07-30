from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "AI Dashboard Backend Running"}

@app.get("/health")
def health():
    return {"status": "Backend is running"}