FROM rustlang/rust:nightly-2017-12-21
#FROM rust:latest
RUN rustup override set nightly-2017-12-21
RUN cargo install diesel_cli --no-default-features --features postgres

RUN cargo install cargo-watch

WORKDIR /usr/src/app

EXPOSE 3001

VOLUME ["/usr/local/cargo"]
