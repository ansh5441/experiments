fn main() {
//    let mut x = 5;
//    println!("The value of x is: {}", x);
//    x = 6;
//    println!("The value of x is: {}", x);
//    let tup = (500, 6.4, 1);
//    println!("{}, {}, {}", tup.0, tup.1, tup.2);
//    let mut number = 3;
//    while number != 0 {
//        println!("{}!", number);
//        number -= 1;
//    }
//    println!("LIFTOFF!!!");
//
//    let a = [1, 2, 3, 4, 5, 6];
//    for elem in a.iter() {
//        println!("The value is {}", elem);
//    }
//    for i in 1..5 {
//        println!("{}", i);
//    }
//
//    println!("{}", nth_fib(7));
//
//
//    let s = String::from("hello");
//    takes_ownership(s);
//    let x = "c".to_lowercase();
//    takes_ownership(x);

//    println!("{}", x);
//    println!("{}", s);
//    let mut s = String::from("hello");
//    println!("{}", s);
//    change(&mut s);
//    println!("{}", s);
//    println!("{}", first_word(&String::from("hel luao world")));
    let my_string = String::from("hello world");

    // first_word works on slices of `String`s
    let word = first_word(&my_string[..]);
    println!("{}", word);


    let my_string_literal = "hello world";
    println!("{}", word);

    // first_word works on slices of string literals
    let word = first_word(&my_string_literal[..]);
    println!("{}", word);

    // since string literals *are* string slices already,
    // this works too, without the slice syntax!
    let word = first_word(my_string_literal);
    println!("{}", word);

    let word = first_word(&my_string);
    println!("{}", word);

}

fn first_word(s: &str) -> &str {
    let bytes = s.as_bytes();
    for (i, &item) in bytes.iter().enumerate() {
        if item == b' ' {
            return &s[0..i];
        }
    }
    &s[..]
}

//fn change(st: &mut String){
//    st.push_str(", World");
//}
//
//fn takes_ownership(some_string: String) {
//    println!("{}", some_string);
//}
//
//fn nth_fib(n: i32) -> i32 {
//    let mut a = 1;
//    let mut b = 1;
//    if n == 1 || n == 2 {
//        return 1;
//    }
//
//    for _i in 3..n {
//        let c = a + b;
//        a = b;
//        b = c;
//
//    }
//    return a + b;
//}