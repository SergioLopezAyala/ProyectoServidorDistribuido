import subprocess
import time
import argparse
import itertools

# Global configurations
SEMESTRE = "2025-10"
FACULTAD_BASE_LISTEN_PORT = 7000  # Starting port for faculties to listen for programs
MAX_PROGRAMS_PER_FACULTY = 5 # Default, can be overridden by faculty's own logic

# Define program templates for variety
PROGRAM_TEMPLATES = [
    {"nombre_base": "Sistemas", "salas": 5, "labs": 2},
    {"nombre_base": "Civil", "salas": 6, "labs": 1},
    {"nombre_base": "Industrial", "salas": 4, "labs": 2},
    {"nombre_base": "Electronica", "salas": 5, "labs": 3},
    {"nombre_base": "Ambiental", "salas": 3, "labs": 2},
    {"nombre_base": "Mecanica", "salas": 4, "labs": 1},
    {"nombre_base": "Quimica", "salas": 3, "labs": 3},
    {"nombre_base": "Arquitectura", "salas": 7, "labs": 1},
    {"nombre_base": "Diseno", "salas": 3, "labs": 1},
    {"nombre_base": "Medicina", "salas": 8, "labs": 4},
    {"nombre_base": "Software", "salas": 5, "labs": 3},
    {"nombre_base": "Telecom", "salas": 4, "labs": 2},
    {"nombre_base": "Biomecanica", "salas": 3, "labs": 2},
    {"nombre_base": "Petroleos", "salas": 2, "labs": 1},
    {"nombre_base": "Minas", "salas": 3, "labs": 1},
]

def generate_faculty_configs(num_faculties):
    faculties = []
    program_template_cycler = itertools.cycle(PROGRAM_TEMPLATES)
    
    for i in range(num_faculties):
        faculty_name = f"Facultad_{i+1}"
        faculty_listen_port = FACULTAD_BASE_LISTEN_PORT + i 
        
        programs_for_faculty = []
        # Ensure each faculty gets its defined number of programs, 
        # or MAX_PROGRAMS_PER_FACULTY if not otherwise specified by faculty logic
        num_programs_this_faculty = MAX_PROGRAMS_PER_FACULTY 

        for j in range(num_programs_this_faculty):
            template = next(program_template_cycler)
            # Ensure unique program names, especially if templates repeat for many faculties
            program_name = f"{template['nombre_base']}_P{j+1}_Fac{i+1}" 
            programs_for_faculty.append({
                "nombre": program_name,
                "salas": template["salas"],
                "labs": template["labs"]
            })

        faculties.append({
            "nombre": faculty_name,
            "listen_port_for_programs": faculty_listen_port,
            "programas": programs_for_faculty
        })
    return faculties

def run_launcher(num_faculties):
    faculty_configs = generate_faculty_configs(num_faculties)
    launched_processes = []

    print(f"[Super-Lanzador] Iniciando {num_faculties} facultades y sus programas...")
    print("-" * 70)
    print("-" * 70)

    # Launch Faculties
    print("\n[Super-Lanzador] Lanzando Facultades...")
    for fac_config in faculty_configs:
        nombre_facultad = fac_config["nombre"]
        puerto_escucha_programas = fac_config["listen_port_for_programs"]
        
        # Command for Facultad.py: python3 Facultad.py <nombre_facultad> <puerto_escucha_programas>
        comando_facultad = [
            "python3", "Facultad.py",
            nombre_facultad,
            str(puerto_escucha_programas)
        ]
        
        print(f"  Lanzando: {nombre_facultad} (escuchando en puerto {puerto_escucha_programas} para programas)")
        print(f"    Comando: {' '.join(comando_facultad)}")
        try:
            # Using Popen to run in the background. For Windows, might need creationflags.
            proc = subprocess.Popen(comando_facultad)
            launched_processes.append(proc)
            print(f"    {nombre_facultad} PID: {proc.pid}")
        except FileNotFoundError:
            print(f"    ERROR: No se encontró Facultad.py. Asegúrese de que está en la ruta correcta y es ejecutable.")
            return 
        except Exception as e:
            print(f"    ERROR al lanzar {nombre_facultad}: {e}")
        
        time.sleep(1.5) # Increased pause for faculty to initialize its listening socket

    # Launch Programs for each Faculty
    print("\n[Super-Lanzador] Lanzando Programas...")
    for fac_config in faculty_configs:
        nombre_facultad = fac_config["nombre"]
        puerto_conexion_facultad = fac_config["listen_port_for_programs"] # Port where this faculty is listening
        
        print(f"  Programas para {nombre_facultad} (conectando a localhost:{puerto_conexion_facultad}):")
        for prog_config in fac_config["programas"]:
            # Command for Programa.py: python3 Programa.py <programa> <semestre> <n_salas> <n_labs> <ip_facultad> <puerto_facultad>
            comando_programa = [
                "python3", "Programa.py",
                prog_config["nombre"],
                SEMESTRE,
                str(prog_config["salas"]),
                str(prog_config["labs"]),
                "localhost",  # Facultad runs on the same machine, programs connect to localhost
                str(puerto_conexion_facultad)
            ]
            print(f"    Lanzando: {prog_config['nombre']}")
            print(f"      Comando: {' '.join(comando_programa)}")
            try:
                proc = subprocess.Popen(comando_programa)
                launched_processes.append(proc)
                print(f"      {prog_config['nombre']} PID: {proc.pid}")
            except FileNotFoundError:
                print(f"      ERROR: No se encontró Programa.py. Asegúrese de que está en la ruta correcta y es ejecutable.")
            except Exception as e:
                print(f"      ERROR al lanzar {prog_config['nombre']}: {e}")

            time.sleep(0.3) # Small pause between program launches

    print("\n[Super-Lanzador] Todos los procesos han sido lanzados.")
    print(f"Total de procesos lanzados: {len(launched_processes)}")
    print("Los procesos se ejecutan en segundo plano.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lanzador para múltiples facultades y programas.")
    parser.add_argument(
        "num_facultades", 
        type=int, 
        choices=[5, 7, 10], 
        help="Número de facultades a simular (5, 7, o 10)."
    )
    args = parser.parse_args()
    
    run_launcher(args.num_facultades)