# Portable qualification

The initial `qualify.py` and its frozen source remain unchanged. The separately hash-bound `qualify_portable.py` runs the same controls with native Docker on Linux or Docker through WSL on Windows. `PORTABILITY-AMENDMENT.json` records both source identities and the invocation-only change.

From the extracted eval root on Linux:

```sh
python3 owner/semantic-successor/qualify_portable.py
```

Actual native Linux/Docker qualification passed **10/10 component controls**; receipts are in `QUALIFICATION-PORTABLE.json`. Windows/WSL qualification is preserved in `QUALIFICATION.json`. Neither result changes the post-outcome condition or qualifies full-system isolation, human review, or universal semantic correctness. Disposable `work/` staging is removed after each control and should be excluded from archive construction if qualification is running concurrently.
