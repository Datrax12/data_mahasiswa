# TODO - Fix Export CSV Error & Enable Download

- [ ] Inspect current `/export` implementation
- [ ] Fix internal server error by using absolute paths for `data/` and `static/` (based on `__file__`)
- [ ] Change `/export` to return CSV as a direct download (`flask.send_file` from in-memory or BytesIO)
- [ ] Keep existing flash+redirect behavior only if needed; prefer download response
- [ ] Optional: update template/button remains `<a href="/export">`
- [ ] Run quick local test: call `/export` and verify browser downloads CSV

