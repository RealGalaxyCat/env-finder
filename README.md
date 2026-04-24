# EnvFinder

EnvFinder is a security research tool that helps identify accidentally exposed configuration
files (.env files) in public github repositories to support responsible disclosure and defensive
analysis.

---

## Todo

- [ ] Replace logging System with stdlib logging module
- [x] Improve Log Messages
- [ ] Implement logic to filter out known default .env files using hash blacklist
- [ ] Add more hashes for default .env files
- [ ] Add type hints in github.py
- [ ] Handle unsuccessful responses in github.py
- [ ] Add retry logic for failed requests
- [ ] Catch SSL Errors

---

## Responsible Use

This tool is intended for ethical security research and defensive analysis only.

Users are responsible for complying with:
- GitHub Terms of Service
- Applicable laws and regulations
- Responsible disclosure practices

Do not use this tool to access systems without authorization.
