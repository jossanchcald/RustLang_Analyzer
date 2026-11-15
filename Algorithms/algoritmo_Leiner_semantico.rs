// Constantes globales
const MAXIMO: i32 = 100;
const FACTOR: f64 = 1.5;

fn sumar(a: i32, b: i32) -> i32 {
    a + b
}

fn promedio(total: i32, cantidad: i32) -> f64 {
    total as f64 / cantidad as f64
}

fn main() {
    // la funcion saludar se declara mas abajo
    saludar();
    let resultado: i32 = sumar(2, 3);
    let media: f64 = promedio(10, 4);

    // variables que reciben su valor antes de usarse
    let total: i32;
    total = 10;
    let mut acumulado: i32;
    acumulado = 0;
    acumulado += total;

    // variable usada dentro de su propio bloque
    if total > 5 {
        let mensaje = "mayor";
        println!("{}", mensaje);
    }

    // variable del for usada dentro del for
    for i in 0..3 {
        acumulado += i;
    }

    // closure llamado como una funcion
    let multiplicar = |x: i32, y: i32| x * y;
    let producto: i32 = multiplicar(2, 4);

    // la constante MINIMO se declara al final del archivo
    let limite: i32 = MINIMO + MAXIMO;

    // conversion numerica explicita con as
    let entero: i32 = 7;
    let decimal: f64 = entero as f64;
    let escala: f64 = decimal * FACTOR;

    // conversiones validas con as
    let byte: u8 = 65;
    let letra = byte as char;
    let codigo = 'a' as u32;
    let bandera = true as i32;
    let truncado = 3.9 as i32;

    // shadowing: la nueva x usa el valor de la anterior
    let x = 1;
    let x = x + 1;

    println!("{}", resultado);
    println!("{}", media);
    println!("{}", acumulado);
    println!("{}", producto);
    println!("{}", limite);
    println!("{}", escala);
    println!("{}", letra);
    println!("{}", codigo);
    println!("{}", bandera);
    println!("{}", truncado);
    println!("{}", x);
}

fn saludar() {
    println!("Hola");
}

const MINIMO: i32 = 1;
