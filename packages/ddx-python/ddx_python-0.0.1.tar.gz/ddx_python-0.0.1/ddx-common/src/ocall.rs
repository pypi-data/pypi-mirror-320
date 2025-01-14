use sgx_types::error::SgxStatus;

extern "C" {
    pub fn ocall_copy_ecall_outcome(
        output_ptr: *const u8,
        output_init_cap: usize,
        output_addr: *mut usize,
        outcome_ptr: *const u8,
        outcome_len: usize,
    ) -> SgxStatus;
}
