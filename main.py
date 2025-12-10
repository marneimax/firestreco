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
DEVICE_IP = "192.168.3.14:5555"

class ConnectRequest(BaseModel):
    ip: str

class AppCommandRequest(BaseModel):
    command: str

def run_adb_command(command_args):
    """Executa um comando ADB bruto"""
    base_cmd = ["adb", "-s", DEVICE_IP, "shell"]
    full_cmd = base_cmd + command_args
    try:
        result = subprocess.run(full_cmd, capture_output=True, text=True)
        return {"status": "success", "output": result.stdout}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.on_event("startup")
async def startup_event():
    print(f"🔌 Inicializando... IP padrão: {DEVICE_IP}")
    # Não conecta automaticamente no startup para dar chance do frontend enviar o IP correto
    # Mas se quiser manter o comportamento original de tentar o default:
    # subprocess.run(["adb", "connect", DEVICE_IP])

@app.post("/api/connect")
async def connect_device(req: ConnectRequest):
    """Conecta a um novo dispositivo IP"""
    global DEVICE_IP
    DEVICE_IP = req.ip
    print(f"🔌 Conectando ao {DEVICE_IP}...")
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
    # Exemplo: command="com.pkg/.Act --es 'foo' 'bar'"
    # O run_adb_command espera uma lista. Vamos usar shlex para dividir corretamente respeitando aspas.
    try:
        args = shlex.split(req.command)
        # Se o usuário não incluiu 'am start -n', podemos flexibilizar ou assumir que ele manda só os args do start?
        # A request original era 'am start -n {app}'
        # Vamos assumir que o 'command' é o argumento para o 'am start -n' OU um comando completo?
        # O prompt diz: "arrumar a rota de app pra aceitar strings complexas" e "os dados serão salvos em objetos... com sugestão"
        # Melhor abordagem: Se o usuário clica num botão customizado, ele pode querer mandar qualquer coisa.
        # Mas para manter compatibilidade com a ideia de "lançar app", vamos assumir que o input é o TARGET do start.
        
        # Se o input começar com "am " ou "input ", talvez devêssemos rodar direto?
        # O requisito é "rota de app". Então implicitamente é um 'am start'.
        # Vamos construir: am start -n <command>
        
        # POREM, o exemplo do switch tinha 'com.amazon... t4375'. Isso implica argumentos EXTRAS após o componente.
        # Então vamos fazer: cmd = ["am", "start", "-n"] + args
        
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
    """Envia texto (substitui espaços por %s para o Android entender)"""
    formatted_text = text.replace(" ", "%s")
    return run_adb_command(["input", "text", formatted_text])

@app.post("/command/raw")
async def send_raw(cmd: str):
    """Executa comandos específicos como screencap ou settings"""
    # Atenção: cmd deve vir como string única, aqui quebramos por espaço simples
    return run_adb_command(cmd.split(" "))

@app.post("/app/{app}")
async def send_app(app: str):
    """Envia um evento de tecla"""
    if app == "alanzoka":
        run_adb_command(["input", "keyevent", "3"])
        run_adb_command(["am", "force-stop", "com.amazon.firetv.youtube"])
        run_adb_command(["am", "start", "-n", "com.amazon.firetv.youtube/dev.cobalt.app.MainActivity"])
        # sleep(2)
        # run_adb_command(["input", "keyevent", "19"])
        # sleep(2)
        # run_adb_command(["input", "keyevent", "66"])
        # sleep(2)
        # run_adb_command(["input", "text", "alanzoka"])
        sleep(4)
        run_adb_command(["input", "keyevent", "66"])

    else:
        # switch = {        
        #     "youtube": "com.amazon.firetv.youtube/dev.cobalt.app.MainActivity",
        #     "youtube busca": "com.amazon.firetv.youtube/dev.cobalt.app.MainActivity t4375",
        #     # "netflix": "com.netflix.mediaclient/com.netflix.mediaclient.ui.launcher.LauncherActivity",
        #     "hbo": "com.hbo.hbonow/com.wbd.beam.BeamActivity",
        #     "watch": "com.softwillians.watchtv/.MainActivity",
        #     "twitch": "tv.twitch.android.viewer/tv.twitch.starshot64.app.StarshotActivity",        
        # }
        # app = switch.get(app, app)
        return run_adb_command(["am", "start", "-n", app])

