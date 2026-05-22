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
| windows | `3.9.11.0` | 2026-05-22 | 270.0 MB | `c29fc05630cf` | [installer](https://github.com/TJRoger/wechat-versions-tracker/releases/download/windows-3.9.11.0/WeChat-windows-3.9.11.0.exe) |
<!-- versions:end -->

## Manual trigger

Go to Actions → "Check WeChat Versions" → "Run workflow" to check immediately.

## Sources

| Platform | URL |
| --- | --- |
| Mac | `https://dldir1.qq.com/weixin/mac/WeChatMac.dmg` |
| Windows | `https://dldir1.qq.com/weixin/Windows/WeChatSetup.exe` |
