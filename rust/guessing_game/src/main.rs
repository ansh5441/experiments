extern crate rand;

use rand::Rng;
use std::cmp::Ordering;
use std::io;


fn main() {
    println!("Guess the number!");

    let secret_number = rand::thread_rng().gen_range(1, 101);
    let mut cnt = 0;
    loop {
        cnt += 1;
        println!("Please input your guess.");

        let mut guess = String::new();
        io::stdin().read_line(&mut guess)
            .expect("Failed to read line");

        println!("you guessed {}", guess);

        let guess: u32 = match guess.trim().parse() {
            Ok(num) => num,
            Err(_) => continue,
        };

        match guess.cmp(&secret_number) {
            Ordering::Less => println!("Too small!"),
            Ordering::Greater => println!("Too Big!"),
            Ordering::Equal => {
                println!("You win! You took {} attempts", cnt);
                break;
            }
        }
    }
}
