from abc import ABC, abstractmethod


class Espacio(ABC):

    mi_categoria = "Infraestructura Educativa"

    def __init__(self, id_espacio: int, capacidad: int, nombre: str):
        self._id_espacio = id_espacio
        self._capacidad = capacidad
        self.nombre = nombre

    @property
    def capacidad(self):
        return self._capacidad

    @capacidad.setter
    def capacidad(self, nueva_capacidad):
        if nueva_capacidad <= 0:
            raise ValueError(
                "La capacidad debe ser mayor que cero"
            )
        self._capacidad = nueva_capacidad

    def id_espacio(self):
        print(
            f"ID del espacio: {self._id_espacio}"
        )

    def evaluar_capacidad(
        self,
        limite: int
    ) -> bool:

        print(
            f"Capacidad: "
            f"{self._capacidad} estudiantes"
        )

        return self.tiene_capacidad(limite)

    def tiene_capacidad(
        self,
        num_estudiantes: int
    ) -> bool:

        return (
            self._capacidad >=
            num_estudiantes
        )

    def mostrar_nombre(self):

        print(
            f"Espacio: "
            f"{self.nombre}"
        )

    @abstractmethod
    def descripcion(self):
        pass


class Laboratorio(Espacio):

    mi_laboratorio = (
        "Laboratorio especializado"
    )

    def __init__(
        self,
        id_espacio: int,
        capacidad: int,
        equipamiento: list
    ):

        super().__init__(
            id_espacio,
            capacidad,
            "Laboratorio de Practica"
        )

        self._equipamiento = (
            list(equipamiento)
        )

    @property
    def equipamiento(self):
        return self._equipamiento

    def id_espacio(self):

        print(
            f"ID del laboratorio: "
            f"{self._id_espacio}"
        )

    def agregar_equipamiento(
        self,
        *equipos
    ):

        if not equipos:

            print(
                "No se agregaron equipos"
            )

            return

        for equipo in equipos:

            self._equipamiento.append(
                equipo
            )

        print(
            f"Se agregaron "
            f"{len(equipos)} equipos"
        )

    def mostrar_capacidad(self):

        print(
            f"Capacidad: "
            f"{self._capacidad}"
        )

    def mostrar_equipamiento(self):

        print(
            f"Equipamiento: "
            f"{self._equipamiento}"
        )

    def descripcion(self):

        return (
            f"Laboratorio con "
            f"{self._capacidad} cupos "
            f"y "
            f"{len(self._equipamiento)} "
            f"equipos"
        )


class Aula(Espacio):

    def descripcion(self):

        return (
            f"Aula {self.nombre} "
            f"con "
            f"{self._capacidad} "
            f"cupos"
        )
class Paralelo:

    mi_paralelo = "Paralelo"

    def __init__(
        self,
        id_paralelo: int,
        num_estudiantes: int,
        nombre_paralelo: str
    ):

        self._id_paralelo = id_paralelo
        self._num_estudiantes = num_estudiantes
        self.nombre_paralelo = nombre_paralelo

    def id_paralelo(self):

        print(
            f"ID Paralelo: "
            f"{self._id_paralelo}"
        )

    def agregar_estudiantes(
        self,
        cantidad: int
    ):

        self._num_estudiantes += cantidad

        print(
            f"Total estudiantes: "
            f"{self._num_estudiantes}"
        )

    def mostrar_nombre_paralelo(self):

        print(
            f"Paralelo: "
            f"{self.nombre_paralelo}"
        )


class Docente:

    mi_docente = "Docente"

    def __init__(
        self,
        disponibilidad: list,
        preferencias: str,
        descansos: list
    ):

        self._disponibilidad = disponibilidad
        self._preferencias = preferencias
        self._descansos = descansos

    @property
    def preferencias(self):
        return self._preferencias

    @preferencias.setter
    def preferencias(self, valor):
        self._preferencias = valor

    def disponibilidad(self):

        print(
            f"Disponibilidad: "
            f"{self._disponibilidad}"
        )

    def cambiar_preferencias(
        self,
        *preferencias
    ):

        if not preferencias:

            print(
                "No se ingresaron preferencias"
            )
            return

        if len(preferencias) == 1:

            self._preferencias = preferencias[0]

        else:

            self._preferencias = (
                ", ".join(preferencias)
            )

        print(
            f"Nueva preferencia: "
            f"{self._preferencias}"
        )

    def mostrar_descansos(self):

        print(
            f"Descansos: "
            f"{self._descansos}"
        )


class Horario:

    mi_horario = "Horario Académico"

    def __init__(
        self,
        id_horario: int,
        periodo: str,
        estado: str
    ):

        self._id_horario = id_horario
        self.periodo = periodo
        self._estado = estado

    def id_horario(self):

        print(
            f"Horario ID: "
            f"{self._id_horario}"
        )

    def cambiar_periodo(
        self,
        nuevo_periodo
    ):

        self.periodo = nuevo_periodo

    def mostrar_estado(self):

        print(
            f"Estado: "
            f"{self._estado}"
        )


