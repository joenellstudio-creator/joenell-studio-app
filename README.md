# Joe Light Studio

All-in-one photo app for photographers, by **Joenell Studio** (Vancouver, BC).

- **Library & Develop** (Lightroom-style): import, albums, keywords, ratings and flags, raw development
  (Canon CR3, Sony ARW, Nikon NEF, Fuji RAF, DNG…), curves, color mixer, effects, lens corrections,
  Upright, masks, AI denoise, HDR and panorama merge, presets, export, print and slideshows.
- **Edit** (Photoshop-style), bundled inside as **Joe Photo Studio**: layers, layer masks, adjustment
  layers, layer styles, type, vectors, brushes, selections and real PSD files.
  In Joe Light Studio choose **Photo ▸ Edit In ▸ Edit in Joe Photo Studio** (⇧⌘E); save, and the edited
  copy appears in your library next to the original.

## Download (Apple Silicon Macs)

Latest build: [Releases › latest](../../releases/tag/latest) → `joe-light-studio-macos-apple-silicon.dmg`.
Builds are not yet signed with an Apple Developer ID, so macOS may warn the first time you open the app
(Control-click the app ▸ Open).

## In the browser: Joenell Studio Lite

The Library & Develop app also runs in the browser as **Joenell Studio Lite** at
https://lite.joenellstudio.com/ (no install; photos stay in the browser's own storage).
`.github/workflows/web.yml` builds it (`cargo xtask web`) and publishes the site to the `lite-site` branch (deployed by Cloudflare Pages; also a zip on the `web-latest` release) on every
push to `main` that touches the app.

## Building

- `photo-studio/` is Joe Photo Studio's source. `.github/workflows/mac.yml` builds it, nests it in
  `Joe Light Studio.app/Contents/Helpers/`, and packages one DMG.
- Locally on a Mac: `(cd photo-studio && packaging/macos/package.sh --arch aarch64)`, then
  `PHOTO_STUDIO_APP="$PWD/photo-studio/target/macos-package/Joe Photo Studio.app" packaging/macos/package.sh --arch aarch64`.

## Credits and licence

Joe Light Studio is based on the open-source apps **LightCraft** and **PhotoCraft** by the ArtCraft Team
and contributors (https://github.com/storytold/lightcraft, https://github.com/storytold/photocraft),
used under the MIT or Apache-2.0 licence. Their licences and notices are kept unchanged in
[LICENSE-MIT](LICENSE-MIT), [LICENSE-APACHE](LICENSE-APACHE), [NOTICE](NOTICE) and
[photo-studio/](photo-studio/); their original README is in [README.lightcraft.md](README.lightcraft.md).
ArtCraft, LightCraft and PhotoCraft are names of their authors; Joe Light Studio is not endorsed by them.
Changes in this repository are © Joenell Studio, under the same MIT OR Apache-2.0 licence.
