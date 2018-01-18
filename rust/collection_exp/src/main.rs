use std::collections::HashMap;

fn mean(vect: &Vec<i64>) -> f64 {
    let mut sum = 0;
    let mut count = 0;
    for el in vect {
        sum += el;
        count += 1;
    }
    sum as f64 / count as f64
}

fn median(vect: &Vec<i64>) -> f64 {
    let mut cc = vect.clone();
    cc.sort();
    if cc.len() % 2 == 0 {
        return (cc[cc.len() / 2] + cc[(cc.len() / 2) - 1]) as f64;
    } else {
        return cc[(cc.len() - 1) / 2] as f64;
    }
}

fn mode(vect: &Vec<i64>) -> i64 {
    let mut map = HashMap::new();
    for v in vect {
        let count = map.entry(v).or_insert(0);
        *count += 1;
    }
    println!("{:?}", map);
    let mut largest = 0;
    let mut largest_key = 0;
    for (k, v) in map {
        if v > largest {
            largest = v;
            largest_key = *k;
        }
    }
    largest_key
}

fn main() {
//    let ve = vec![1, 2, 3, 4, 4, 5, 6, 7, 5, 4, 5, 6, 7, 8, 4];
//    let x = mean(&ve);
//    let y = median(&ve);
//    let z = mode(&ve);
//    println!("{}, {}, {}", x, y, z);
    jain();

}


fn jain() {
    let v = vec![1, 2, 3];

    v[100];
}