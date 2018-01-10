extern crate iron;
extern crate time;

use iron::prelude::*;
use iron::{BeforeMiddleware, AfterMiddleware, typemap};
use time::precise_time_ns;


extern crate router;

use iron::status;
use router::Router;


struct ResponseTime;

impl typemap::Key for ResponseTime { type Value = u64; }

impl BeforeMiddleware for ResponseTime {
    fn before(&self, req: &mut Request) -> IronResult<()> {
        req.extensions.insert::<ResponseTime>(precise_time_ns());
        Ok(())
    }
}

impl AfterMiddleware for ResponseTime {
    fn after(&self, req: &mut Request, res: Response) -> IronResult<Response> {
        let delta = precise_time_ns() - *req.extensions.get::<ResponseTime>().unwrap();
        println!("Request took: {} ms", (delta as f64) / 1000000.0);
        Ok(res)
    }
}

fn hello_world(_: &mut Request) -> IronResult<Response> {
    Ok(Response::with((iron::status::Ok, "Hello World")))
}

fn main() {
//    let mut chain = Chain::new(hello_world);
//    chain.link_before(ResponseTime);
//    chain.link_after(ResponseTime);
//    Iron::new(chain).http("localhost:3000").unwrap();


    let mut router = Router::new();           // Alternative syntax:
    router.get("/", handler, "index");        // let router = router!(index: get "/" => handler,
    router.get("/:query", handler, "query");  //                      query: get "/:query" => handler);

    Iron::new(router).http("localhost:3000").unwrap();

    fn handler(req: &mut Request) -> IronResult<Response> {
        let ref query = req.extensions.get::<Router>().unwrap().find("query").unwrap_or("/");
        Ok(Response::with((status::Ok, *query)))
    }
}