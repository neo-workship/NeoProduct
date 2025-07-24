# Grid 布局

Grid 布局与 Flex 布局有一定的相似性，都可以指定容器内部多个项目的位置。但是，它们也存在重大区别。

Flex 布局是轴线布局，只能指定"项目"针对轴线的位置，可以看作是一维布局。Grid 布局则是将容器划分成"行"和"列"，产生单元格，然后指定"项目所在"的单元格，可以看作是二维布局。Grid 布局远比 Flex 布局强大。

## 一、基本概念

### 1.1、容器和项目

采用网格布局的区域，称为 **"容器"（container）**。容器内部采用网格定位的子元素，称为 **"项目"（item）**。

- 最外层的<div>元素就是容器，内层的三个<div>元素就是项目
  项目只能是容器的顶层子元素，不包含项目的子元素，比如上面代码的<p>元素就不是项目,Grid 布局只对项目生效。

```html
<div>
  <div><p>1</p></div>
  <div><p>2</p></div>
  <div><p>3</p></div>
</div>
```

### 1.2、行和列

容器里面的水平区域称为"行"（row），垂直区域称为"列"（column）。

### 1.3、单元格

行和列的交叉区域，称为"单元格"（cell）。正常情况下，n 行和 m 列会产生 n x m 个单元格。比如，3 行 3 列会产生 9 个单元格。

## 二、容器属性

Grid 布局的属性分成两类。一类定义在容器上面，称为**容器属性**；另一类定义在项目上面，称为**项目属性**。

### 2.1、display 属性

- display: grid 指定一个容器采用网格布局

```css
div {
  display: grid;
}
```

默认情况下，容器元素都是块级元素，但也可以设成行内元素。

```css
div {
  display: inline-grid;
}
```

> > 设为网格布局以后，容器子元素（项目）的 float、display: inline-block、display: table-cell、vertical-align 和 column-\*等设置都将失效。

### 2.2、grid-template-columns、grid-template-rows 属性

- 容器指定了网格布局以后，接着就要划分行和列。

**grid-template-columns** 属性定义每一列的列宽
**grid-template-rows** 属性定义每一行的行高

```
.container {
  display: grid;
  grid-template-columns: 100px 100px 100px;
  grid-template-rows: 100px 100px 100px;
}
```

- 除了使用绝对单位，也可以使用百分比

```css
.container {
  display: grid;
  grid-template-columns: 33.33% 33.33% 33.33%;
  grid-template-rows: 33.33% 33.33% 33.33%;
}
```

- （1）repeat() 简化重复的值

重复写同样的值非常麻烦，尤其网格很多时。这时，可以使用 repeat()函数，简化重复的值。repeat()接受两个参数，第一个参数是重复的次数（上例是 3），第二个参数是所要重复的值

```css
.container {
  display: grid;
  grid-template-columns: repeat(3, 33.33%);
  grid-template-rows: repeat(3, 33.33%);
}
```

repeat()重复某种模式也是可以的

```css
grid-template-columns: repeat(2, 100px 20px 80px);
```

- （2）auto-fill 关键字

有时，单元格的大小是固定的，但是容器的大小不确定。如果希望每一行（或每一列）容纳尽可能多的单元格，这时可以使用 auto-fill 关键字表示自动填充。

```css
/** 表示每列宽度100px，然后自动填充，直到容器不能放置更多的列 */
.container {
  display: grid;
  grid-template-columns: repeat(auto-fill, 100px);
}
```

- （3）fr 关键字

为了方便表示比例关系，网格布局提供了 fr 关键字（fraction 的缩写，意为"片段"）。如果两列的宽度分别为 1fr 和 2fr，就表示后者是前者的两倍。

```css
.container {
  display: grid;
  grid-template-columns: 1fr 1fr;
}
```

fr 可以与绝对长度的单位结合使用，这时会非常方便

```css
.container {
  display: grid;
  grid-template-columns: 150px 1fr 2fr;
}
```

- （4）minmax()

minmax()函数产生一个长度范围，表示长度就在这个范围之中。它接受两个参数，分别为最小值和最大值

```css
grid-template-columns: 1fr 1fr minmax(100px, 1fr);
```

- （5）auto 关键字
  auto 关键字表示由浏览器自己决定长度

```css
grid-template-columns: 100px auto 100px;
```

- （6）网格线的名称
  grid-template-columns 属性和 grid-template-rows 属性里面，还可以使用方括号，指定每一根网格线的名字，方便以后的引用。

```css
.container {
  display: grid;
  grid-template-columns: [c1] 100px [c2] 100px [c3] auto [c4];
  grid-template-rows: [r1] 100px [r2] 100px [r3] auto [r4];
}
```

- （7）布局实例
  grid-template-columns 属性对于网页布局非常有用。两栏式布局只需要一行代码。

```css
/** 将左边栏设为70%，右边栏设为30% */
.wrapper {
  display: grid;
  grid-template-columns: 70% 30%;
}
```

### 2.3、grid-row-gap 属性、grid-column-gap 属性、grid-gap 属性

grid-row-gap 属性设置行与行的间隔（行间距），grid-column-gap 属性设置列与列的间隔（列间距）

