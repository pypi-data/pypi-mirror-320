use core::{error, fmt, hash};

use async_channel::Sender;
use async_trait::async_trait;
use serde::{de::DeserializeOwned, Serialize};
use tokio::net::TcpStream;
use tokio_tungstenite::{tungstenite::Message, MaybeTlsStream, WebSocketStream};

use crate::error::BinaryOptionsResult;

use super::{
    client::SenderMessage,
    types::{Data, MessageType, UserRequest},
};

pub trait Credentials: Clone + Send + Sync {}

#[async_trait]
pub trait DataHandler: Clone + Send + Sync {
    type Transfer: MessageTransfer;

    async fn update(&self, message: &Self::Transfer) -> BinaryOptionsResult<()>;
}

#[async_trait]
pub trait Callback: Clone + Send + Sync {
    type T: DataHandler;
    type Transfer: MessageTransfer;

    async fn call(
        &self,
        data: Data<Self::T, Self::Transfer>,
        sender: &SenderMessage<Self::Transfer>,
    ) -> BinaryOptionsResult<()>;
}

pub trait MessageTransfer:
    DeserializeOwned + Clone + Into<Message> + Send + Sync + error::Error + fmt::Debug + fmt::Display
{
    type Error: Into<Self> + Clone + error::Error;
    type TransferError: error::Error;
    type Info: MessageInformation;

    fn info(&self) -> Self::Info;

    fn error(&self) -> Option<Self::Error>;

    fn to_error(&self) -> Self::TransferError;

    fn user_request(&self) -> Option<UserRequest<Self>>;

    fn new_user(request: UserRequest<Self>) -> Self;

    fn error_info(&self) -> Option<Vec<Self::Info>>;
}

pub trait MessageInformation:
    Serialize + DeserializeOwned + Clone + Send + Sync + Eq + hash::Hash + fmt::Debug + fmt::Display
{
    fn none(&self) -> Self;
}

#[async_trait]
/// Every struct that implements MessageHandler will recieve a message and should return
pub trait MessageHandler: Clone + Send + Sync {
    type Transfer: MessageTransfer;

    async fn process_message(
        &self,
        message: &Message,
        previous: &Option<<<Self as MessageHandler>::Transfer as MessageTransfer>::Info>,
        sender: &Sender<Message>,
    ) -> BinaryOptionsResult<(Option<MessageType<Self::Transfer>>, bool)>;
}

#[async_trait]
pub trait Connect: Clone + Send + Sync {
    type Creds: Credentials;
    // type Uris: Iterator<Item = String>;

    async fn connect(
        &self,
        creds: Self::Creds,
    ) -> BinaryOptionsResult<WebSocketStream<MaybeTlsStream<TcpStream>>>;
}