class Planificador:

    def __init__(self):
        self.horarios = []

    def agregar(
        self,
        horario
    ):

        self.horarios.append(horario)

        print(
            "Horario agregado"
        )
class LaboratorioUniversitario(
    Laboratorio,
    Docente
):

    def __init__(
        self,
        id_espacio,
        capacidad,
        equipamiento,
        disponibilidad,
        preferencias,
        descansos
    ):

        Laboratorio.__init__(
            self,
            id_espacio,
            capacidad,
            equipamiento
        )

        Docente.__init__(
            self,
            disponibilidad,
            preferencias,
            descansos
        )

    def mostrar_informacion_completa(self):

        print(
            "\n=== LABORATORIO UNIVERSITARIO ==="
        )

        self.mostrar_nombre()
        self.mostrar_capacidad()
        self.mostrar_equipamiento()
        self.disponibilidad()
        self.mostrar_descansos()


if __name__ == "__main__":

    aula = Aula(
        1,
        30,
        "Lab 1"
    )

    aula.id_espacio()

    aula.mostrar_nombre()

    print(
        aula.descripcion()
    )

    lab = Laboratorio(
        101,
        20,
        ["Computadoras"]
    )

    lab.id_espacio()

    lab.agregar_equipamiento(
        "Router",
        "Switch",
        "Servidor"
    )

    lab.mostrar_equipamiento()

    print(
        lab.descripcion()
    )

    docente = Docente(
        ["Lunes"],
        "Redes",
        ["Viernes"]
    )

    docente.disponibilidad()

    docente.cambiar_preferencias(
        "IA",
        "Programacion",
        "Base de Datos"
    )

    docente.mostrar_descansos()

    p1 = Paralelo(
        1,
        35,
        "Sistemas A"
    )

    p1.id_paralelo()

    p1.agregar_estudiantes(
        5
    )

    p1.mostrar_nombre_paralelo()

    h1 = Horario(
        100,
        "2026-2",
        "Activo"
    )

    h1.id_horario()

    h1.cambiar_periodo(
        "2026-3"
    )

    h1.mostrar_estado()

    laboratorio_universitario = (
        LaboratorioUniversitario(
            201,
            25,
            [
                "Computadoras",
                "Router"
            ],
            [
                "Lunes",
                "Martes"
            ],
            "Redes",
            [
                "Viernes"
            ]
        )
    )

    laboratorio_universitario.mostrar_informacion_completa()

    print(
        Laboratorio.mi_laboratorio
    )

    Laboratorio.mi_laboratorio = (
        "Laboratorio de Alta Tecnologia"
    )

    print(
        Laboratorio.mi_laboratorio
    )

    aula_grande = Aula(
        50,
        40,
        "Aula Principal"
    )

    if aula_grande.tiene_capacidad(
        35
    ):

        print(
            "Se puede asignar el paralelo"
        )

    else:

        print(
            "No hay capacidad suficiente"
        )

    aula_pequena = Aula(
        51,
        20,
        "Aula Pequeña"
    )

    if aula_pequena.tiene_capacidad(
        35
    ):

        print(
            "Se puede asignar el paralelo"
        )

    else:

        print(
            "No hay capacidad suficiente"
        )

    docente2 = Docente(
        [
            "Lunes",
            "Martes"
        ],
        "Redes",
        [
            "Viernes"
        ]
    )

    docente2.cambiar_preferencias(
        "Inteligencia Artificial",
        "Programacion",
        "Base de Datos"
    )

    print(
        docente2.preferencias
    )

    lab2 = Laboratorio(
        102,
        30,
        [
            "Computadoras"
        ]
    )

    lab2.agregar_equipamiento(
        "Router",
        "Switch",
        "Servidor",
        "Firewall"
    )

    lab2.mostrar_equipamiento()

    espacios = [

        Aula(
            60,
            35,
            "Aula A"
        ),

        Laboratorio(
            61,
            25,
            [
                "PC"
            ]
        )
    ]

    for espacio in espacios:

        print(
            espacio.descripcion()
        )

    laboratorio_universitario2 = (
        LaboratorioUniversitario(
            999,
            35,
            [
                "Computadoras"
            ],
            [
                "Lunes",
                "Miercoles"
            ],
            "Seguridad Informatica",
            [
                "Viernes"
            ]
        )
    )

    laboratorio_universitario2.mostrar_informacion_completa()

    print(
        Laboratorio.mi_laboratorio
    )

    Laboratorio.mi_laboratorio = (
        "Laboratorio Inteligente"
    )

    print(
        Laboratorio.mi_laboratorio
    )

    try:

        aula_error = Aula(
            80,
            30,
            "Aula Test"
        )

        aula_error.capacidad = -10

    except ValueError as e:

        print(
            "Error capturado:",
            e
        )

    planificador = Planificador()

    horario1 = Horario(
        1,
        "2026-2",
        "Activo"
    )

    horario2 = Horario(
        2,
        "2026-2",
        "Activo"
    )

    planificador.agregar(
        horario1
    )

    planificador.agregar(
        horario2
    )

    print(
        len(
            planificador.horarios
        )
    )