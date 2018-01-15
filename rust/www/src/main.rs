extern crate iron; 
#[macro_use(bson, doc)]
extern crate bson;
extern crate mongodb;

use iron::prelude::*;
use iron::status;

use bson::Bson;
use mongodb::{Client, ThreadedClient};
use mongodb::db::ThreadedDatabase;

fn main() {

	// Direct connection to a server. Will not look for other servers in the topology.
	let client = Client::connect("localhost", 27017)
	    .expect("Failed to initialize client.");
	let coll = client.db("finance_db").collection("btc_collection");
	
	let doc = doc! {};


	// Find the document and receive a cursor
    let mut cursor = coll.find(Some(doc.clone()), None)
        .ok().expect("Failed to execute find.");

    let mut vec = Vec::new();
    let item = cursor.next();

    // cursor.next() returns an Option<Result<Document>>
    match item {
        Some(Ok(doc)) => match doc.get("price_of_bitcoin") {
            Some(&Bson::FloatingPoint(ref price)) => vec.push(price),
            _ => panic!("Expected title to be a string!"),
        },
        Some(Err(_)) => panic!("Failed to get next from server!"),
        None => panic!("Server returned no results!"),
    }




    Iron::new(|_: &mut Request| {
        Ok(Response::with((status::Ok, vec)))
    }).http("localhost:3000").unwrap();
}











