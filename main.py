import shlex
import subprocess
import gzip
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from time import sleep
from pydantic import BaseModel

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Configuração (Global State)
# IP padrão (o App pode atualizar via API)
DEVICE_IP = "192.168.3.14:5555"

class ConnectRequest(BaseModel):
    ip: str

class AppCommandRequest(BaseModel):
    command: str

def run_adb_command(command_args):
    """Executa um comando ADB bruto via subprocesso"""
    # Adiciona -H e -P se necessário? Não, estamos rodando adb local no container.
    # O adb connect deve ter sido feito antes ou ser persistente.
    base_cmd = ["adb", "-s", DEVICE_IP, "shell"]
    full_cmd = base_cmd + command_args
    try:
        # print(f"Executando: {' '.join(full_cmd)}")
        result = subprocess.run(full_cmd, capture_output=True, text=True)
        return {"status": "success", "output": result.stdout}
    except Exception as e:
        print(f"Erro ADB: {e}")
        return {"status": "error", "message": str(e)}

@app.on_event("startup")
async def startup_event():
    print(f"🔌 Inicializando... IP alvo: {DEVICE_IP}")
    # Tenta conectar no startup
    # Se estivermos em host networking, o adb do container compartilha rede.
    try:
        print("Tentando conectar via ADB CLI...")
        # Separate IP and Port if needed, but adb connect handles host:port
        subprocess.run(["adb", "connect", DEVICE_IP], capture_output=True)
    except Exception as e:
        print(f"Aviso startup: {e}")

@app.post("/api/connect")
async def connect_device(req: ConnectRequest):
    """Conecta a um novo dispositivo IP"""
    global DEVICE_IP
    DEVICE_IP = req.ip
    print(f"🔌 Conectando ao {DEVICE_IP}...")
    # Executa adb connect
    result = subprocess.run(["adb", "connect", DEVICE_IP], capture_output=True, text=True)
    return {"status": "success", "output": result.stdout, "current_ip": DEVICE_IP}

@app.get("/api/status")
async def get_status():
    return {"ip": DEVICE_IP}

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "ip": DEVICE_IP})

@app.post("/api/app")
async def send_complex_app(req: AppCommandRequest):
    """Envia um comando de app complexo via AM START"""
    try:
        args = shlex.split(req.command)
        cmd = ["am", "start", "-n"] + args
        return run_adb_command(cmd)
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/key/{keycode}")
async def send_key(keycode: int):
    """Envia um evento de tecla"""
    return run_adb_command(["input", "keyevent", str(keycode)])

@app.post("/text")
async def send_text(text: str):
    """Envia texto"""
    formatted_text = text.replace(" ", "%s")
    return run_adb_command(["input", "text", formatted_text])

@app.post("/command/raw")
async def send_raw(cmd: str):
    """Executa comandos específicos"""
    return run_adb_command(cmd.split(" "))

@app.post("/app/{app}")
async def send_app(app: str):
    """Envia app simplificado"""
    if app == "alanzoka":
        run_adb_command(["input", "keyevent", "3"])
        run_adb_command(["am", "force-stop", "com.amazon.firetv.youtube"])
        run_adb_command(["am", "start", "-n", "com.amazon.firetv.youtube/dev.cobalt.app.MainActivity"])
        sleep(4)
        run_adb_command(["input", "keyevent", "66"])
    else:
        return run_adb_command(["am", "start", "-n", app])

# live preview from device screen
@app.get("/live")
async def live_preview():
    """Mostra uma prévia do dispositivo via MJPEG (Compressed Screencap)"""
    def generate_frames_clean():
        # Utiliza screencap com compressão gzip
        adb_cmd = f"adb -s {DEVICE_IP} shell \"while true; do screencap | gzip -1; echo '|EOF|'; done\""
        adb_proc = subprocess.Popen(adb_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        
        buffer = b""
        delimiter = b"|EOF|\n"
        
        try:
            while True:
                chunk = adb_proc.stdout.read(65536)
                if not chunk: break
                buffer += chunk
                
                while True:
                    pos = buffer.find(delimiter)
                    if pos == -1: break
                    
                    gz_data = buffer[:pos]
                    buffer = buffer[pos + len(delimiter):]
                    
                    try:
                        raw_data = gzip.decompress(gz_data)
                        if len(raw_data) > 12:
                            w = int.from_bytes(raw_data[0:4], 'little')
                            h = int.from_bytes(raw_data[4:8], 'little')
                            pixels = raw_data[12:]
                            
                            # Transcode usando ffmpeg (que deve estar no container agora)
                            conv = subprocess.run([
                                "ffmpeg", "-y",
                                "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{w}x{h}",
                                "-i", "-",
                                "-f", "image2", "-vcodec", "mjpeg", "-q:v", "5",
                                "-vf", "scale=720:-1",
                                "-"
                            ], input=pixels, capture_output=True)
                            
                            if conv.stdout:
                                yield (b'--frame\r\n'
                                       b'Content-Type: image/jpeg\r\n\r\n' + conv.stdout + b'\r\n')
                    except Exception:
                        pass
        except Exception:
            pass
        finally:
            adb_proc.terminate()

    return StreamingResponse(generate_frames_clean(), media_type="multipart/x-mixed-replace; boundary=frame")
