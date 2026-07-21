# BBG Boardgame 桌游店

一个像素风的桌游店。整个店是一张 640×448 的 canvas，常驻角色各有各的作息，
猫会自己在店里溜达，进度存在 localStorage 里，关掉网页再打开会接着演。

**在线预览：** https://tongyuezhubot.github.io/bbg/


角色都写在 `index.html` 的 `CAST` 表里，加一条就能加人：外观字段决定长相，
`role` 决定行为（`owner` / `napper` / `coder` / `clerk` / `regular`）。

## 目录

```
index.html      整个项目就这一个文件，没有任何外部依赖
tools/          离线检视工具（不影响网页运行，纯开发用）
```

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
```

`sim.js` 会顺带跑几项回归：走路一律平移、老存档缺角色要补齐、
以及旧存档里的非法状态不能把人卡死。

## 部署

GitHub Pages 直接指向仓库根目录即可，`index.html` 自带全部资源，不需要构建步骤。
