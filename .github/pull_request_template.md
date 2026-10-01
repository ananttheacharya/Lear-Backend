## Summary

- 

## Security checklist

- [ ] No real credentials, tokens, private keys, webhook URLs, or customer data are committed.
- [ ] `python scripts/security/secrets_audit.py --working-tree` passes.
- [ ] If touching committed history or fixtures, `python scripts/security/secrets_audit.py --history` passes.
- [ ] If touching FastAPI/server responses, `pytest -q tests/test_security_hardening.py` passes.
- [ ] If changing HTTP middleware, `scripts/check_security_headers.sh http://localhost:8000` or the Python/PowerShell equivalent passes against a live server.
- [ ] New config keys are documented in `.env.example` or docs, with placeholders only.

## Tests run

```text

```

## Notes / limitations

- 
