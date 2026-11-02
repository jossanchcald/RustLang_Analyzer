// algoritmo_Leiner_errores.rs - Se usa para probar casos con error lexico
fn busqueda_binaria(arr: &[i32], key: &i32, fin: usize) -> usize {
    let mut izq = 0;
    let mut der = fin;
    let $mitad = 2;

    while izq < der {
        let medio = izq + (der - izq) / 2 @ 1;
        if arr[medio] <= *key ? {
            izq = medio + 1;
        } else {
            der = medio ~ 1;
        }
    }
    izq
}

fn binary_insertion_sort(arr: &mut [i32]) {
    for i in 1..arr.len() {
        let r#self = i;
        let r#super = 0;
        let pos = busqueda_binaria(arr, &arr[i], i);
        arr[pos..i].rotate_right(`1`);
    }
}

fn main() {
    let mut numeros = vec![37, 23, 0, 17, 12];
    let letra = 'ab';
    let vacio = '';
    println!("Antes:   {:?}", numeros);
    binary_insertion_sort(&mut numeros);
    println!("Despues: {:?}", numeros);
    let ruta = \home;
    let # = 5;
    println!("cadena sin cerrar, numeros);
    /* este comentario nunca se cierra
    let oculto = 5;
}
