# BBG Boardgame 桌游店

一个像素风的桌游店。整个店是一张 640×448 的 canvas，常驻角色各有各的作息，
猫会自己在店里溜达，进度存在 localStorage 里，关掉网页再打开会接着演。

**在线预览：** https://bbg-boardgame.pages.dev/
（GitHub Pages 上的 https://tongyuezhubot.github.io/bbg/ 仍在跑，但 canonical 指向 pages.dev）


角色都写在 `index.html` 的 `CAST` 表里，加一条就能加人：外观字段决定长相，
`role` 决定行为（`owner` / `napper` / `coder` / `clerk` / `regular`）。

## 目录

```
index.html      店本身：全部逻辑、样式、落地页都在这一个文件里
og.png          分享卡片封面 1200×630（微信 / Twitter / Slack 抓这张）
door.png        落地页背景，与封面同一张场景，只是没烤字
favicon.png     浏览器标签页图标 32×32
icon-192.png    apple-touch-icon，加到手机主屏用
icon-512.png    大号图标备用
tools/          离线检视工具（不影响网页运行，纯开发用）
```

首次进站会先看到一张落地页，点「推门进店」才进店；进过一次就记在
localStorage 里不再拦，地址后面加 `#door` 可以强制再看一次。

## 开发工具

工具都是把 `index.html` 里的 `<script>` 抠出来，在 Node 里配一套极简 canvas
光栅器跑起来，所以检查的永远是线上真正在跑的那份代码，不是另抄一份。

```bash
python3 tools/mksim.py && node tools/sim.js   # 无头跑 25 分钟，查行为与存档兼容
node tools/spritelab.js                       # 全员精灵表 sprites.png
node tools/facelab.js                         # 放大的头部对照 faces.png
node tools/scenelab.js                        # 整店一帧 scene.png
node tools/floorlab.js                        # 地板贴图 floor.png
node tools/counterscene.js                    # 收银台 counter.png
node tools/check.js                           # 座位可达性 + ASCII 地图
python3 tools/mkcover.py                      # 重画封面 og.png / door.png 与各尺寸图标
```

`sim.js` 会顺带跑几项回归：走路一律平移、老存档缺角色要补齐、
以及旧存档里的非法状态不能把人卡死。

## 部署

两处都是纯静态，不需要构建步骤。除 `index.html` 外还有几张 PNG 要一起提交。

**GitHub Pages**：指向仓库根目录，push 即生效。

**Cloudflare Pages**（主站，`bbg-boardgame.pages.dev`）：控制台的 Git 集成没接通，
目前是 wrangler 直传，每次要手动跑：

```bash
rm -rf dist && mkdir -p dist/photo
cp index.html *.png dist/ && cp photo/*.jpg dist/photo/
npx wrangler@latest pages deploy dist --project-name bbg-boardgame
```

`dist/` 只是为了不把 `tools/`、`.git` 传上去，已在 .gitignore 里。

分享卡片的 `og:image` 必须是绝对地址，换域名时同步改 `index.html` 里的
`canonical` / `og:url` / `og:image` / `twitter:image` 四处。
