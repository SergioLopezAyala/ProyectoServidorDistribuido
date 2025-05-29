import subprocess
import time
import argparse
import itertools

# Global configurations
SEMESTRE = "2025-10"
FACULTAD_BASE_LISTEN_PORT = 7000  # Starting port for faculties to listen for programs
MAX_PROGRAMS_PER_FACULTY = 5 # Default, can be overridden by faculty's own logic

# Define program templates for variety (solo se usará el nombre_base)
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

def generate_faculty_configs(num_faculties, salones_por_programa, labs_por_programa):
    faculties = []
    program_template_cycler = itertools.cycle(PROGRAM_TEMPLATES)
    
    for i in range(num_faculties):
        faculty_name = f"Facultad_{i+1}"
        faculty_listen_port = FACULTAD_BASE_LISTEN_PORT + i 
        
        programs_for_faculty = []
        num_programs_this_faculty = MAX_PROGRAMS_PER_FACULTY 

        for j in range(num_programs_this_faculty):
            template = next(program_template_cycler)
            program_name = f"{template['nombre_base']}_P{j+1}_Fac{i+1}" 
            
            programs_for_faculty.append({
                "nombre": program_name,
                "salas": salones_por_programa, # Usar valor del argumento
                "labs": labs_por_programa    # Usar valor del argumento
            })

        faculties.append({
            "nombre": faculty_name,
            "listen_port_for_programs": faculty_listen_port,
            "programas": programs_for_faculty
        })
    return faculties

def run_launcher(num_faculties, salones_arg, labs_arg):
    faculty_configs = generate_faculty_configs(num_faculties, salones_arg, labs_arg)
    launched_processes = []

    print(f"[Super-Lanzador] Iniciando {num_faculties} facultades.")
    print(f"  Cada programa solicitará: {salones_arg} salones y {labs_arg} laboratorios.")
    print("-" * 70)
    print("IMPORTANTE: Este lanzador REQUIERE que haya modificado Facultad.py y Programa.py")
    print("para aceptar puertos como argumentos de línea de comandos.")
    print("Facultad.py: <nombre_facultad> <puerto_escucha_programas>")
    print("Programa.py: <programa> <semestre> <n_salas> <n_labs> <ip_facultad> <puerto_facultad>")
    print("-" * 70)

    # Launch Faculties
    print("\n[Super-Lanzador] Lanzando Facultades...")
    for fac_config in faculty_configs:
        nombre_facultad = fac_config["nombre"]
        puerto_escucha_programas = fac_config["listen_port_for_programs"]
        
        comando_facultad = [
            "python3", "Facultad.py",
            nombre_facultad,
            str(puerto_escucha_programas)
        ]
        
        print(f"  Lanzando: {nombre_facultad} (escuchando en puerto {puerto_escucha_programas} para programas)")
        print(f"    Comando: {' '.join(comando_facultad)}")
        try:
            proc = subprocess.Popen(comando_facultad)
            launched_processes.append(proc)
            print(f"    {nombre_facultad} PID: {proc.pid}")
        except FileNotFoundError:
            print(f"    ERROR: No se encontró Facultad.py. Asegúrese de que está en la ruta correcta y es ejecutable.")
            return 
        except Exception as e:
            print(f"    ERROR al lanzar {nombre_facultad}: {e}")
        
        time.sleep(1.5)

    # Launch Programs for each Faculty
    print("\n[Super-Lanzador] Lanzando Programas...")
    for fac_config in faculty_configs:
        nombre_facultad = fac_config["nombre"]
        puerto_conexion_facultad = fac_config["listen_port_for_programs"]
        
        print(f"  Programas para {nombre_facultad} (conectando a localhost:{puerto_conexion_facultad}):")
        for prog_config in fac_config["programas"]:
            comando_programa = [
                "python3", "Programa.py",
                prog_config["nombre"],
                SEMESTRE,
                str(prog_config["salas"]), # Este valor ahora viene del argumento
                str(prog_config["labs"]),  # Este valor ahora viene del argumento
                "localhost",
                str(puerto_conexion_facultad)
            ]
            print(f"    Lanzando: {prog_config['nombre']} (solicitando {prog_config['salas']} salas, {prog_config['labs']} labs)")
            print(f"      Comando: {' '.join(comando_programa)}")
            try:
                proc = subprocess.Popen(comando_programa)
                launched_processes.append(proc)
                print(f"      {prog_config['nombre']} PID: {proc.pid}")
            except FileNotFoundError:
                print(f"      ERROR: No se encontró Programa.py. Asegúrese de que está en la ruta correcta y es ejecutable.")
            except Exception as e:
                print(f"      ERROR al lanzar {prog_config['nombre']}: {e}")

            time.sleep(0.3)

    print("\n[Super-Lanzador] Todos los procesos han sido lanzados.")
    print(f"Total de procesos lanzados: {len(launched_processes)}")
    print("Los procesos se ejecutan en segundo plano.")
    print("Deberá detenerlos manualmente.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lanzador para múltiples facultades y programas.")
    parser.add_argument(
        "num_facultades", 
        type=int, 
        choices=[5, 7, 10], 
        help="Número de facultades a simular (5, 7, o 10)."
    )
    parser.add_argument(
        "salones",
        type=int,
        help="Número de salones a solicitar por cada programa."
    )
    parser.add_argument(
        "laboratorios",
        type=int,
        help="Número de laboratorios a solicitar por cada programa."
    )
    args = parser.parse_args()
    
    if args.salones < 0 or args.laboratorios < 0:
        print("Error: El número de salones y laboratorios no puede ser negativo.")
    else:
        run_launcher(args.num_facultades, args.salones, args.laboratorios)