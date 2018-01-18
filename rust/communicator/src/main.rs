fn is_prime(num: i64)->bool{
	let upper_limit = (num as f64).sqrt() as i64 + 1;
	for i in 2..upper_limit {
		if num % i == 0 {
			return false;
		}
	}
	true
}

fn is_palindrome(string: &str) -> bool {
    let half_len = string.len()/2;
    string.chars().take(half_len).eq(string.chars().rev().take(half_len))
}


fn p1()->i32{
	let mut sum = 0;
	for i in 1..1000 {
		if i%3 == 0 || i%5 ==0 {
			sum += i;
		}
	}
	sum
}


fn p2() -> i64{
	let mut sum = 0;
	let mut a: i64 = 1;
	let mut b: i64 = 1;
	let mut c = 0;
	// let mut c = a + b;
	while c < 4000000 {
		if c%2 == 0{
			sum += c;
		}
		c = a + b;
		a = b;
		b = c;
	}
	sum
}

fn p3() -> i64 {
	let num:i64 = 600851475143;
	let upper_limit = (num as f64).sqrt() as i64 + 1;
	println!("{}", upper_limit);
	for i in (1..upper_limit).rev() {
		if num % i == 0 {
			if is_prime(i) {
				return i;
			}
		}
	}
	0
}

fn p4() -> i64 {
	let mut largest = 0;
	for i in (100..999).rev() {
		for j in (100..999).rev() {
			let prod = i*j;
			let prod_str = prod.to_string();
			if is_palindrome(&prod_str) {
				if prod > largest {
					largest = prod
				}
			}
		}
	}
	largest
}

fn p5() -> i64{
	let mut num = 0;
	let mut condition = false;
	let increment = 2*3*5*7*11*13*17*19;
	while !condition {

		num += increment;
		let mut is_divisible_by_all = true;
		for i in 2..21 {
			if num % i != 0 {
				is_divisible_by_all = false;
				break;
			}
		}
		condition = is_divisible_by_all
	}
	num
}

fn p6() -> i64{
	let mut sum_sq = 0;
	let mut sq_sum = 0;
	for i in 1..101{
		sq_sum += i * i;
		sum_sq += i
	}
	sum_sq = sum_sq * sum_sq;
	return sum_sq - sq_sum;
}


fn p7() -> i64{
	let mut prime_count = 0;
	let mut num = 1;
	while prime_count < 10001 {
		num += 1;
	    if is_prime(num) {
			prime_count += 1
	    }
	}
	num
}
fn main (){
	// communicator::client::connect();
	let x = p7();
	println!("{}", x);
}