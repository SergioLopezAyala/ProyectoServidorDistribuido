class Solicitud:
    def __init__(self, facultad, semestre, n_salas, n_labs):
        self.facultad = facultad
        self.semestre = semestre
        self.n_salas = n_salas
        self.n_labs = n_labs

    def to_dict(self):
        return {
            "facultad": self.facultad,
            "semestre": self.semestre,
            "n_salas": self.n_salas,
            "n_labs": self.n_labs
        }

    @staticmethod
    def from_dict(data):
        return Solicitud(
            data["facultad"],
            data["semestre"],
            data["n_salas"],
            data["n_labs"]
        )