# live preview from device screen
@app.get("/live")
async def live_preview():
    """Mostra uma prévia do dispositivo via MJPEG (Compressed Screencap)"""
    def generate_frames():
        # Utiliza screencap com compressão gzip no dispositivo para reduzir tráfego
        # Adiciona um marcador |EOF| para facilitar o split
        adb_cmd = f"adb -s {DEVICE_IP} shell \"while true; do screencap | gzip -1; echo '|EOF|'; done\""
        
        # O ffmpeg será inicializado dinamicamente quando soubermos a resolução
        ffmpeg_proc = None
        adb_proc = None

        try:
            adb_proc = subprocess.Popen(adb_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            
            buffer = b""
            delimiter = b"|EOF|\n"
            
            while True:
                chunk = adb_proc.stdout.read(65536)
                if not chunk:
                    break
                buffer += chunk
                
                while True:
                    # Tenta encontrar o delimitador
                    # Nota: o echo adiciona \n
                    pos = buffer.find(delimiter)
                    if pos == -1:
                        break
                    
                    # Extrai o frame comprimido (gzip)
                    # O delimitador está APÓS o gzip.
                    # Mas o comando é `gzip ...; echo ...`
                    # Então o gzip escreve stdout, fecha. Echo escreve.
                    # Pode ter bytes extras de newline do gzip? Não, gzip é binário.
                    gz_data = buffer[:pos]
                    buffer = buffer[pos + len(delimiter):]
                    
                    try:
                        # Descomprime
                        raw_data = gzip.decompress(gz_data)
                        
                        # Screencap header: 12 bytes (Width, Height, Format) - Little Endian
                        # Format: 1=RGBA, 5=RGBA? Geralmente 1
                        if len(raw_data) > 12:
                            w = int.from_bytes(raw_data[0:4], byteorder='little')
                            h = int.from_bytes(raw_data[4:8], byteorder='little')
                            # f = int.from_bytes(raw_data[8:12], byteorder='little')
                            pixels = raw_data[12:]
                            
                            # Inicializa FFmpeg se mudou resolução ou primeira vez
                            if ffmpeg_proc is None:
                                ffmpeg_cmd = [
                                    "ffmpeg",
                                    "-f", "rawvideo",
                                    "-pix_fmt", "rgba", # screencap geralmente é RGBA
                                    "-s", f"{w}x{h}",
                                    "-i", "-",
                                    "-f", "mjpeg",
                                    "-q:v", "3",
                                    "-vf", "scale=720:-1", # Reduz para 720p para economizar banda do browser se a fonte for 1080p
                                    "-frames:v", "1",
                                    "-nostats", "-loglevel", "0",
                                    "-"
                                ]
                                # Nota: rodar 1 frame por vez no FFmpeg é ineficiente (startup cost).
                                # O ideal é manter o pipe aberto. Mas o rawvideo exige stream contínuo sem cabeçalhos repetidos.
                                # Se enviarmos os pixels continuamente, funciona.
                                # Mas precisamos garantir o sync.
                                
                                # Vamos tentar modo persistente:
                                ffmpeg_cmd = [
                                    "ffmpeg",
                                    "-f", "rawvideo",
                                    "-pix_fmt", "rgba",
                                    "-s", f"{w}x{h}",
                                    "-i", "-",
                                    "-f", "mjpeg",
                                    "-q:v", "3",
                                    "-vf", "scale=720:-1",
                                    "-nostats", "-loglevel", "0",
                                    "-"
                                ]
                                ffmpeg_proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

                            # Envia pixels para o FFmpeg
                            ffmpeg_proc.stdin.write(pixels)
                            ffmpeg_proc.stdin.flush()
                            
                            # Lê o frame MJPEG do FFmpeg
                            # Como ler exatamente 1 frame JPEG do stream continuo?
                            # Precisamos parsear o MJPEG de saída também.
                            # FFmpeg em modo mjpeg solta JPEGs concatenados.
                            
                            # Pequeno hack: como estamos num loop Python controlado frame-a-frame (devido ao gzip),
                            # talvez seja mais fácil rodar o FFmpeg para converter 1 frame e fechar?
                            # "startup cost" do ffmpeg é 10-20ms? Pode ser aceitável para 10fps.
                            # Vamos tentar pipe persistente primeiro, mas preciso ler a saída.
                            
                            # Leitura não-blocante ou ler até o fim do JPEG?
                            # O output do ffmpeg vai para um buffer de leitura
                            pass 

                        # ... (continuando a lógica de leitura do ffmpeg abaixo)
                    except Exception as e:
                        print(f"Frame error: {e}")
                        continue
            
            # (Para simplificar a implementação dentro deste bloco 'while', 
            #  vou refazer a estrutura para ler o output do ffmpeg de forma assincrona ou intercalada?
            #  Intercalada é difícil porque ffmpeg pode bufferizar.
            #  
            #  Solução Alternativa: Python converte Raw -> JPEG usando biblioteca padrão se 'ffmpeg' for complexo de sincronizar?
            #  Não, usuário quer velocidade.
            # 
            #  Vamos usar a abordagem 'Transcode sem estado': 
            #  A cada frame recebido -> subprocess.run(ffmpeg single frame) -> yield output.
            #  É menos eficiente mas garante que não travamos no pipe.)
            
            pass 

        except Exception as e:
            print(f"Stream error: {e}")
        finally:
            if adb_proc: adb_proc.terminate()
            if ffmpeg_proc: ffmpeg_proc.terminate()

    # --- Reimplementação Limpa com Transcode Frame-a-Frame ---
    def generate_frames_clean():
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
                            
                            # Transcode único frame
                            # Input: raw stdin -> Output: mjpeg stdout
                            # -y: overwrite
                            # -f rawvideo ... -i - : lê do stdin
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
