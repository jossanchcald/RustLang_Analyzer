// algoritmo_Jared_sintactico.rs
// Parte sintactica de Jared: asignacion, if / else if / else, while, break, continue,
// arreglos, tuplas y funciones con retorno

fn sumar(a: i32, b: i32) -> i32 {
    return a + b;
}

fn doble(x: i32) -> i32 {
    let y = x * 2;
    y
}

fn promedio(a: i32, b: i32) -> f64 {
    (a + b) as f64 / 2.0
}

fn principal() -> i32 {
    if 1 > 0 {
        return 1;
    }
    return 0;
}

fn main() {
    let mut contador = 0;
    let limite: i32 = 5;
    let total: i32;
    let activo = true;

    // Estructuras de datos: arreglos y tuplas
    let numeros = [10, 20, 30];
    let ceros = [0; 5];
    let matriz = [[1, 2], [3, 4]];
    let persona = ("Carlos", 20, 1.75);
    let vacia = ();

    // Asignacion posterior a la declaracion
    total = 50;
    total = sumar(contador, 2);
    contador = contador + 1;
    numeros = [1, 2, 3];

    // Condicionales: sin parentesis, con parentesis y con else if / else
    if contador > limite && activo {
        total = 1;
    }
    if (contador >= 18) {
        total = 2;
    } else if (contador == 3 || !activo) {
        total = 3;
    } else if contador < 0 {
        total = 4;
    } else {
        total = 5;
    }

    // while con break y continue
    while contador <= limite {
        if contador == 3 {
            break;
        }
        contador = contador + 1;
        continue;
    }

    while (activo) {
        activo = false;
    }
}
