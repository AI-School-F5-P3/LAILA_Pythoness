class FlowManager:
    """
    Controla el flujo de interacciones en la conversación.
    Permite avanzar paso a paso y verifica si se alcanzó el límite de interacciones.
    """
    def __init__(self, max_interactions=3):
        """
        Inicializa el FlowManager.

        Args:
            max_interactions (int): Número máximo de interacciones permitidas.
        """
        self.max_interactions = max_interactions
        self.current_interaction = 0

    def can_continue(self):
        """
        Verifica si la conversación puede continuar.

        Returns:
            bool: True si quedan interacciones por completar, False en caso contrario.
        """
        return self.current_interaction < self.max_interactions

    def increment(self):
        """
        Incrementa el contador de interacciones.
        """
        self.current_interaction += 1

    def reset(self):
        """
        Reinicia el contador de interacciones a cero.
        """
        self.current_interaction = 0

    def status(self):
        """
        Muestra el estado actual del flujo de interacción.

        Returns:
            str: Mensaje con el progreso actual.
        """
        return f"Interacción {self.current_interaction + 1} de {self.max_interactions}"


from flow_manager import FlowManager

def main():
    flow_manager = FlowManager(max_interactions=3)
    
    print("Iniciando flujo de conversación...\n")
    while flow_manager.can_continue():
        print(flow_manager.status())
        user_input = input("Tú: ").strip()
        print(f"Respuesta recibida: {user_input}")
        flow_manager.increment()
    
    print("\nFlujo completado. ¡Gracias por participar!")

if __name__ == "__main__":
    main()
