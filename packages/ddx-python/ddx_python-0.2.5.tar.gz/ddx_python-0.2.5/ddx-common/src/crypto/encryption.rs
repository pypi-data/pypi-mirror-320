use crate::{
    Result,
    constants::{AES_KEY_LEN, AES_NONCE_LEN},
    error,
};
use aes_gcm::aead::Buffer;

// Performs the encryption and decryption in untrusted mode.
#[cfg(not(target_vendor = "teaclave"))]
pub(crate) mod untrusted {
    use super::*;
    use aes_gcm::{Aes128Gcm, Key, KeyInit, Nonce, aead::AeadInPlace};
    pub fn do_encrypt_with_nonce(
        ciphertext: &mut dyn Buffer,
        key_fixed_bytes: [u8; AES_KEY_LEN],
        nonce_fixed_bytes: [u8; AES_NONCE_LEN],
    ) -> Result<()> {
        let key = Key::<Aes128Gcm>::from_slice(&key_fixed_bytes);
        let cipher: Aes128Gcm = Aes128Gcm::new(key);
        let nonce = Nonce::from(nonce_fixed_bytes);
        cipher
            .encrypt_in_place(&nonce, b"", ciphertext)
            .map_err(|source| error!("{:?}", source))?;
        Ok(())
    }

    pub fn do_decrypt(
        ciphertext: &mut Vec<u8>,
        key_fixed_bytes: [u8; AES_KEY_LEN],
        nonce_fixed_bytes: [u8; AES_NONCE_LEN],
    ) -> Result<()> {
        tracing::debug!("Untrusted decrypt - Ciphertext size {:?}", ciphertext.len());
        let key = Key::<Aes128Gcm>::from_slice(&key_fixed_bytes);

        tracing::trace!("Aes256GcmSiv::new - BEGIN");
        // Set to software mode in Cargo.toml. The default behavior causes the operator
        //  to silently crash here:
        let cipher: Aes128Gcm = Aes128Gcm::new(key);
        tracing::trace!("Aes256GcmSiv::new - COMPLETE");

        let nonce = Nonce::from(nonce_fixed_bytes);

        // Decrypt `buffer` in-place, replacing its ciphertext context with the original plaintext
        tracing::trace!("decrypt_in_place - BEGIN");
        cipher
            .decrypt_in_place(&nonce, b"", ciphertext)
            .map_err(|source| error!("{:?}", source))?;
        tracing::trace!("decrypt_in_place - COMPLETE");

        Ok(())
    }
}

#[cfg(target_vendor = "teaclave")]
pub(crate) mod trusted {
    use super::*;
    use sgx_crypto::aes::gcm::{Aad, AesGcm};

    pub fn do_encrypt_with_nonce(
        ciphertext: &mut dyn Buffer,
        key_fixed_bytes: [u8; AES_KEY_LEN],
        nonce_fixed_bytes: [u8; AES_NONCE_LEN],
    ) -> Result<()> {
        let aad = Aad::empty();
        let mut cipher = AesGcm::new(&key_fixed_bytes, nonce_fixed_bytes.into(), aad)
            .map_err(|source| error!("{:?}", source))?;
        cipher
            .enc_update_in_place(ciphertext.as_mut())
            .map_err(|source| error!("{:?}", source))?;
        Ok(())
    }

    pub fn do_decrypt(
        ciphertext: &mut Vec<u8>,
        key_fixed_bytes: [u8; AES_KEY_LEN],
        nonce_fixed_bytes: [u8; AES_NONCE_LEN],
    ) -> Result<()> {
        let aad = Aad::empty();
        let mut cipher = AesGcm::new(&key_fixed_bytes, nonce_fixed_bytes.into(), aad)
            .map_err(|source| error!("{:?}", source))?;
        unsafe {
            cipher
                .dec_update_in_place(ciphertext.as_mut())
                .map_err(|source| error!("{:?}", source))?;
        }
        Ok(())
    }
}
