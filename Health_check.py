import time
import zmq
import subprocess
import psutil

IP_SERVIDOR = "10.43.103.220"
PUERTO = 5555
TIEMPO_CHECK = 2  # segundos entre chequeos
INTENTOS_FALLO = 3

LOG_FILE = "log_healthcheck.txt"

def log(mensaje):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {mensaje}\n")

def servidor_esta_activo():
    contexto = zmq.Context()
    socket = contexto.socket(zmq.DEALER)
    socket.setsockopt(zmq.IDENTITY, b"health_checker")
    socket.setsockopt(zmq.LINGER, 0)

    try:
        socket.connect(f"tcp://{IP_SERVIDOR}:{PUERTO}")
        inicio = time.time()
        socket.send(b"ping")

        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)
        socks = dict(poller.poll(1500))  # 1.5 segundos

        if socket in socks:
            respuesta = socket.recv()
            fin = time.time()
            latencia = fin - inicio
            cpu = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory().percent
            log(f"Servidor respondió en {latencia:.4f}s | CPU: {cpu}% | RAM: {ram}%")
            return respuesta == b"pong"
        else:
            log("Timeout esperando respuesta del servidor.")
            return False
    except Exception as e:
        log(f"Error al contactar al servidor: {e}")
        return False
    finally:
        socket.close()
        contexto.term()

def activar_replicado():
    log("Iniciando servidor réplica por fallo del principal.")
    print("[HealthCheck] Iniciando servidor réplica...")
    subprocess.Popen(["python3", "ServidorReplica.py"])

def main():
    print("[HealthCheck] Iniciando monitoreo...")
    log("Inicio de monitoreo de estado del servidor principal.")
    fallos = 0

    while True:
        activo = servidor_esta_activo()

        if activo:
            print("[HealthCheck] Servidor OK")
            fallos = 0
        else:
            fallos += 1
            log(f"Falla detectada #{fallos}")
            print(f"[HealthCheck] Falla detectada ({fallos})")

        if fallos >= INTENTOS_FALLO:
            activar_replicado()
            break

        time.sleep(TIEMPO_CHECK)

if __name__ == "__main__":
    main()
