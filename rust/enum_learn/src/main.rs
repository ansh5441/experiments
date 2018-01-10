#[allow(unused_variables)]
fn main() {
    lear();
}

#[allow(unused_variables)]
fn lear() {
    enum IpAddressKind {
        V4,
        V6,
    }

    let four = IpAddressKind::V4;
    let six = IpAddressKind::V6;

    fn route(ip_type: IpAddressKind) {}
    //__________________________________________________________________________________________________
    enum IpAddr {
        V4(String),
        V6(String),
    }
    let home = IpAddr::V4(String::from("127.0.0.1"));
    let loopback = IpAddr::V6(String::from("::1"));

    //__________________________________________________________________________________________________
    enum IpAddrV2 {
        V4(u8, u8, u8, u8),
        V6(String),
    }
    let home = IpAddrV2::V4(127, 0, 0, 1);
    let loopback = IpAddrV2::V6(String::from("::1"));

    //__________________________________________________________________________________________________
    #[derive(Debug)]
    enum Message {
        Quit,
        // anonymous struct
        Move { x: i32, y: i32 },
        Write(String),
        ChangeColour(i32, i32, i32), // tuple
    }

    impl Message {
        fn call(&self) {
            println!("The message is {:?}", self);
        }
    }

    let m = Message::Write(String::from("Hello"));

    m.call();

//__________________________________________________________________________________________________

    enum Coin {
        Penny,
        Nickel,
        Dime,
        Quarter,
    }
    fn value_in_cents(coin: Coin) -> u32 {
        match coin {
            Coin::Penny => 1,
            Coin::Nickel => 5,
            Coin::Dime => 10,
            Coin::Quarter => 25,
        }
    }
//__________________________________________________________________________________________________

    #[derive(Debug)] // So we can inspect the state in a minute
    enum UsState {
        Alabama,
        Alaska,
        // ... etc
    }

    enum CoinV2 {
        Penny,
        Nickel,
        Dime,
        Quarter(UsState),
    }

    fn value_in_cents_v2(coin: CoinV2) -> u32 {
        match coin {
            CoinV2::Penny => 1,
            CoinV2::Nickel => 5,
            CoinV2::Dime => 10,
            CoinV2::Quarter(state) => {
                println!("State coin from {:?}", state);
                25
            }
        }
    }
    let coin = CoinV2::Quarter(UsState::Alaska);
    value_in_cents_v2(coin);
//__________________________________________________________________________________________________
    fn plus_one(x: Option<i32>) -> Option<i32> {
        match x {
            None => None,
            Some(q) => Some(q + 1),
        }
    }
    println!("{:?}, {:?}, {:?}", plus_one(Some(20)), plus_one(Some(203)), plus_one(None));
//__________________________________________________________________________________________________
    let some_u8_value = Some(0u8);
    if let Some(3) = some_u8_value {
        println!("three");
    }
//__________________________________________________________________________________________________
    let coin = CoinV2::Quarter(UsState::Alaska);

    let mut count = 0;
    if let CoinV2::Quarter(state) = coin {
        println!("State quarter from {:?}!", state);
    } else {
        count += 1;
    }
}

