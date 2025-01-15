use binary_option_tools_core::{
    error::BinaryOptionsToolsError, pocketoption::error::PocketOptionError,
};
use pyo3::{exceptions::PyValueError, PyErr};
use thiserror::Error;
use uuid::Uuid;

#[derive(Error, Debug)]
pub enum BinaryErrorPy {
    #[error("PocketOptionError, {0}")]
    PocketOptionError(#[from] PocketOptionError),
    #[error("BinaryOptionError, {0}")]
    BinaryOptionError(#[from] BinaryOptionsToolsError),
    #[error("Uninitialized, {0}")]
    Uninitialized(String),
    #[error("Error descerializing data, {0}")]
    DeserializingError(#[from] serde_json::Error),
    #[error("UUID parsing error, {0}")]
    UuidParsingError(#[from] uuid::Error),
    #[error("Trade not found, haven't found trade for id '{0}'")]
    TradeNotFound(Uuid),
}

impl From<BinaryErrorPy> for PyErr {
    fn from(value: BinaryErrorPy) -> Self {
        PyValueError::new_err(value.to_string())
    }
}

pub type BinaryResultPy<T> = Result<T, BinaryErrorPy>;
