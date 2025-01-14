"""
Esta es el modulo del reproductor
"""


class Player:
    """
    Esta es la clase del reproductor
    de musica
    """

    def play(self, song):
        """
        Reproduce la cancion

        Parameters:
        song (str): La cancion a reproducir

        Returns:
        int: 1 si reproduce 0 si fracaso
        """
        print(f"Reproduciendo {song}")
        return 1

    def stop(self):
        print("Reproducción detenida")
