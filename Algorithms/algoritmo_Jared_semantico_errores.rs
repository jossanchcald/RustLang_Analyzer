const LIMITE: i32 = return 10;

// return fuera de una funcion
return 5;

// el valor devuelto no coincide con el tipo declarado
fn obtener_numero() -> i32 {
    return 3.5;
}

// falta la expresion final sin punto y coma
fn doble(n: i32) -> i32 {
    n * 2;
}

// funcion sin tipo de retorno que devuelve un valor
fn saludar() {
    return 5;
}

// if sin else, solo devuelve dentro del if
fn obtener_edad(activo: bool) -> i32 {
    if activo {
        return 20;
    }
}

// if / else donde una rama no devuelve
fn clasificar(edad: i32) -> i32 {
    if edad >= 18 {
        return 1;
    } else {
        let aviso = 0;
    }
}

// main no puede devolver i32
fn main() -> i32 {
    // la condicion no es bool
    if 2 {
        let a = 1;
    }
    while 5 {
        let b = 2;
    }

    // arreglo con elementos de distinto tipo
    let numeros = [10, 20, true];

    // break y continue fuera de un ciclo
    break;
    continue;

    return 0;
}

// else sin if previo
else {
    let c = 3;
}
