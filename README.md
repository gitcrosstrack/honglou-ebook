# 一卷红楼

《红楼梦》全一百二十回的插画网页电子书。宣纸底色、宋体正文与朱砂点缀，支持电脑和手机阅读。

![卷首山水](assets/mountain.webp)

- 120 回完整原文，按十回分组的可搜索目录及上一回／下一回切换。
- 120 回均配有对应情节的插画，共 122 幅新绘图片（含封面及第一回两幅插画）；第八回另保留四幅底本图式。
- 字号、行距、宣纸／素白／夜读三种底色。
- 跨章节书签与上次阅读位置，保存在当前浏览器。
- 没有前端构建依赖，也不依赖在线字体、CDN 或远程图片。

## 阅读

在线：[https://gitcrosstrack.github.io/honglou-ebook/](https://gitcrosstrack.github.io/honglou-ebook/)

下载仓库后，直接打开 `index.html` 即可阅读；也可运行：

```sh
python3 -m http.server 8000
```

在浏览器访问 `http://localhost:8000`。支持 `#chapter-3` 等章节链接。未开启 JavaScript 时显示全 120 回连续正文。

## 原文与校验

采用维基文库《红楼梦》汇校本的**简体显示文本**。前八十回据庚辰本，后四十回据程甲本；采用来源汇校文本。各回回目以该底本为准，不和其他版本混合。全书共 862,670 个字符、2,396 个文字段落。完整来源 HTML、固定修订号与摘要分别保存于 `sources/` 和 `data/chapters.json`。

正文及诗词保留字词、标点、异文和段内换行。只调整排版，脚注编号移至独立注释栏。第八回宝玉及金锁图式直接保留底本原图。第一回底本附录的回前文字与诗仍按原顺序收录，其性质见底本注释。

校验脚本独立重新解析保存的来源 HTML，与成品 HTML 中每一回的正文节点逐段比较；同时核对回目、文本 SHA-256、底本快照 SHA-256，以及四幅原图字节摘要。校验对象是所选数字底本，不代表所有古本之间没有异文。

```sh
python3 -m pip install -r requirements.txt
python3 scripts/import_sources.py
python3 scripts/build.py
python3 scripts/verify.py
python3 scripts/package.py build
```

`import_sources.py` 读取已经保存的 HTML；四幅原图缺失时才从原来源下载。构建与校验不生成或改写小说内容。`build/红楼梦全120回.html` 为图片、样式和脚本全部内嵌的离线单文件。

## 配图

全 120 回配图已完成。`data/render-progress.json` 保存完整进度；本次完成过程中未触发生图限流。

`data/illustrations.json` 保存每幅图对应的章节、段落索引和原文片段。插画放在对应情节之前，页面可点击“对应原文”定位。`data/image-prompts.json` 保存生成及修正提示词。绘图采用内置 `image_gen`，不冒充历史古画。

## 目录结构

```text
index.html             生成的网页
styles.css / reader.js 生成的样式与交互
src/                   页面模板、样式、阅读器源码
assets/                新绘插画与底本原图
sources/               120 回来源 HTML 快照
data/                  底本数据、配图对应关系、校验结果
scripts/               导入、构建、校验、离线打包
```

阅读器代码采用 MIT 许可。小说原作属于公有领域；维基文库数字化文本、校注与原图的许可及署名信息见各自来源页面，仓库不为这些来源材料附加许可限制。
