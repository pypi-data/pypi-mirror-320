use crate::{constants::EXEC_OUTCOME_MSG_MAX_SIZE, types::transaction::PostProcessingRequest};
use anyhow::{Error, anyhow};
use serde::{Deserialize, Serialize};
use std::{convert::TryFrom, string::String};

#[derive(thiserror::Error, Debug)]
pub enum ExecutionError {
    #[error("Skippable error {} - Roll-back the state", _0)]
    Skippable(String),

    #[error("Retryable error {} - Try executing again", _0)]
    Retryable(String),
}

impl From<serde_json::Error> for ExecutionError {
    fn from(e: serde_json::Error) -> Self {
        ExecutionError::Retryable(format!("{:?}", e))
    }
}

/// The result of a transaction execution including possible recoverable errors
///
/// Execution is a multi step process, this delivers a `PostProcessingRequest` containing
/// the inputs for commitment in untrusted context.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ExecutionOutcome {
    Success(PostProcessingRequest),
    Skip(String),
    Retry(String),
}

impl Default for ExecutionOutcome {
    fn default() -> Self {
        ExecutionOutcome::Success(PostProcessingRequest::Done)
    }
}

impl From<ExecutionError> for ExecutionOutcome {
    fn from(e: ExecutionError) -> Self {
        match e {
            ExecutionError::Retryable(e) => {
                let mut msg = format!("{:?}", e);
                msg.truncate(EXEC_OUTCOME_MSG_MAX_SIZE);
                ExecutionOutcome::Retry(msg)
            }
            ExecutionError::Skippable(e) => {
                let mut msg = format!("{:?}", e);
                msg.truncate(EXEC_OUTCOME_MSG_MAX_SIZE);
                ExecutionOutcome::Skip(msg)
            }
        }
    }
}

impl TryFrom<ExecutionOutcome> for ExecutionError {
    type Error = Error;

    fn try_from(value: ExecutionOutcome) -> Result<Self, Self::Error> {
        match value {
            ExecutionOutcome::Skip(inner) => Ok(ExecutionError::Skippable(inner)),
            ExecutionOutcome::Retry(inner) => Ok(ExecutionError::Retryable(inner)),
            ExecutionOutcome::Success(_) => Err(anyhow!(
                "Trying to convert ExecutionOutcome::Success into ExecutionError"
            )),
        }
    }
}

pub type ExecutionResult<T> = Result<T, ExecutionError>;

#[macro_export]
macro_rules! skip_if {
    ($guard: expr, $msg: expr) => {
        if $guard {
            return Err(ExecutionError::Skippable($msg));
        }
    };
    ($guard: expr) => {
        $guard.map_err(|e| ExecutionError::Skippable(e.to_string()))
    };
}

#[macro_export]
macro_rules! retry_if {
    ($guard: expr, $msg: expr) => {
        if $guard {
            return Err(ExecutionError::Retryable($msg));
        }
    };
    ($guard: expr) => {
        $guard.map_err(|e| ExecutionError::Retryable(e.to_string()))
    };
}

#[cfg(test)]
pub mod tests {
    use core::convert::TryInto;

    use crate::{ExecutionError, ExecutionOutcome, types::transaction::PostProcessingRequest};

    #[test]
    fn try_from_execution_error_to_outcome() {
        let msg = "A".to_string();
        match ExecutionOutcome::Skip(msg.clone()).try_into().unwrap() {
            ExecutionError::Skippable(s) if s == msg => {}
            _ => panic!("Invalid conversion"),
        }

        match ExecutionOutcome::Retry(msg.clone()).try_into().unwrap() {
            ExecutionError::Retryable(s) if s == msg => {}
            _ => panic!("Invalid conversion"),
        }
    }

    #[test]
    #[should_panic]
    fn try_from_execution_error_to_outcome_panics() {
        let _x: ExecutionError = ExecutionOutcome::Success(PostProcessingRequest::Done)
            .try_into()
            .unwrap();
    }
}
