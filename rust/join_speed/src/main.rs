use std::fs::File;
use std::io::prelude::*;
use std::time::Instant;

fn main() {
    let mut f = File::open("/Users/ansh/code/experiments/pyth/sample.txt").expect("file not found");

    let mut contents = String::new();
    f.read_to_string(&mut contents)
        .expect("something went wrong reading the file");

    let x: Vec<&str> = contents.split("\n").collect();
    let mut arr_1: Vec<&str> = Vec::new();
    let mut arr_2: Vec<&str> = Vec::new();

    for &elem in x.iter() {
        let y: Vec<&str> = elem.split(" ").collect();
        if y.len() == 2 {
            arr_1.push(y[0]);
            arr_2.push(y[1]);
        }
    }
    let start = Instant::now();
    let mut i = 0;
    let mut j = 0;
    let len_1 = arr_1.len();
    let len_2 = arr_2.len();
    let mut match_arr: Vec<&str> = Vec::new();
    while i < len_1 && j < len_2 {
        if arr_1[i] < arr_2[j] {
            i += 1;
        } else if arr_1[i] > arr_2[j] {
            j += 1
        } else {
            match_arr.push(arr_1[i]);
            i += 1;
            j += 1;
        }
    }
    let elapsed = start.elapsed();
    println!("found {} matches in {:?} seconds.", match_arr.len(), elapsed);
}


//fn find_common(arr_1: &Vec<&str>, arr_2: &Vec<&str>) -> Vec<&str> {
//    let mut i = 0;
//    let mut j = 0;
//    let len_1 = arr_1.len();
//    let len_2 = arr_2.len();
//    let mut match_arr: Vec<&str> = Vec::new();
//    while i < len_1 && j < len_2{
//        if arr_1[i] < arr_2[j]{
//            i += 1;
//        } else if  arr_1[i] > arr_2[j] {
//            j += 1
//        } else {
//            match_arr.push(arr_1[i]);
//            i += 1;
//            j += 1;
//        }
//
//    }
//    match_arr
//}