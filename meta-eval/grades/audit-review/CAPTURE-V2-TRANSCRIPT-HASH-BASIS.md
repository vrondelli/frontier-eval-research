# V2 transcript hash basis

The frozen V2runner computes transcript_sha256 from the UTF8stdout text before writing the file. On Windows, read/communicate normalizes line endings and write_text emits CRLF. Consequently the raw file SHA differs from the recorded text SHA for both coached attempts. This is an instrument schema/basis issue, not evidence that transcript content changed after capture.

For both files, independently hashing read_text(encoding='utf-8').encode() exactly equals the recorded field; direct raw file hashes are separately retained by the final custody audit. That interpretation is licensed by the frozen runner code, not an arbitrary post-outcome normalization. ALL-ATTEMPT-CUSTODY-BEFORE-HASH-BASIS.json retains the initial raw-hash mismatch observation. No raw log, launch receipt or frozen runner was edited.

The current audit therefore reports both event-text integrity against the prearchive text hash and raw-file identity as newly inventoried bytes. It does not call the normalized text hash a prearchive raw-byte hash. Public release redactions are a separate later transformation with their own original/public hash map.
