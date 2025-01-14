use crate::types::{request::Request, state::BootstrapState, transaction::OrderedFinalTxs};
use serde::{Deserialize, Serialize};

#[allow(clippy::large_enum_variant)]
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "op", rename_all_fields = "camelCase")]
pub enum ScenarioOp {
    #[serde(rename = "Setup")]
    Setup {
        scenario: String,
        #[cfg(feature = "fixed_expiry_future")]
        start_timestamp: i64,
        version_db: Vec<String>,
        genesis_params: BootstrapState,
        trade_mining_length: u64,
        funding_price_leaves_duration: u64,
        #[cfg(feature = "fixed_expiry_future")]
        expiry_price_leaves_duration: u64,
    },
    #[serde(rename = "Teardown")]
    Teardown,
}

/// Any number of sequential requests
///
/// We send requests in batch to avoid unnecessary HTTP chatter given the data loading use case.
/// The client may send any batch size it wants. Requests are executed in order of batch
/// ordinal and their order in the `requests` list.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RequestBatch(pub Vec<Request>);

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RequestBatchResponse {
    /// The transactions executed in sequential order
    ///
    /// Note that each inner `Tx` contains `state_root_hash` and `request_index`.
    pub txs: OrderedFinalTxs,
    /// Number of requests successfully executed
    ///
    /// This count may be greater than the size of `txs` as not all requests result in a state transition.
    /// If no error, this count is always equal to the number of requests in the batch.
    pub executed: u64,
    /// Error status and reason if one occurred
    ///
    /// We raise errors immediately (stopping execution). There is no batch-level rollback, an error response
    /// may still include successful transactions.
    pub err: Option<String>,
}
