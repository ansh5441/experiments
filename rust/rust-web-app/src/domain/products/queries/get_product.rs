/*! Contains the `GetProductQuery` type. */

use auto_impl::auto_impl;

use domain::Resolver;
use domain::error::{err_msg, Error};
use domain::products::{Product, ProductId, ProductStore};

pub type Result = ::std::result::Result<Product, Error>;

/** Input for a `GetProductQuery`. */
#[derive(Deserialize)]
pub struct GetProduct {
    pub id: ProductId,
}

/** Get a product entity. */
#[auto_impl(Fn)]
pub trait GetProductQuery {
    fn get_product(&self, query: GetProduct) -> Result;
}

/** Default implementation for a `GetProductQuery`. */
pub fn get_product_query(store: impl ProductStore) -> impl GetProductQuery {
    move |query: GetProduct| {
        let product = store.get_product(query.id)?.ok_or(err_msg("not found"))?;

        Ok(product)
    }
}

impl Resolver {
    pub fn get_product_query(&self) -> impl GetProductQuery {
        let store = self.products().product_store();

        get_product_query(store)
    }
}
