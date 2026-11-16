# Gatitos dibujados con figuras del Canvas de tkinter (sin imagenes externas)

BORDE = "#4a3a46"
ROSA = "#f7a8c4"
ROSA_OSCURO = "#e2729b"
BLANCO = "#ffffff"

PELAJES = {
    "crema": "#fff4e6",
    "naranja": "#ffc48a",
    "gris": "#d9d9e3",
    "negro": "#5a4e5c",
}


def _ojos(c, x, y, s, forma, tags):
    t = tags + ("ojos",)
    for lado in (-1, 1):
        ox = x + lado * 10 * s
        if forma == "abiertos":
            c.create_oval(ox - 4 * s, y - 5 * s, ox + 4 * s, y + 4 * s, fill=BORDE, outline="", tags=t)
            c.create_oval(ox - 2 * s, y - 4 * s, ox + 0.5 * s, y - 1.5 * s, fill=BLANCO, outline="", tags=t)
        elif forma == "felices":
            c.create_arc(ox - 5 * s, y - 4 * s, ox + 5 * s, y + 6 * s, start=0, extent=180, style="arc",
                         outline=BORDE, width=max(2, 2 * s), tags=t)
        elif forma == "dormidos":
            c.create_arc(ox - 5 * s, y - 6 * s, ox + 5 * s, y + 3 * s, start=180, extent=180, style="arc",
                         outline=BORDE, width=max(2, 2 * s), tags=t)
        elif forma == "preocupados":
            c.create_oval(ox - 3.5 * s, y - 3 * s, ox + 3.5 * s, y + 5 * s, fill=BORDE, outline="", tags=t)
            c.create_line(ox - 5 * s, y - 8 * s + lado * 2 * s, ox + 5 * s, y - 8 * s - lado * 2 * s,
                          fill=BORDE, width=max(2, 2 * s), tags=t)


def cabeza(c, x, y, s, pelaje="crema", ojos="abiertos", tags=()):
    color = PELAJES.get(pelaje, pelaje)
    for lado in (-1, 1):
        c.create_polygon(x + lado * 24 * s, y - 4 * s, x + lado * 19 * s, y - 30 * s, x + lado * 4 * s, y - 17 * s,
                         fill=color, outline=BORDE, width=2, tags=tags)
        c.create_polygon(x + lado * 20 * s, y - 8 * s, x + lado * 18 * s, y - 24 * s, x + lado * 9 * s, y - 17 * s,
                         fill=ROSA, outline="", tags=tags)
    c.create_oval(x - 28 * s, y - 22 * s, x + 28 * s, y + 20 * s, fill=color, outline=BORDE, width=2, tags=tags)
    for lado in (-1, 1):
        c.create_oval(x + lado * 19 * s - 5 * s, y + 5 * s, x + lado * 19 * s + 5 * s, y + 10 * s,
                      fill=ROSA, outline="", tags=tags)
        for k in (-1, 0, 1):
            c.create_line(x + lado * 24 * s, y + 4 * s + k * 4 * s, x + lado * 38 * s, y + 2 * s + k * 7 * s,
                          fill=BORDE, width=1, tags=tags)
    _ojos(c, x, y, s, ojos, tags)
    c.create_polygon(x - 3 * s, y + 3 * s, x + 3 * s, y + 3 * s, x, y + 6.5 * s, fill=ROSA_OSCURO,
                     outline=ROSA_OSCURO, tags=tags)
    for lado in (-1, 1):
        c.create_arc(x - 4 * s + lado * 4 * s - 4 * s, y + 3 * s, x + lado * 4 * s + 4 * s, y + 11 * s,
                     start=180, extent=180, style="arc", outline=BORDE, width=max(1, 1.5 * s), tags=tags)


def cola(c, puntos, s, pelaje, tags=()):
    color = PELAJES.get(pelaje, pelaje)
    c.create_line(*puntos, fill=BORDE, width=9 * s + 3, smooth=True, capstyle="round", tags=tags)
    c.create_line(*puntos, fill=color, width=9 * s, smooth=True, capstyle="round", tags=tags)


def gatoSentado(c, x, y, s=1.0, pelaje="crema", ojos="abiertos", tags=()):
    # (x, y) es el punto donde el gato apoya las patas
    color = PELAJES.get(pelaje, pelaje)
    cola(c, (x + 18 * s, y - 6 * s, x + 40 * s, y - 10 * s, x + 44 * s, y - 34 * s), s, pelaje, tags)
    c.create_oval(x - 24 * s, y - 44 * s, x + 24 * s, y + 2 * s, fill=color, outline=BORDE, width=2, tags=tags)
    for lado in (-1, 1):
        c.create_oval(x + lado * 9 * s - 7 * s, y - 7 * s, x + lado * 9 * s + 7 * s, y + 3 * s,
                      fill=color, outline=BORDE, width=2, tags=tags)
    cabeza(c, x, y - 58 * s, s, pelaje, ojos, tags)


