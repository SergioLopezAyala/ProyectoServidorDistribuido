import subprocess
import time
import argparse
import itertools
from datetime import datetime

# Global configurations
SEMESTRE = "2025-10"
FACULTAD_BASE_LISTEN_PORT = 7000
MAX_PROGRAMS_PER_FACULTY = 5
LOG_FILE = "log_superlanzador.txt"

PROGRAM_TEMPLATES = [
    {"nombre_base": "Sistemas"},
    {"nombre_base": "Civil"},
    {"nombre_base": "Industrial"},
    {"nombre_base": "Electronica"},
    {"nombre_base": "Ambiental"},
    {"nombre_base": "Mecanica"},
    {"nombre_base": "Quimica"},
    {"nombre_base": "Arquitectura"},
    {"nombre_base": "Diseno"},
    {"nombre_base": "Medicina"},
    {"nombre_base": "Software"},
    {"nombre_base": "Telecom"},
    {"nombre_base": "Biomecanica"},
    {"nombre_base": "Petroleos"},
    {"nombre_base": "Minas"},
]

def log_event(mensaje):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{now}] {mensaje}\n")

def generate_faculty_configs(num_faculties, salones_por_programa, labs_por_programa):
    faculties = []
    program_template_cycler = itertools.cycle(PROGRAM_TEMPLATES)
    
    for i in range(num_faculties):
        faculty_name = f"Facultad_{i+1}"
        faculty_listen_port = FACULTAD_BASE_LISTEN_PORT + i 
        
        programs_for_faculty = []
        for j in range(MAX_PROGRAMS_PER_FACULTY):
            template = next(program_template_cycler)
            program_name = f"{template['nombre_base']}_P{j+1}_Fac{i+1}" 
            
            programs_for_faculty.append({
                "nombre": program_name,
                "salas": salones_por_programa,
                "labs": labs_por_programa
            })

        faculties.append({
            "nombre": faculty_name,
            "listen_port_for_programs": faculty_listen_port,
            "programas": programs_for_faculty
        })
    return faculties

def run_launcher(num_faculties, salones_arg, labs_arg):
    log_event("Inicio de ejecución del superlanzador.")
    faculty_configs = generate_faculty_configs(num_faculties, salones_arg, labs_arg)
    launched_processes = []

    print(f"[Super-Lanzador] Iniciando {num_faculties} facultades.")
    print(f"Cada programa solicitará: {salones_arg} salones y {labs_arg} laboratorios.")
    log_event(f"Lanzando {num_faculties} facultades con programas que solicitan {salones_arg} salones y {labs_arg} laboratorios.")

    print("\n[Super-Lanzador] Lanzando Facultades...")
    for fac_config in faculty_configs:
        nombre_facultad = fac_config["nombre"]
        puerto_escucha_programas = fac_config["listen_port_for_programs"]
        
        comando_facultad = [
            "python3", "Facultad.py",
            nombre_facultad,
            str(puerto_escucha_programas)
        ]
        
        print(f"  → {nombre_facultad} (puerto {puerto_escucha_programas})")
        try:
            start = time.time()
            proc = subprocess.Popen(comando_facultad)
            duration = time.time() - start
            launched_processes.append(proc)
            log_event(f"{nombre_facultad} lanzada en {duration:.2f}s (PID: {proc.pid})")
        except FileNotFoundError:
            log_event(f"ERROR: Facultad.py no encontrado para {nombre_facultad}")
            continue
        time.sleep(1.0)

    print("\n[Super-Lanzador] Lanzando Programas...")
    for fac_config in faculty_configs:
        nombre_facultad = fac_config["nombre"]
        puerto_conexion_facultad = fac_config["listen_port_for_programs"]
        for prog_config in fac_config["programas"]:
            comando_programa = [
                "python3", "Programa.py",
                prog_config["nombre"],
                SEMESTRE,
                str(prog_config["salas"]),
                str(prog_config["labs"]),
                "localhost",
                str(puerto_conexion_facultad)
            ]
            try:
                start = time.time()
                proc = subprocess.Popen(comando_programa)
                duration = time.time() - start
                launched_processes.append(proc)
                log_event(f"{prog_config['nombre']} lanzado en {duration:.2f}s (PID: {proc.pid}) → Facultad: {nombre_facultad}")
            except FileNotFoundError:
                log_event(f"ERROR: Programa.py no encontrado para {prog_config['nombre']}")
            time.sleep(0.3)

    log_event(f"Total de procesos lanzados: {len(launched_processes)}")
    log_event("Ejecución finalizada.")
    print("\n[Super-Lanzador] Todos los procesos han sido lanzados.")
    print("Verifica el archivo log_superlanzador.txt para más detalles.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lanzador para múltiples facultades y programas.")
    parser.add_argument("num_facultades", type=int, choices=[5, 7, 10], help="Número de facultades a simular (5, 7, o 10).")
    parser.add_argument("salones", type=int, help="Número de salones a solicitar por cada programa.")
    parser.add_argument("laboratorios", type=int, help="Número de laboratorios a solicitar por cada programa.")
    args = parser.parse_args()
    
    if args.salones < 0 or args.laboratorios < 0:
        print("Error: El número de salones y laboratorios no puede ser negativo.")
    else:
        run_launcher(args.num_facultades, args.salones, args.laboratorios)
