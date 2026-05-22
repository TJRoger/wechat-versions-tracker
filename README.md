# wechat-versions-tracker

Tracks WeChat Mac and Windows installer versions. A GitHub Actions workflow checks the official Tencent CDN daily, and when a new version appears, the installer is archived as a GitHub Release asset.

## How it works

1. Daily cron job downloads the latest installers from Tencent CDN
2. Extracts version numbers (plist for Mac, PE metadata for Windows)
3. If a version is new, creates a GitHub Release and uploads the installer
4. Updates `versions.json` and this README

## Tracked versions

<!-- versions:start -->
_No versions tracked yet._
<!-- versions:end -->

## Manual trigger

Go to Actions → "Check WeChat Versions" → "Run workflow" to check immediately.

## Sources

| Platform | URL |
| --- | --- |
| Mac | `https://dldir1.qq.com/weixin/mac/WeChatMac.dmg` |
| Windows | `https://dldir1.qq.com/weixin/Windows/WeChatSetup.exe` |