def gatoDormido(c, x, y, s=1.0, pelaje="gris", tags=()):
    color = PELAJES.get(pelaje, pelaje)
    cola(c, (x + 34 * s, y - 8 * s, x + 50 * s, y - 2 * s, x + 30 * s, y + 2 * s), s, pelaje, tags)
    c.create_oval(x - 40 * s, y - 26 * s, x + 40 * s, y + 2 * s, fill=color, outline=BORDE, width=2, tags=tags)
    cabeza(c, x - 28 * s, y - 22 * s, s * 0.85, pelaje, "dormidos", tags)
    for i, letra in enumerate("zzZ"):
        c.create_text(x - 2 * s + i * 9 * s, y - 50 * s - i * 9 * s, text=letra, fill=ROSA_OSCURO,
                      font=("Helvetica", int(8 + i * 3 * s), "bold"), tags=tags)


def gatoHeroe(c, x, y, s=1.0, pelaje="naranja", tags=()):
    # Gatito superheroe original: capa morada, antifaz y una estrella en el pecho
    color = PELAJES.get(pelaje, pelaje)
    c.create_polygon(x - 20 * s, y - 40 * s, x + 20 * s, y - 40 * s, x + 36 * s, y + 2 * s, x - 36 * s, y + 2 * s,
                     fill="#8b5cf6", outline=BORDE, width=2, tags=tags)
    c.create_oval(x - 24 * s, y - 44 * s, x + 24 * s, y + 2 * s, fill=color, outline=BORDE, width=2, tags=tags)
    for lado in (-1, 1):
        c.create_oval(x + lado * 9 * s - 7 * s, y - 7 * s, x + lado * 9 * s + 7 * s, y + 3 * s,
                      fill=color, outline=BORDE, width=2, tags=tags)
    _estrella(c, x, y - 22 * s, 8 * s, "#ffd34d", tags)
    cabeza(c, x, y - 58 * s, s, pelaje, "abiertos", tags)
    hy = y - 58 * s
    c.create_polygon(x - 22 * s, hy - 9 * s, x + 22 * s, hy - 9 * s, x + 25 * s, hy - 4 * s, x + 18 * s, hy + 3 * s,
                     x - 18 * s, hy + 3 * s, x - 25 * s, hy - 4 * s, fill="#6d28d9", outline=BORDE, width=1,
                     tags=tags)
    for lado in (-1, 1):
        ox = x + lado * 10 * s
        c.create_oval(ox - 4 * s, hy - 5 * s, ox + 4 * s, hy + 1 * s, fill=BLANCO, outline="", tags=tags)
        c.create_oval(ox - 2 * s, hy - 4 * s, ox + 2 * s, hy + 1 * s, fill=BORDE, outline="", tags=tags)


def gatoEstambre(c, x, y, s=1.0, pelaje="negro", tags=()):
    gatoSentado(c, x, y, s, pelaje, "felices", tags)
    bx, by, r = x + 46 * s, y - 12 * s, 13 * s
    c.create_oval(bx - r, by - r, bx + r, by + r, fill="#7dd3c0", outline=BORDE, width=2, tags=tags)
    for k in (-6, 0, 6):
        c.create_arc(bx - r + 2, by - r + k * s, bx + r - 2, by + r + k * s, start=200, extent=140,
                     style="arc", outline="#3c9c86", width=1, tags=tags)
    c.create_line(bx - r, by + 4 * s, bx - r - 16 * s, by + 10 * s, bx - r - 26 * s, by + 8 * s,
                  smooth=True, fill="#3c9c86", width=2, tags=tags)


def _estrella(c, x, y, r, color, tags):
    import math
    puntos = []
    for i in range(10):
        radio = r if i % 2 == 0 else r * 0.45
        angulo = math.pi / 2 + i * math.pi / 5
        puntos += [x + radio * math.cos(angulo), y - radio * math.sin(angulo)]
    c.create_polygon(*puntos, fill=color, outline=BORDE, width=1, tags=tags)


