# weavslide

自动生成讲座展示和 AI 配音的工具

## .slide.html 文件格式

每个 `.slide.html` 文件描述一页幻灯片，包含三个顶级元素：

### `<slide>` — 幻灯片内容

可包含任意 HTML，用于组成最终的演示文稿页面。

### `<thoughts>` — 思路要点

可包含任意 HTML，仅需存放该页幻灯片的思考要点片段。

### `<spoken>` — 口播文案

TTS 语音合成的文本来源。内容必须完全口语化，包含语气词和停顿。

- `<spoken>` 顶级元素内**只能**包含 `<p>` 子元素，不得放入其他 HTML 标签。

### 示例

```html
<slide>
  <h1>欢迎</h1>
  <ul>
    <li>今天的话题</li>
    <li>关于我们</li>
  </ul>
</slide>

<thoughts>
  <p>开场白，介绍自己和今天主题</p>
</thoughts>

<spoken>
  <p>大家好，欢迎来到今天的分享。</p>
  <p>嗯，我是今天的主讲人，咱们今天聊聊一个挺有意思的话题。</p>
</spoken>
```

## CLI 命令

安装后可通过 `weavslide` 命令使用，或用 `uv run weavslide` 直接运行。

### `validate` — 验证输入文件

```bash
# 扫描当前目录所有 .slide.html 文件
weavslide validate

# 指定文件
weavslide validate slides/01-opening.slide.html slides/02-basics.slide.html
```

### `preview` — 预览讲座展示

将所有 `.slide.html` 文件的 `<slide>` 内容拼成完整 HTML，用浏览器预览。

```bash
weavslide preview

# 使用自定义 CSS
weavslide preview --css my-theme.css
```

## 许可证

本项目基于 [MIT License](LICENSE) 发布。
