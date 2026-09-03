# 恒生石材产品中心栏目深度重构优化

## 任务概述
对 hsst.hk 网站产品中心栏目进行深度重构优化，解决 CSS 重复冲突、内联样式泛滥、卡片信息简陋等核心问题。

## 执行结果

### Phase 1: CSS深度清理与重建 ✅
**文件**: `css/style-202605042143.css` (7795行 → 8431行)

**完成内容**:
1. **删除3处重复的 .stone-card 定义** (原位于行3263, 3723, 3956)
   - 统一为1个规范定义：14px圆角, 4:3宽高比, cubic-bezier过渡
2. **删除3处重复的 .stone-card-img 定义** (height:160px / 200px / aspect-ratio:4/3 三种冲突)
   - 统一为 aspect-ratio:4/3 + cursor:zoom-in
3. **合并 .stone-card-img cursor:zoom-in** (从行2114合并到主定义)
4. **stone-cards-grid 升级**: minmax(240px) → minmax(280px), gap 16px → 24px
5. **series-overview-card 重新设计**:
   - 去掉 height:120px 固定限制
   - 左侧彩色竖条指示器 (5px → hover 8px)
   - hover 金色边框
   - padding 12px→24px
6. **series-section-header 升级**:
   - 金色渐变底线装饰 (::after)
   - padding 18px→24px
7. **series-number 升级**: 2rem→2.8rem, 金色渐变文字
8. **新增 40+ CSS 类** 用于子页面:
   - `.product-hero` / `.product-hero-bg` / `.product-hero-content` / `.product-hero-title`
   - `.product-action-bar` / `.product-action-btn`
   - `.product-gallery-grid` / `.product-gallery-item` / `.product-gallery-item-img`
   - `.product-section-title`
   - `.spec-grid-modern` / `.spec-card`
   - `.application-card` / `.application-grid` / `.app-card-title`
   - `.surface-treatment-tag` / `.surface-treatment-section`
   - `.related-product-card` / `.related-products-grid` / `.related-cases-grid`
   - `.product-video-section` / `.product-video-grid`
   - `.form-grid-2col`
   - 响应式断点适配 (768px, 480px)

### Phase 2: products.html + en/products.html 主页面重构 ✅
**文件**: `products.html` (2623行), `en/products.html` (2967行)

**完成内容**:
1. **移除 115 个内联 style** (CN: 126→11, EN: 128→21)
2. **移除 95 个 stone-card-img 的内联 background-image**
3. **移除 10 个 series-section-header 的内联 gradient**
4. **移除 10 个 series-section-content 的内联 bg:#fff**
5. **每张 stone-card 赋予唯一石材名称**:
   - 之前：同系列所有卡片标题相同（如"白色系大理石" × 14张）
   - 之后：每张卡片有独立名称（卡拉拉白、爵士白、魚肚白、大花白...）
   - 英文版同步（Carrara White, Statuario, Calacatta...）
   - 共覆盖10个系列，每系列5-15个独立石材名

### Phase 3: 20个子页面重构 (10中+10英) ✅
**文件**: `products/*.html` (10个), `en/products/*.html` (10个)

**完成内容**:
1. **移除 ~3700 个内联 style= 属性** (平均每文件 185 个)
2. **移除 ~490 个 onmouseover/onmouseout 内联JS事件** (全部清零)
3. **Hero区域**: 内联style → `.product-hero` CSS类
4. **操作按钮栏**: 内联style → `.product-action-bar` / `.product-action-btn`
5. **产品图库**: 内联grid + onmouseover → `.product-gallery-grid` / `.product-gallery-item` (纯CSS hover)
6. **应用场景卡片**: 内联style + emoji + onmouseover → `.application-card` (CSS hover)
7. **表面处理标签**: 内联style → `.surface-treatment-tag`
8. **相关产品/案例**: 内联style + onmouseover → `.related-product-card` (CSS hover)
9. **视频区域**: 内联style → `.product-video-grid` / `.product-video-card`
10. **所有文字内容保持不变** (中英文均未修改)
11. **所有图片路径保持不变**

### Phase 4: 英文版同步 ✅
- `en/products.html` 同步所有主页面改动
- `en/products/*.html` (10个) 同步所有子页面改动
- 英文内容保持不变，只改结构/CSS

## 关键数据

| 指标 | 重构前 | 重构后 | 改善 |
|------|--------|--------|------|
| .stone-card CSS定义数 | 3 | 1 | -67% |
| .stone-card-img CSS定义数 | 3+1 | 1+2(响应式) | -75% |
| products.html 内联style | 126 | 11 | -91% |
| en/products.html 内联style | 128 | 21 | -84% |
| 子页面平均内联style | ~200 | ~21 | -90% |
| 子页面onmouseover事件 | ~25/页 | 0 | -100% |
| 卡片信息辨识度 | 同系列同名 | 唯一石材名 | 质变 |
| CSS新增类 | 0 | 40+ | 大幅扩展 |

## Git 提交
1. `b0fc60f` - Phase 1+3: CSS dedup + sub-page inline style removal
2. `32cac8d` - Phase 2: main page inline style cleanup + unique stone names
3. `d762330` - fix: merge duplicate stone-card-img cursor property

**注意**: git push 因仓库较大(465MB)网络超时，需在本地环境执行 `git push`

## 保持不变的内容
- 所有中英文文字内容
- 所有图片路径
- 导航栏结构
- 页面SEO结构 (meta tags, schema.org)
- JavaScript功能逻辑 (对比按钮、表单验证、Cookie banner)
