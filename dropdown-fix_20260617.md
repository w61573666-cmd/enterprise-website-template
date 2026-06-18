# 工程案例下拉菜单修复

## 问题
products.html 导航栏中"工程案例"下拉项（酒店與度假村、商業空間工程等）直接显示在导航栏内，未被隐藏。

## 根因
两个层面冲突：

### 1. 内联 `<style>` 冲突
22个 HTML 文件的 `<style>` 标签内含精简版 `.dropdown-panel` 和 `.nav-dropdown:hover .dropdown-panel` CSS 规则：
- `.dropdown-panel { display: none; z-index: 999; ... }`
- `.nav-dropdown:hover .dropdown-panel { display: grid !important; }`

仅设置 display 了事，未设 opacity/visibility。

### 2. JavaScript 手动控制
内联 JS 通过 mouseenter/mouseleave 设置 `dropPanel.style.display = 'block'` / `'none'`：
```js
projNav.addEventListener('mouseenter', function(){ dropPanel.style.display='block'; });
projNav.addEventListener('mouseleave', function(){ dropTimer=setTimeout(function(){ dropPanel.style.display='none'; },200); });
```

JS 的 inline style 属性 (`display: block`) 与内联stylesheet (`display: none`) 与外部CSS (`opacity: 0; visibility: hidden; display: grid`) 三者互相冲突，导致特定条件下下拉面板异常可见。

## 修复方案
1. 从22个HTML文件的内联 `<style>` 中删除 `.dropdown-panel` 及 `.nav-dropdown:hover .dropdown-panel` CSS 规则
2. 从22个HTML文件的内联 `<script>` 中删除 dropPanel 手动控制 JS 块（var projDropdowns + if(projNav&&dropPanel) 代码）
3. 统一由外部 CSS (`style-202605042143.css`) 的纯 CSS hover 方案控制：默认 `opacity: 0; visibility: hidden;`，hover 时 `opacity: 1; visibility: visible;`

## 修改文件 (22个)
- products.html
- en/products.html
- products/*.html (10个产品子页面)
- en/products/*.html (10个英文产品子页面)

## Commit
`d47eb6e` — 22 files changed, 272 deletions
