fn obtener_numero() -> i32 {
    return 3;
}

fn doble(n: i32) -> i32 {
    n * 2
}

fn promedio(a: i32, b: i32) -> f64 {
    (a + b) as f64 / 2.0
}

fn mayor_de_edad(edad: i32) -> bool {
    if edad >= 18 {
        return true;
    } else {
        return false;
    }
}

fn obtener_edad(activo: bool) -> i32 {
    if activo {
        return 20;
    }
    0
}

fn saludar() {
    return;
}

fn main() {
    let mut contador = 0;
    let limite: i32 = 5;
    let activo = true;
    let numeros = [10, 20, 30];
    let decimales = [1.5, 2.5];
    let banderas = [true, false];

    if contador < limite && activo {
        contador = contador + 1;
    } else if contador == 3 {
        contador = 0;
    } else {
        contador = 1;
    }

    while contador <= limite {
        if contador == 3 {
            break;
        }
        contador = contador + 1;
        continue;
    }

    let total = doble(contador);
    let media = promedio(total, 2);
}
