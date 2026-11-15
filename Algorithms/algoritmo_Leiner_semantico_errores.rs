// Identificadores 4: constante repetida en el mismo ambito
const LIMITE: i32 = 10;
const LIMITE: i32 = 20;

// Identificadores 6: parametros repetidos
fn sumar(a: i32, a: i32) -> i32 {
    a + a
}

// Identificadores 6: funcion repetida
fn saludar() {
    println!("Hola");
}

fn saludar() {
    println!("Hola otra vez");
}

fn main() {
    // Identificadores 1: variable usada fuera de su ambito
    if true {
        let edad = 20;
    }
    println!("{}", edad);

    // Identificadores 2: funcion no declarada
    despedir();

    // Identificadores 3: variable usada antes de declararse
    println!("{}", contador);
    let contador = 5;

    // Identificadores 5: variable usada antes de inicializarse
    let total: i32;
    println!("{}", total);

    // Conversion 1: conversion numerica implicita
    let entero: i32 = 5;
    let decimal: f64 = entero;

    // Conversion 2: conversion invalida con as (solo u8 se convierte a char)
    let numero: i32 = 65;
    let letra = numero as char;

    // Conversion 5: char a flotante con as
    let simbolo = 'a';
    let valor = simbolo as f64;

    // Conversion 6: conversion hacia bool con as
    let activo = entero as bool;
}
