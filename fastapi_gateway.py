from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import httpx, os, subprocess, pathlib

app = FastAPI()
TGI = os.getenv("TGI_HOST", "http://localhost:8080")
MODEL_DIR = pathlib.Path("/models")

@app.get("/admin/models")
def list_models():
    return [p.name for p in MODEL_DIR.iterdir() if p.is_dir()]

@app.post("/admin/download")
def download_model(model_id: str):
    target = MODEL_DIR / model_id.replace("/", "_")
    if target.exists():
        return {"msg": f"{model_id} 已存在"}
    subprocess.run([
        "huggingface-cli", "snapshot", model_id, "--local-dir", str(target)
    ], check=True)
    return {"msg": f"{model_id} 已下載"}

@app.api_route("/v1/{path:path}", methods=["GET", "POST", "OPTIONS"])
async def proxy_to_tgi(path: str, request: Request):
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.request(
            method=request.method,
            url=f"{TGI}/v1/{path}",
            headers={k: v for k, v in request.headers.items() if k.lower() != "host"},
            content=await request.body()
        )
        return StreamingResponse(response.aiter_raw(), status_code=response.status_code)