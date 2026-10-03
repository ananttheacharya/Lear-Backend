## Summary

- 

## Security checklist

- [ ] No real credentials, tokens, private keys, webhook URLs, or customer data are committed.
- [ ] `python scripts/security/secrets_audit.py --working-tree` passes.
- [ ] If touching committed history or fixtures, `python scripts/security/secrets_audit.py --history` passes.
- [ ] If touching FastAPI/server responses, `pytest -q tests/test_security_hardening.py` passes.
- [ ] If changing HTTP middleware, `python scripts/security/check_security_headers.py http://localhost:8000` passes against a live server, or `pytest -q tests/test_security_hardening.py` covers the change without a daemon.
- [ ] New config keys are documented in `.env.example` or docs, with placeholders only.

## Tests run

```text

```

## Notes / limitations

- 
