# wechat-versions-tracker

Tracks WeChat Mac and Windows installer versions. A GitHub Actions workflow checks the official Tencent CDN daily, and when a new version appears, the installer is archived as a GitHub Release asset.

## How it works

1. Daily cron job downloads the latest installers from Tencent CDN
2. Extracts version numbers (plist for Mac, PE metadata for Windows)
3. If a version is new, creates a GitHub Release and uploads the installer
4. Updates `versions.json` and this README

## Tracked versions

<!-- versions:start -->
| Platform | Version | Date | Size | SHA256 | Download |
| --- | --- | --- | --- | --- | --- |
| mac | `4.1.10` | 2026-06-11 | 468.0 MB | `229ef9136029` | [installer](https://github.com/TJRoger/wechat-versions-tracker/releases/download/mac-4.1.10/WeChat-mac-4.1.10.dmg) |
| mac | `4.1.9` | 2026-06-11 | 466.0 MB | `531f5dc9c4cc` | [installer](https://github.com/TJRoger/wechat-versions-tracker/releases/download/mac-4.1.9/WeChat-mac-4.1.9.dmg) |
| mac | `4.1.8` | 2026-06-11 | 461.0 MB | `972823a966cd` | [installer](https://github.com/TJRoger/wechat-versions-tracker/releases/download/mac-4.1.8/WeChat-mac-4.1.8.dmg) |
| mac | `4.1.7` | 2026-06-11 | 457.9 MB | `4ee1f0e33f91` | [installer](https://github.com/TJRoger/wechat-versions-tracker/releases/download/mac-4.1.7/WeChat-mac-4.1.7.dmg) |
| mac | `4.1.6` | 2026-06-11 | 448.1 MB | `a0468c8b53ba` | [installer](https://github.com/TJRoger/wechat-versions-tracker/releases/download/mac-4.1.6/WeChat-mac-4.1.6.dmg) |
| mac | `4.1.5` | 2026-06-11 | 422.8 MB | `8a7227f2094e` | [installer](https://github.com/TJRoger/wechat-versions-tracker/releases/download/mac-4.1.5/WeChat-mac-4.1.5.dmg) |
| mac | `4.1.4` | 2026-06-11 | 412.5 MB | `90622436d1d6` | [installer](https://github.com/TJRoger/wechat-versions-tracker/releases/download/mac-4.1.4/WeChat-mac-4.1.4.dmg) |
| mac | `4.1.2` | 2026-06-11 | 408.8 MB | `85f42e65cc72` | [installer](https://github.com/TJRoger/wechat-versions-tracker/releases/download/mac-4.1.2/WeChat-mac-4.1.2.dmg) |
| windows | `3.9.11.0` | 2026-05-22 | 270.0 MB | `c29fc05630cf` | [installer](https://github.com/TJRoger/wechat-versions-tracker/releases/download/windows-3.9.11.0/WeChat-windows-3.9.11.0.exe) |
<!-- versions:end -->

## Manual trigger

Go to Actions → "Check WeChat Versions" → "Run workflow" to check immediately.

## Sources

| Platform | URL |
| --- | --- |
| Mac | `https://dldir1v6.qq.com/weixin/Universal/Mac/WeChatMac.dmg` |
| Windows | `https://dldir1.qq.com/weixin/Windows/WeChatSetup.exe` |
