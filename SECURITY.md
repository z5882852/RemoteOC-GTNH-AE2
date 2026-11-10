# Security policy

Please open a GitHub issue containing only a non-sensitive summary of a suspected
security problem so the maintainer can arrange a private reporting channel. Do
not include exploit details, live server tokens, private URLs, or other
credentials in a public issue.

Before deployment, copy `server/.env.example` to `server/.env` and replace the
placeholder with a unique, long random token. Never commit that file; `.env` files
are ignored by Git.
