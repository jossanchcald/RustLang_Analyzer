// algoritmo_Jared_sintactico_errores.rs
// Casos con errores sintacticos de la parte de Jared. Entre cada error hay sentencias validas
fn main() {
    let mut contador = 0;
    let limite = 5;

    // Error 1: if sin condicion
    if { contador = 1; }
    contador = contador + 1;
    limite = limite + 1;

    // Error 2: while sin condicion
    while { contador = 2; }
    contador = contador + 1;
    limite = limite + 1;

    // Error 3: asignacion sin valor
    contador = ;
    contador = contador + 1;
    limite = limite + 1;

    // Error 4: comparacion encadenada (las comparaciones no se encadenan)
    if contador < 1 < 5 { contador = 3; }
    contador = contador + 1;
    limite = limite + 1;

    // Error 5: continue con valor
    while contador > 0 { continue 3; }
    contador = contador + 1;
    limite = limite + 1;

    // Error 6: else sin if
    else { contador = 4; }
    contador = contador + 1;
}
