import zmq

def main():
    contexto = zmq.Context()

    # Socket ROUTER para clientes (facultades)
    frontend = contexto.socket(zmq.ROUTER)
    frontend.bind("tcp://10.43.103.220:5555")

    # Socket DEALER para trabajadores
    backend = contexto.socket(zmq.DEALER)
    backend.bind("tcp://10.43.103.220:5556")

    print("[Broker] En funcionamiento. Enrutando solicitudes...")

    # Enrutador proxy entre frontend y backend
    zmq.proxy(frontend, backend)

    # Cierre (nunca se llega aquí en la práctica)
    frontend.close()
    backend.close()
    contexto.term()

if __name__ == "__main__":
    main()