# CONTRIBUTING.md
## 開発方法
FFmpegはLGPL版をビルド、またはビルド済みZIPをダウンロードしてください。
ffmpeg/bin/にffmpeg.exeが来るようにしてください。

yt-dlpはGithubの[yt-dlp/yt-dlp](https://github.com/yt-dlp/yt-dlp#release-files)よりexeをダウンロードし、main.pyと同じ階層に配置してください。

開発環境は3.13.3ですが、その他のバージョンでも構いません。requirements.txtはpyinstallerと、その依存関係のみです。ソフトウェア本体は、Tkinterを使用しているため、PCにTkinterが導入されている必要があります。

[conv.spec](conv.spec)はpyinstallerの設定ファイルです。

[setup.iss](setup.iss)は[Inno Setup](https://jrsoftware.org/isinfo.php)の設定ファイルです。

## 貢献
Issue、PRは自由に投げてもらって構いません。
