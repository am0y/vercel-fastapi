from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import httpx
import asyncio
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

class InpaintRequest(BaseModel):
    prompt: str
    image_url: str
    mask_url: str

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

@app.post("/proxy/inpaint")
async def proxy_inpaint(request: InpaintRequest):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'x-fal-target-url': 'https://queue.fal.run/fal-ai/flux-pro/v1/fill',
        'Cookie': 'fal-app=true'
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Initial request
            response = await client.post(
                'https://3dcanvas.party/api/proxy',
                headers=headers,
                json=request.dict()
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)
            
            return response.json()
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/proxy/check/{request_id}")
async def check_status(request_id: str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Cookie': 'fal-app=true'
    }
    
    url = f"https://queue.fal.run/fal-ai/flux-pro/requests/{request_id}"
    headers['x-fal-target-url'] = url
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                'https://3dcanvas.party/api/proxy',
                headers=headers
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)
            
            return response.json()
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
