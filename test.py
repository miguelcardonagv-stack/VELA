from gpiozero import OutputDevice
import time

# Motor A (Pines 17 y 22)
a1 = OutputDevice(17)
a2 = OutputDevice(22)

# Motor B (Pines 23 y 24)
b1 = OutputDevice(23)
b2 = OutputDevice(24)

print("Iniciando prueba de ambos motores...")

try:
    # Ambos motores adelante
    print("Moviendo adelante...")
    a1.on(); a2.off()
    b1.on(); b2.off()
    time.sleep(3)
    
    # Detener
    a1.off(); a2.off()
    b1.off(); b2.off()
    print("Detenidos.")

except KeyboardInterrupt:
    pass
finally:
    # Limpieza total
    a1.off(); a2.off(); b1.off(); b2.off()
    a1.close(); a2.close(); b1.close(); b2.close()
    print("Pines cerrados.")
