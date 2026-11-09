
fn square(x: i32) -> i32 {
    x * x
}

fn average(total: f64, count: f64) -> f64 {
    return total / count;
}

fn is_even(n: i32) -> bool {
    n % 2 == 0
}

fn factorial(n: i32) -> i32 {
    if n <= 1 {
        return 1;
    }
    return n * factorial(n - 1);
}

fn fibonacci(n: i32) -> i32 {
    let mut a = 0;
    let mut b = 1;
    for _ in 0..n {
        let next = a + b;
        a = b;
        b = next;
    }
    return a;
}

fn main() {
    // 1. Expresiones aritmeticas, negacion unaria y agrupacion
    let a = 2 + 3 * 4;
    let b = (2 + 3) * 4;
    let c = 10 - 4 - 3;
    let d = 100 / 5 / 2 % 3;
    let e = -a * b;
    let f = -(a + b) * -2;
    let g = 7 % 3 + 8 / 2 - 1;
    let h: i32 = square(4) + factorial(5);
    let r = average(10.0, 4.0);

    // 2. Operador as: mayor que * / % y menor que la negacion unaria
    let i = a as f64 * 1.5;
    let j = -a as f64;
    let k = a as f64 as i32;
    let l = (a + b) as f64 / 2.0;
    let m = a + b as i64;

    // 3. Expresiones booleanas: comparaciones, &&, || y !
    let n1 = a < b;
    let n2 = a == b || c != d;
    let n3 = !(a > b) && b >= c || d <= a;
    let n4 = !n1;
    let n5 = !true && !false || true;
    let n6 = a + 1 < b * 2 && is_even(a);

    // 4. Asignaciones compuestas
    let mut total = 0;
    total += 5;
    total -= 2;
    total *= 3;
    total /= 2;
    total %= 4;
    total += a * 2 - (b % 3);
    total -= -1;

    // 5. Vectores con vec!
    let mut nums = vec![5, 3, 8, 1];
    let zeros = vec![0; 10];
    let empty = vec![];
    let nested = vec![vec![1, 2], vec![3]];
    let calc = vec![a + 1, b * 2, -c,];
    nums.push(9);
    nums.push(a * 2);
    let size = nums.len();

    // 6. Strings: String::from, .to_string() y llamadas encadenadas
    let s1 = String::from("hola");
    let s2 = "mundo".to_string();
    let s3 = 42.to_string();
    let s4 = a.to_string();
    let s5 = 3.5.to_string();
    let mut s6 = String::new();
    s6.push_str("abc");
    let s7 = s1.to_string().to_uppercase();

    // 7. Bucle for ... in sobre rangos y colecciones
    let mut sum = 0;
    for i in 0..10 {
        sum += i;
    }
    for i in 0..=10 {
        sum += i * 2;
    }
    for i in 1..a + 1 {
        sum -= i;
    }
    for _ in 0..3 {
        total += 1;
    }
    for n in nums.iter() {
        sum += n;
    }
    for n in &nums {
        sum += n;
    }
    for n in [1, 2, 3] {
        sum += n;
    }
    for n in vec![4, 5, 6] {
        sum += n;
    }

    // 8. Closures: definicion e invocacion
    let double = |x| x * 2;
    let add = |a: i32, b: i32| a + b;
    let five = || 5;
    let typed = |x: i32| -> i32 { x + 1 };
    let block = |x| { let y = x * 2; y + 1 };
    let adder = |x| |y| x + y;
    let both = || 1 + 2;
    let sum2 = add(2, 3);
    let doubled = nums.iter().map(|x| x * 2);
    let evens = nums.iter().filter(|x| x % 2 == 0).collect();
    apply(|x| x + 1, 5);

    // 9. Mezcla con el resto del lenguaje
    let mut count = 0;
    while count < 10 {
        count += 1;
        if count % 2 == 0 {
            continue;
        }
        total += count;
    }
    if total > 100 {
        println!("Total grande: {}", total);
    } else if total > 50 {
        println!("Total medio");
    } else {
        println!("Total pequeno");
    }
    println!("Suma: {}", sum);
    println!("fib(10) = {}", fibonacci(10));
}