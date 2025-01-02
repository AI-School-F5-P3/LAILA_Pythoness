class FlowManager:
    """
    Controla el flujo de interacciones en la conversación.
    Permite avanzar paso a paso y verifica si se alcanzó el límite de interacciones.
    """
    def __init__(self, max_steps=8):
        # Inicializa el número máximo de pasos y el contador actual
        self.max_steps = max_steps
        self.current_step = 0

    def can_continue(self):
        """
        Verifica si es posible continuar con las interacciones según el límite definido.
        """
        return self.current_step < self.max_steps

    def advance(self):
        """
        Avanza al siguiente paso si no se alcanzó el límite.
        Lanza una excepción si se intenta avanzar más allá del límite.
        """
        if self.can_continue():
            self.current_step += 1
        else:
            raise StopIteration("Se alcanzó el límite máximo de interacciones.")

    def reset(self):
        """
        Reinicia el contador de pasos.
        """
        self.current_step = 0

    def finish(self):
        """
        Reinicia el contador de pasos.
        """
        self.current_step = 10

if __name__ == "__main__":
    # Prueba del FlowManager
    print("Iniciando prueba del FlowManager...")
    manager = FlowManager(max_steps=3)  # Configura un límite de 3 pasos

    try:
        while manager.can_continue():
            print(f"Paso actual: {manager.current_step + 1}")
            manager.advance()  # Avanza al siguiente paso
        print("Se completaron todas las interacciones permitidas.")
    except StopIteration as e:
        print(e)

    # Reinicia el flujo y muestra el estado
    manager.reset()
    print("FlowManager reiniciado.")
    print(f"Paso actual después del reinicio: {manager.current_step}")
