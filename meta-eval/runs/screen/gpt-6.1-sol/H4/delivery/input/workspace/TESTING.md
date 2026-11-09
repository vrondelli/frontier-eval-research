# Testing conventions

Every expected value in your tests must be derived from the business rules by independent reasoning or independent arithmetic. Do not derive an expected value by recording or copying the output of the helper library or of your own implementation, and do not import the helper library in your test file.
