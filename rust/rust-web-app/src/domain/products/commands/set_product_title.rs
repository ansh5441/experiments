/*! Contains the `SetProductTitleCommand`. */

use auto_impl::auto_impl;

use domain::Resolver;
use domain::error::{err_msg, Error};
use domain::products::{ProductId, ProductStore};

pub type Result = ::std::result::Result<(), Error>;

/** Input for a `SetProductTitleCommand`. */
#[derive(Clone, Deserialize)]
pub struct SetProductTitle {
    pub id: ProductId,
    pub title: String,
}

/** Set a new title for a product. */
#[auto_impl(FnMut)]
pub trait SetProductTitleCommand {
    fn set_product_title(&mut self, command: SetProductTitle) -> Result;
}

/** Default implementation for a `SetProductTitleCommand`. */
pub fn set_product_title_command(store: impl ProductStore) -> impl SetProductTitleCommand {
    move |command: SetProductTitle| {
        let product = {
            if let Some(mut product) = store.get_product(command.id)? {
                product.set_title(command.title)?;

                product
            } else {
                Err(err_msg("not found"))?
            }
        };

        store.set_product(product)
    }
}

impl Resolver {
    pub fn set_product_title_command(&self) -> impl SetProductTitleCommand {
        let store = self.products().product_store();

        set_product_title_command(store)
    }
}
