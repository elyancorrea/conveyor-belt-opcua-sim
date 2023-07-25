import threading
import sim
import interface

def run_sim():
    sim.show()

def run_interface():
    interface.main()

# Criar os threads
sim_thread = threading.Thread(target=run_sim)
interface_thread = threading.Thread(target=run_interface)

# Iniciar os threads
sim_thread.start()
interface_thread.start()

# Aguardar a conclusão dos threads
sim_thread.join()
interface_thread.join()