```css
.container {
  grid-row-gap: 20px;
  grid-column-gap: 20px;
}
```

grid-gap 属性是 grid-column-gap 和 grid-row-gap 的合并简写形式，语法如下.如果 grid-gap 省略了第二个值，浏览器认为第二个值等于第一个值

```css
grid-gap: <grid-row-gap> <grid-column-gap>;
```

### 2.4、grid-template-areas 属性

网格布局允许指定"区域"（area），一个区域由单个或多个单元格组成。grid-template-areas 属性用于定义区域

```css
/** 先划分出9个单元格，然后将其定名为a到i的九个区域，分别对应这九个单元格 */
.container {
  display: grid;
  grid-template-columns: 100px 100px 100px;
  grid-template-rows: 100px 100px 100px;
  grid-template-areas:
    "a b c"
    "d e f"
    "g h i";
}
```

### 2.5、grid-auto-flow 属性

划分网格以后，容器的子元素会按照顺序，自动放置在每一个网格。默认的放置顺序是"先行后列"，即先填满第一行，再开始放入第二行。
这个顺序由 grid-auto-flow 属性决定，默认值是 row，即"先行后列"。也可以将它设成 column，变成"先列后行"。

### 2.6、justify-items 属性、align-items 属性、place-items 属性

justify-items 属性设置单元格内容的水平位置（左中右），align-items 属性设置单元格内容的垂直位置（上中下）

```css
.container {
  justify-items: start | end | center | stretch;
  align-items: start | end | center | stretch;
}
```

这两个属性的写法完全相同，都可以取下面这些值

```
start：对齐单元格的起始边缘。
end：对齐单元格的结束边缘。
center：单元格内部居中。
stretch：拉伸，占满单元格的整个宽度（默认值）
```

place-items 属性是 align-items 属性和 justify-items 属性的合并简写形式

```css
place-items: <align-items> <justify-items>;
```

### 2.7、justify-content 属性、align-content 属性、place-content 属性

justify-content 属性是整个内容区域在容器里面的水平位置（左中右），align-content 属性是整个内容区域的垂直位置（上中下）。

```css
.container {
  justify-content: start | end | center | stretch | space-around | space-between
    | space-evenly;
  align-content: start | end | center | stretch | space-around | space-between |
    space-evenly;
}
```

place-content 属性是 align-content 属性和 justify-content 属性的合并简写形式

```css
place-content: <align-content> <justify-content>;
```

### grid-auto-columns 属性、grid-auto-rows 属性

有时候，一些项目的指定位置，在现有网格的外部。比如网格只有 3 列，但是某一个项目指定在第 5 行。这时，浏览器会自动生成多余的网格，以便放置项目.

grid-auto-columns 属性和 grid-auto-rows 属性用来设置，浏览器自动创建的多余网格的列宽和行高。它们的写法与 grid-template-columns 和 grid-template-rows 完全相同。如果不指定这两个属性，浏览器完全根据单元格内容的大小，决定新增网格的列宽和行高。

### grid-template 属性、grid 属性

grid-template 属性是 grid-template-columns、grid-template-rows 和 grid-template-areas 这三个属性的合并简写形式。
grid 属性是 grid-template-rows、grid-template-columns、grid-template-areas、 grid-auto-rows、grid-auto-columns、grid-auto-flow 这六个属性的合并简写形式。

## 三、项目属性

这些属性定义在项目上面

### 3.1、grid-column-start 属性、grid-column-end 属性、grid-row-start 属性、grid-row-end 属性

项目的位置是可以指定的，具体方法就是指定项目的四个边框，分别定位在哪根网格线

- grid-column-start 属性：左边框所在的垂直网格线
- grid-column-end 属性：右边框所在的垂直网格线
- grid-row-start 属性：上边框所在的水平网格线
- grid-row-end 属性：下边框所在的水平网格线

```css
/** 1号项目的左边框是第二根垂直网格线，右边框是第四根垂直网格线 */
.item-1 {
  grid-column-start: 2;
  grid-column-end: 4;
}
```

### 3.2、grid-column 属性、grid-row 属性

grid-column 属性是 grid-column-start 和 grid-column-end 的合并简写形式，grid-row 属性是 grid-row-start 属性和 grid-row-end 的合并简写形式。

```css
.item {
  grid-column: <start-line> / <end-line>;
  grid-row: <start-line> / <end-line>;
}

.item-1 {
  grid-column: 1 / 3;
  grid-row: 1 / 2;
}
/* 等同于 */
.item-1 {
  grid-column-start: 1;
  grid-column-end: 3;
  grid-row-start: 1;
  grid-row-end: 2;
}
```

### 3.3、grid-area 属性

grid-area 属性指定项目放在哪一个区域。

```css
.item-1 {
  grid-area: e;
}
```

### 3.4、justify-self 属性、align-self 属性、place-self 属性

justify-self 属性设置单元格内容的水平位置（左中右），跟 justify-items 属性的用法完全一致，但只作用于单个项目。
align-self 属性设置单元格内容的垂直位置（上中下），跟 align-items 属性的用法完全一致，也是只作用于单个项目。

```css
.item {
  justify-self: start | end | center | stretch;
  align-self: start | end | center | stretch;
}
```
