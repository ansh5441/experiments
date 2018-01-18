struct Point<T> {
    x: T,
    y: T,
}

impl<T> Point<T> {
    fn x(&self) -> &T {
        &self.x
    }
}
impl Point<f32> {
    fn distance_from_origin(&self) -> f32 {
        (self.x.powi(2) + self.y.powi(2)).sqrt()
    }
}

fn main() {
//    let list = vec![1, 2, 3, 4, 5];
//    print!("{}", largest(&list));
//
//    let char_list = vec!['y', 'm', 'a', 'q'];
//
//    let result = largest(&char_list);
//    println!("The largest char is {}", result);

    let p = Point { x: 4, y: 5 };
    println!("p.x is {}", p.x());
    let p = Point { x: 4.0, y: 3.0};
    println!("p.distance_from_origin is {}", p.distance_from_origin());

}
//
//fn largest<T>(list: &[T]) -> T {
//    let mut largest = list[0];
//    for &item in list.iter() {
//        if item > largest {
//            largest = item;
//        }
//    }
//    largest
//}