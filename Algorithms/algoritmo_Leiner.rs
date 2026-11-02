fn busqueda_binaria<T: Ord>(arr: &[T], key: &T, fin: usize) -> usize {
    let mut izq = 0;
    let mut der = fin;

    while izq < der {
        let medio = izq + (der - izq) / 2; // evita overflow
        if arr[medio] <= *key {
            izq = medio + 1; // <= mantiene la estabilidad
        } else {
            der = medio;
        }
    }
    izq
}

fn binary_insertion_sort<T: Ord>(arr: &mut [T]) {
    for i in 1..arr.len() {
        let pos = busqueda_binaria(arr, &arr[i], i);
        // mueve arr[i] a `pos` y desplaza el resto a la derecha
        arr[pos..=i].rotate_right(1);
    }
}

fn main() {
    let mut numeros = vec![37, 23, 0, 17, 12, 72, 31, 46, 100, 88, 54];
    println!("Antes:   {:?}", numeros);
    binary_insertion_sort(&mut numeros);
    println!("Después: {:?}", numeros);

    let mut palabras = vec!["mango", "kiwi", "uva", "banana", "fresa"];
    println!("\nAntes:   {:?}", palabras);
    binary_insertion_sort(&mut palabras);
    println!("Después: {:?}", palabras);
}