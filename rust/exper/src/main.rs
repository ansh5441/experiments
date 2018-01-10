#![allow(unused_variables)]

fn main() {
    //    struct User {
//        username: String,
//        email: String,
//        sign_in_count: u64,
//        active: bool,
//    }
//
//    let mut user1 = User {
//        email: String::from("someone@example.com"),
//        username: String::from("someusername123"),
//        active: true,
//        sign_in_count: 1,
//    };
//
//    user1.email = String::from("some2@example.com");
//    println!("{}", user1.email);
//
//
//    let user2 = User {
//        email: String::from("another@example.com"),
//        username: String::from("anotherusername567"),
//        ..user1
//    };
//
//    println!("{}", user2.email);
//    println!("{}", user2.sign_in_count);
    struct_method()
}


fn struct_method() {
    struct Rectangle {
        width: u32,
        height: u32,
    }

    impl Rectangle {
        fn area(&self) -> u32 { &self.width * &self.height }
        fn can_hold(&self, other: &Rectangle) -> bool {
            self.width >= other.width && self.height >= other.height
        }
    }

    let x = Rectangle { width: 30, height: 50 };
    let y = Rectangle { width: 29, height: 49 };

    println!(
        "The area of the rectangle is {} square pixels",
        x.area()
    );
    println!("{}", y.can_hold(&y))
}
