// algoritmo_Jared.rs 
// Identificadores, raw identifiers, comentarios y delimitadores o puntuacion

/// Comentario de una linea
/* Comentario de bloque
   en varias lineas */
/* Bloque /* anidado /* en dos niveles */ sigue */ fin */

const MAX_INTENTOS: u32 = 3;
const _LIMITE_2: i32 = 10;

fn calcular_total(valor_a: i32, valor_b: i32, _ignorado: i32) -> i32 {
    let suma = valor_a + valor_b; // comentario al final de la linea
    let producto = (valor_a * valor_b) /* inline */ - suma;
    producto
}

fn main() {
    let mut contador = 0;
    let edad_1: i32 = 20;
    let _privada = 5;
    let r#match = 10;        // raw identifier con palabra reservada
    let r#loop = r#match + 1;
    let r#for = [1, 2, 3];
    let tupla = (edad_1, r#loop);
    let _ = calcular_total(edad_1, r#loop, 0);

    while contador <= MAX_INTENTOS {
        if contador == 2 {
            contador += 1;
            continue;
        } else if contador >= 5 {
            break;
        } else {
            contador += 1;
        }
    }

    loop {
        contador -= 1;
        if contador < 0 { break; }
    }
    let _x = r#for[0];
    let _y = tupla;
}
