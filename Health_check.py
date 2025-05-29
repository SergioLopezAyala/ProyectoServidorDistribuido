import time
import zmq
import subprocess

IP_SERVIDOR = "10.43.103.220"  # IP del servidor principal
IP_REPLICA = "10.43.103.169"      # IP de esta máquina (donde se lanzará la réplica)
PUERTO = 5555
TIEMPO_CHECK = 2  # segundos
INTENTOS_FALLO = 3

def servidor_esta_activo():
    contexto = zmq.Context()
    socket = contexto.socket(zmq.DEALER)

    identidad = b"health_checker"
    socket.setsockopt(zmq.IDENTITY, identidad)
    socket.connect(f"tcp://{IP_SERVIDOR}:{PUERTO}")

    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)

    try:
        socket.send(b"ping")
        print("[HealthCheck] Ping enviado...")

        socks = dict(poller.poll(1500))  # Espera 1.5 segundos

        if socket in socks:
            respuesta = socket.recv()
            print(f"[HealthCheck] Respuesta recibida: {respuesta}")
            return respuesta == b"pong"
        else:
            print("[HealthCheck] Timeout: no se recibió pong.")
            return False

    except Exception as e:
        print(f"[HealthCheck] Error al contactar el servidor: {e}")
        return False
    finally:
        socket.close()
        contexto.term()

def activar_replicado():
    print("[HealthCheck] Iniciando servidor réplica...")
    subprocess.Popen(["python3", "Servidor.py"])

def main():
    print("[HealthCheck] Iniciando monitoreo...")

    fallos = 0
    while True:
        activo = servidor_esta_activo()
        if activo:
            print("[HealthCheck] Servidor OK")
            fallos = 0
        else:
            fallos += 1
            print(f"[HealthCheck] Falla detectada ({fallos})")

        if fallos >= INTENTOS_FALLO:
            activar_replicado()
            break

        time.sleep(TIEMPO_CHECK)

if __name__ == "__main__":
    main()