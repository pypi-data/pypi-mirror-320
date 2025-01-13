## 1.28.4 - 2025-01-12
### Extractors
#### Additions
- [pexels] add support ([#2286](https://github.com/mikf/gallery-dl/issues/2286), [#4214](https://github.com/mikf/gallery-dl/issues/4214), [#6769](https://github.com/mikf/gallery-dl/issues/6769))
- [weebcentral] add support ([#6778](https://github.com/mikf/gallery-dl/issues/6778))
#### Fixes
- [bunkr] update to new site layout ([#6798](https://github.com/mikf/gallery-dl/issues/6798), [#6805](https://github.com/mikf/gallery-dl/issues/6805))
- [bunkr] fix `ValueError` on relative redirects ([#6790](https://github.com/mikf/gallery-dl/issues/6790))
- [plurk] fix `user` data extraction and make it non-fatal ([#6742](https://github.com/mikf/gallery-dl/issues/6742))
#### Improvements
- [bunkr] support `/f/` media URLs
- [e621] accept `tag` search URLs with empty tag ([#6783](https://github.com/mikf/gallery-dl/issues/6783))
- [pixiv] provide fallback URLs ([#6762](https://github.com/mikf/gallery-dl/issues/6762))
- [wallhaven] extract `search[tags]` and `search[tag_id]` metadata ([#6772](https://github.com/mikf/gallery-dl/issues/6772))
### Miscellaneous
- [util] support not splitting `value` argument when calling `contains()`  ([#6773](https://github.com/mikf/gallery-dl/issues/6773))