class GatoTamborilero:
    # Gatito detras de una mesa que golpea con las patas cuando se analiza el codigo
    def __init__(self, c, x, y, s=0.8, pelaje="crema"):
        self.c, self.x, self.y, self.s, self.pelaje = c, x, y, s, pelaje
        self.animando = False
        self.dibujar("abiertos")

    def dibujar(self, ojos):
        c, x, y, s = self.c, self.x, self.y, self.s
        c.delete("tamborilero")
        color = PELAJES[self.pelaje]
        t = ("tamborilero",)
        c.create_oval(x - 24 * s, y - 14 * s, x + 24 * s, y + 30 * s, fill=color, outline=BORDE, width=2, tags=t)
        cabeza(c, x, y - 18 * s, s, self.pelaje, ojos, t)
        c.create_rectangle(x - 52 * s, y + 12 * s, x + 52 * s, y + 30 * s, fill="#c98b5e", outline=BORDE,
                           width=2, tags=t)
        c.create_rectangle(x - 52 * s, y + 12 * s, x + 52 * s, y + 16 * s, fill="#dda37a", outline="", tags=t)
        self.patas = []
        for lado in (-1, 1):
            px = x + lado * 16 * s
            pata = c.create_oval(px - 7 * s, y + 5 * s, px + 7 * s, y + 14 * s, fill=color, outline=BORDE,
                                 width=2, tags=t)
            self.patas.append(pata)

    def golpear(self, golpes=8, alTerminar=None):
        if self.animando:
            return
        self.animando = True
        self.dibujar("felices")
        self._paso(0, golpes, alTerminar)

    def _paso(self, i, golpes, alTerminar):
        c, s = self.c, self.s
        c.delete("pum")
        if i >= golpes:
            self.animando = False
            if alTerminar:
                alTerminar()
            return
        arriba = self.patas[i % 2]
        abajo = self.patas[(i + 1) % 2]
        c.move(arriba, 0, -9 * s)
        x0, y0, x1, y1 = c.coords(abajo)
        c.create_text((x0 + x1) / 2 + (-16 if i % 2 else 16) * s, y0 - 4 * s, text="¡pum!",
                      fill=ROSA_OSCURO, font=("Helvetica", 8, "bold"), tags=("tamborilero", "pum"))
        c.after(90, lambda: c.move(arriba, 0, 9 * s))
        c.after(180, lambda: self._paso(i + 1, golpes, alTerminar))

    def reaccionar(self, hayErrores):
        self.dibujar("preocupados" if hayErrores else "felices")
        x, y, s = self.x, self.y, self.s
        if hayErrores:
            self.c.create_text(x + 34 * s, y - 40 * s, text="!", fill="#d93c3c",
                               font=("Helvetica", 14, "bold"), tags=("tamborilero",))
        else:
            for dx, dy in ((30, -38), (40, -28)):
                self.c.create_text(x + dx * s, y + dy * s, text="♥", fill=ROSA_OSCURO,
                                   font=("Helvetica", 11, "bold"), tags=("tamborilero",))


class GatoTecladoImagenes:
    # Mismo comportamiento que GatoTamborilero, pero alternando dos imagenes (una pata, la otra pata)
    def __init__(self, c, x, y, cuadros):
        self.c, self.x, self.y, self.cuadros = c, x, y, cuadros
        self.animando = False
        self.dibujar()

    def dibujar(self, _ojos=None):
        self.c.delete("tamborilero")
        self.item = self.c.create_image(self.x, self.y, image=self.cuadros[0], tags=("tamborilero",))

    def golpear(self, golpes=10, alTerminar=None):
        if self.animando:
            return
        self.animando = True
        self.dibujar()
        self._paso(0, golpes, alTerminar)

    def _paso(self, i, golpes, alTerminar):
        if i >= golpes:
            self.c.itemconfigure(self.item, image=self.cuadros[0])
            self.animando = False
            if alTerminar:
                alTerminar()
            return
        self.c.itemconfigure(self.item, image=self.cuadros[(i + 1) % len(self.cuadros)])
        self.c.after(120, lambda: self._paso(i + 1, golpes, alTerminar))

    def reaccionar(self, hayErrores):
        self.dibujar()
        ancho = self.cuadros[0].width()
        x, y = self.x + ancho // 2 + 10, self.y - 18
        if hayErrores:
            self.c.create_text(x, y, text="!", fill="#d93c3c", font=("Helvetica", 16, "bold"), tags=("tamborilero",))
        else:
            self.c.create_text(x, y, text="♥", fill=ROSA_OSCURO, font=("Helvetica", 13, "bold"), tags=("tamborilero",))
            self.c.create_text(x + 12, y + 12, text="♥", fill=ROSA_OSCURO, font=("Helvetica", 10, "bold"),
                               tags=("tamborilero",))
