fn main() {
    let string1 = String::from("abcd");
    let string2 = "xyz";
    let result = longest(string1.as_str(), string2);
    println!("The longest string is {}", result);
//    let list = vec![1, 2, 3, 4, 5];
//    println!("The largest int is {}", largest(&list));
//
//    let char_list = vec!['y', 'm', 'a', 'q'];
//
//    let result = largest(&char_list);
//    println!("The largest char is {}", result);
//
//    let p = Point { x: 4, y: 5 };
//    println!("p.x is {}", p.x());
//    let p = Point { x: 4.0, y: 3.0};
//    println!("p.distance_from_origin is {}", p.distance_from_origin());
//    let t = Tweet {
//        username: String::from("horse_ebooks"),
//        content: String::from("of course, as you probably already know, people"),
//        reply: false,
//        retweet: false,
//    };
//    println!("1 new tweet: {}", t.summary());
//
//    let article = NewsArticle {
//        headline: String::from("Penguins win the Stanley Cup Championship!"),
//        location: String::from("Pittsburgh, PA, USA"),
//        author: String::from("Iceburgh"),
//        content: String::from("The Pittsburgh Penguins once again are the best
//        hockey team in the NHL."),
//    };
//
//    println!("New article available! {}", article.summary());
}

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

pub trait Summarizable {
    fn summary(&self) -> String;
}

pub trait Summarizable {
    fn summary(&self) -> String {
        String::from("(Read More...)")
    }
}

pub struct NewsArticle {
    pub headline: String,
    pub location: String,
    pub author: String,
    pub content: String,
}

impl Summarizable for NewsArticle {
    fn summary(&self) -> String {
        format!("{}, by {} ({})", self.headline, self.author, self.location)
    }
}


pub struct Tweet {
    username: String,
    content: String,
    reply: bool,
    retweet: bool,
}

impl Summarizable for Tweet {
    fn summary(&self) -> String {
        format!("{}: {}", self.username, self.content)
    }
}

pub fn notify<T: Summarizable>(item: T) {
    println!("Breaking News {}", item.summary());
}


fn largest<T: PartialOrd + Copy>(list: &[T]) -> T {
    let mut largest = list[0];
    for &item in list.iter() {
        if item > largest {
            largest = item;
        }
    }
    largest
}

