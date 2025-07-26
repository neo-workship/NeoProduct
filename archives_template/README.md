# 企业档案扁平化数据模型设计文档

## 文档概述

**项目名称**：企业档案管理系统  
**文档版本**：v1.0  
**创建时间**：2025 年 7 月 26 日  
**文档作者**：系统架构师  
**适用范围**：企业档案数据存储、查询、分析系统

## 1. 设计背景

### 1.1 业务需求

- 管理企业的 1500+个档案字段
- 支持四级层级结构：一级分类 → 二级分类 → 三级分类 → 具体字段
- 需要高效的字段级 CRUD 操作
- 支持跨企业数据统计分析
- 前端需要灵活的层级展示和四级联动选择

### 1.2 传统嵌套模型的问题

- **性能瓶颈**：深度嵌套导致查询效率低下
- **更新困难**：修改单个字段需要更新整个企业文档
- **索引限制**：嵌套数组难以建立有效索引
- **内存开销**：单个企业文档过大（MB 级别）
- **扩展性差**：新增字段需要修改现有数据结构

### 1.3 设计目标

- 🎯 **高性能**：字段级操作达到毫秒级响应
- 🎯 **可扩展**：轻松添加新字段、新分类、新企业
- 🎯 **易查询**：支持复杂的统计分析和模糊查询
- 🎯 **前端友好**：便于实现四级联动和树形展示
- 🎯 **数据一致性**：保证数据完整性和关联关系

## 2. 扁平化设计核心思想

### 2.1 设计原则

**"一个字段 = 一个文档"**

将传统的嵌套结构完全扁平化：

```
传统模型：1个企业 = 1个复杂嵌套文档（包含1500个字段）
扁平化模型：1个企业 = 1500个独立字段文档（松散关联）
```

### 2.2 关联方式

通过以下字段维护逻辑关联关系：

- `enterprise_code`：企业维度关联
- `l1_code`, `l2_code`, `l3_code`：层级维度关联
- `path_code`, `path_name`：路径维度关联
- 排序字段：`l1_order`, `l2_order`, `l3_order`, `field_order`

## 3. 数据模型设计

### 3.1 文档结构

```json
{
  "_id": "ObjectId",

  // === 企业维度 ===
  "enterprise_code": "E001", // 企业代码（主要查询维度）
  "enterprise_name": "示例科技有限公司", // 企业名称

  // === 层级维度 ===
  "l1_code": "L1A1B2C3", // 一级分类编码
  "l1_name": "基本信息", // 一级分类名称
  "l2_code": "L2D4E5F6", // 二级分类编码
  "l2_name": "登记信息", // 二级分类名称
  "l3_code": "L3G7H8I9", // 三级分类编码
  "l3_name": "企业基本信息", // 三级分类名称

  // === 路径维度 ===
  "path_code": "L1A1B2C3.L2D4E5F6.L3G7H8I9", // 编码路径
  "path_name": "基本信息.登记信息.企业基本信息", // 名称路径
  "full_path_code": "L1A1B2C3.L2D4E5F6.L3G7H8I9.FJ1K2L3", // 完整编码路径
  "full_path_name": "基本信息.登记信息.企业基本信息.统一社会信用代码", // 完整名称路径

  // === 字段维度 ===
  "field_code": "FJ1K2L3", // 字段编码
  "field_name": "统一社会信用代码", // 字段名称
  "field_type": "string", // 字段类型

  // === 数据维度 ===
  "value": "91110000123456789X", // 字段值
  "value_text": "91110000123456789X", // 文本值（用于全文检索）

  // === 元数据维度 ===
  "remark": "必填项", // 备注说明
  "data_url": "http://api.example.com", // 数据源URL
  "is_required": true, // 是否必填
  "data_source": "工商局", // 数据来源

  // === 排序维度 ===
  "l1_order": 1, // 一级分类排序
  "l2_order": 1, // 二级分类排序
  "l3_order": 1, // 三级分类排序
  "field_order": 1, // 字段排序

  // === 时间维度 ===
  "create_time": "2025-07-26T10:30:00Z", // 创建时间
  "update_time": "2025-07-26T10:30:00Z", // 更新时间

  // === 状态维度 ===
  "status": "active" // 数据状态：active/inactive/draft
}
```

### 3.2 字段类型定义

| 字段类型  | 说明     | 示例字段           |
| --------- | -------- | ------------------ |
| `string`  | 文本类型 | 企业名称、地址     |
| `number`  | 数值类型 | 注册资金、员工数量 |
| `date`    | 日期类型 | 成立日期、登记日期 |
| `boolean` | 布尔类型 | 是否上市、是否国企 |
| `email`   | 邮箱类型 | 联系邮箱           |
| `phone`   | 电话类型 | 联系电话、传真     |
| `url`     | 链接类型 | 企业网站           |

### 3.3 编码规则

#### 3.3.1 层级编码

- **一级分类编码**：`L1` + 6 位哈希码，如 `L1A1B2C3`
- **二级分类编码**：`L2` + 6 位哈希码，如 `L2D4E5F6`
- **三级分类编码**：`L3` + 6 位哈希码，如 `L3G7H8I9`
- **字段编码**：`F` + 6 位哈希码，如 `FJ1K2L3`

#### 3.3.2 哈希算法

使用 MD5 哈希确保编码的唯一性和一致性：

```python
def generate_code(name: str, level: str, parent_code: str = "") -> str:
    hash_input = f"{parent_code}_{name}" if parent_code else name
    hash_code = hashlib.md5(hash_input.encode('utf-8')).hexdigest()[:6].upper()
    return f"{level_prefix}{hash_code}"
```

## 4. 索引设计

### 4.1 主要索引

```javascript
// 1. 企业主索引 - 最常用查询
db.enterprise_fields.createIndex(
  {
    enterprise_code: 1,
    l1_code: 1,
    l2_code: 1,
    l3_code: 1,
    field_order: 1,
  },
  { name: "idx_enterprise_hierarchy" }
);

// 2. 路径查询索引
db.enterprise_fields.createIndex(
  {
    enterprise_code: 1,
    path_code: 1,
  },
  { name: "idx_enterprise_path" }
);

// 3. 字段查询索引
db.enterprise_fields.createIndex(
  {
    enterprise_code: 1,
    field_name: 1,
  },
  { name: "idx_enterprise_field" }
);

// 4. 全文搜索索引
db.enterprise_fields.createIndex(
  {
    field_name: "text",
    value_text: "text",
    remark: "text",
  },
  {
    name: "idx_fulltext_search",
    weights: {
      field_name: 10,
      value_text: 5,
      remark: 1,
    },
  }
);

// 5. 分类统计索引
db.enterprise_fields.createIndex(
  {
    l1_code: 1,
    l2_code: 1,
    l3_code: 1,
  },
  { name: "idx_category_stats" }
);

// 6. 唯一性约束索引
db.enterprise_fields.createIndex(
  {
    enterprise_code: 1,
    field_code: 1,
  },
  { name: "idx_unique_enterprise_field", unique: true }
);
```

### 4.2 分片策略（大规模部署）

```javascript
// 按企业代码进行分片，支持水平扩展
sh.shardCollection("enterprise_db.enterprise_fields", {
  enterprise_code: 1,
  l1_code: 1,
});
```

## 5. 核心查询模式

### 5.1 单企业完整数据查询

```javascript
// 获取企业的层级结构数据（用于前端树形展示）
db.enterprise_fields.aggregate([
  { $match: { enterprise_code: "E001", status: "active" } },
  { $sort: { l1_order: 1, l2_order: 1, l3_order: 1, field_order: 1 } },

  // 按三级分类分组
  {
    $group: {
      _id: {
        l1_code: "$l1_code",
        l1_name: "$l1_name",
        l2_code: "$l2_code",
        l2_name: "$l2_name",
        l3_code: "$l3_code",
        l3_name: "$l3_name",
      },
      fields: {
        $push: {
          field_code: "$field_code",
          field_name: "$field_name",
          value: "$value",
          is_required: "$is_required",
        },
      },
    },
  },

  // 按二级分类分组
  {
    $group: {
      _id: {
        l1_code: "$_id.l1_code",
        l1_name: "$_id.l1_name",
        l2_code: "$_id.l2_code",
        l2_name: "$_id.l2_name",
      },
      level3_categories: {
        $push: {
          l3_code: "$_id.l3_code",
          l3_name: "$_id.l3_name",
          fields: "$fields",
        },
      },
    },
  },

  // 按一级分类分组
  {
    $group: {
      _id: { l1_code: "$_id.l1_code", l1_name: "$_id.l1_name" },
      level2_categories: {
        $push: {
          l2_code: "$_id.l2_code",
          l2_name: "$_id.l2_name",
          level3_categories: "$level3_categories",
        },
      },
    },
  },
]);
```

### 5.2 字段级查询

```javascript
// 精确查询特定字段
db.enterprise_fields.findOne({
  enterprise_code: "E001",
  field_name: "统一社会信用代码",
});

// 模糊查询字段
db.enterprise_fields
  .find({
    enterprise_code: "E001",
    $text: { $search: "统一 信用" },
  })
  .hint("idx_fulltext_search");

// 按分类查询字段
db.enterprise_fields
  .find({
    enterprise_code: "E001",
    l1_name: "基本信息",
    l2_name: "登记信息",
  })
  .sort({ l3_order: 1, field_order: 1 });
```

### 5.3 跨企业统计分析

```javascript
// 注册资金统计分析
db.enterprise_fields.aggregate([
  {
    $match: {
      field_name: "注册资金",
      value: { $ne: "", $ne: null },
    },
  },

  // 数据类型转换
  {
    $addFields: {
      numeric_value: {
        $toDouble: {
          $replaceAll: { input: "$value", find: "万元", replacement: "" },
        },
      },
    },
  },

  // 统计计算
  {
    $group: {
      _id: null,
      总企业数: { $sum: 1 },
      平均注册资金: { $avg: "$numeric_value" },
      最大注册资金: { $max: "$numeric_value" },
      最小注册资金: { $min: "$numeric_value" },
      标准差: { $stdDevPop: "$numeric_value" },
    },
  },
]);

// 按地区统计企业分布
db.enterprise_fields.aggregate([
  { $match: { field_name: { $in: ["注册资金", "企业地址"] } } },

  // 重组企业数据
  {
    $group: {
      _id: "$enterprise_code",
      enterprise_name: { $first: "$enterprise_name" },
      fields: { $push: { field_name: "$field_name", value: "$value" } },
    },
  },

  // 提取地区和资金信息
  {
    $addFields: {
      地区: {
        $substr: [
          {
            $arrayElemAt: [
              {
                $map: {
                  input: {
                    $filter: {
                      input: "$fields",
                      cond: { $eq: ["$$this.field_name", "企业地址"] },
                    },
                  },
                  as: "item",
                  in: "$$item.value",
                },
              },
              0,
            ],
          },
          0,
          2,
        ],
      },
      注册资金: {
        $toDouble: {
          $replaceAll: {
            input: {
              $arrayElemAt: [
                {
                  $map: {
                    input: {
                      $filter: {
                        input: "$fields",
                        cond: { $eq: ["$$this.field_name", "注册资金"] },
                      },
                    },
                    as: "item",
                    in: "$$item.value",
                  },
                },
                0,
              ],
            },
            find: "万元",
            replacement: "",
          },
        },
      },
    },
  },

  // 按地区分组统计
  {
    $group: {
      _id: "$地区",
      企业数量: { $sum: 1 },
      平均注册资金: { $avg: "$注册资金" },
      资金总和: { $sum: "$注册资金" },
    },
  },

  { $sort: { 资金总和: -1 } },
]);
```

### 5.4 四级联动查询

```javascript
// 获取一级分类列表
db.enterprise_fields.distinct("l1_name", { status: "active" });

// 根据一级分类获取二级分类
db.enterprise_fields
  .find(
    {
      l1_code: "L1A1B2C3",
      status: "active",
    },
    { l2_code: 1, l2_name: 1, l2_order: 1 }
  )
  .sort({ l2_order: 1 });

// 根据前两级获取三级分类
db.enterprise_fields
  .find(
    {
      l1_code: "L1A1B2C3",
      l2_code: "L2D4E5F6",
      status: "active",
    },
    { l3_code: 1, l3_name: 1, l3_order: 1 }
  )
  .sort({ l3_order: 1 });

// 根据前三级获取字段列表
db.enterprise_fields
  .find(
    {
      l1_code: "L1A1B2C3",
      l2_code: "L2D4E5F6",
      l3_code: "L3G7H8I9",
      status: "active",
    },
    { field_code: 1, field_name: 1, field_order: 1 }
  )
  .sort({ field_order: 1 });
```

## 6. CRUD 操作

### 6.1 创建操作

#### 6.1.1 添加新字段到单个企业

```javascript
// 为企业E001添加新字段"企业简称"
const newField = {
  enterprise_code: "E001",
  enterprise_name: "示例科技有限公司",
  l1_code: "L1A1B2C3",
  l1_name: "基本信息",
  l2_code: "L2D4E5F6",
  l2_name: "登记信息",
  l3_code: "L3G7H8I9",
  l3_name: "企业基本信息",
  field_code: "F_SHORT_NAME",
  field_name: "企业简称",
  field_type: "string",
  value: "示例科技",
  is_required: false,
  create_time: new Date(),
  update_time: new Date(),
  status: "active",
};

db.enterprise_fields.insertOne(newField);
```

#### 6.1.2 为所有企业批量添加字段

```javascript
// 获取所有企业代码
const enterprises = db.enterprise_fields.distinct("enterprise_code");

// 批量生成文档
const bulkOps = enterprises.map((code) => ({
  insertOne: {
    document: {
      enterprise_code: code,
      // ... 其他字段信息
      field_name: "新字段名",
      value: "",
      create_time: new Date(),
    },
  },
}));

db.enterprise_fields.bulkWrite(bulkOps);
```

### 6.2 读取操作

```javascript
// 读取企业的特定字段值
db.enterprise_fields.findOne(
  {
    enterprise_code: "E001",
    field_name: "统一社会信用代码",
  },
  { value: 1 }
);

// 读取企业的某个分类下所有字段
db.enterprise_fields
  .find({
    enterprise_code: "E001",
    l3_code: "L3G7H8I9",
  })
  .sort({ field_order: 1 });
```

### 6.3 更新操作

```javascript
// 更新单个字段值
db.enterprise_fields.updateOne(
  {
    enterprise_code: "E001",
    field_name: "注册资金",
  },
  {
    $set: {
      value: "2000万元",
      update_time: new Date(),
    },
  }
);

// 批量更新某类字段
db.enterprise_fields.updateMany(
  {
    enterprise_code: "E001",
    l1_name: "基本信息",
    value: "",
  },
  {
    $set: {
      status: "incomplete",
      update_time: new Date(),
    },
  }
);
```

### 6.4 删除操作

```javascript
// 删除特定字段（软删除）
db.enterprise_fields.updateOne(
  {
    enterprise_code: "E001",
    field_code: "F_TEMP_FIELD",
  },
  {
    $set: {
      status: "inactive",
      update_time: new Date(),
    },
  }
);

// 物理删除（谨慎使用）
db.enterprise_fields.deleteOne({
  enterprise_code: "E001",
  field_code: "F_TEMP_FIELD",
});
```

## 7. 性能优化

### 7.1 查询性能

| 操作类型   | 传统嵌套模型        | 扁平化模型          | 性能提升     |
| ---------- | ------------------- | ------------------- | ------------ |
| 单字段查询 | 需要扫描整个文档    | 直接索引定位        | 100-1000 倍  |
| 字段更新   | 更新整个文档(MB 级) | 更新单个文档(KB 级) | 1000-2000 倍 |
| 跨企业统计 | 内存解析嵌套结构    | 直接聚合计算        | 10-100 倍    |
| 模糊搜索   | 全文档扫描          | 全文索引            | 50-500 倍    |

### 7.2 存储空间

```
单个字段文档大小：约500-800字节
单企业存储（1500字段）：1500 × 600字节 ≈ 900KB
1000个企业总存储：约900MB
包含索引总存储：约1.5-2GB

相比嵌套模型节省：60-70%存储空间
```

### 7.3 并发性能

**写操作并发**：

- 不同字段可以完全并行更新
- 避免文档级锁竞争
- 支持高并发写入场景

**读操作并发**：

- 字段级缓存策略
- 减少锁等待时间
- 提升整体吞吐量

## 8. 扩展性设计

### 8.1 水平扩展

**分片策略**：

```javascript
// 按企业代码分片
sh.shardCollection("enterprise_db.enterprise_fields", {
  enterprise_code: 1,
});

// 支持企业维度的水平扩展
// 新增企业自动分布到不同分片
```

**容量规划**：

```
小规模：1,000企业 × 1,500字段 = 150万文档
中规模：10,000企业 × 1,500字段 = 1,500万文档
大规模：100,000企业 × 1,500字段 = 1.5亿文档

MongoDB单集合理论上限：约160亿文档
```

### 8.2 功能扩展

**新增字段类型**：

```javascript
// 轻松添加新的字段类型
"field_type": "json",     // JSON对象类型
"field_type": "file",     // 文件类型
"field_type": "enum",     // 枚举类型
"field_type": "array"     // 数组类型
```

**新增元数据**：

```javascript
// 可以随时添加新的元数据字段
"validation_rule": "regex:^[0-9]{18}$",  // 验证规则
"display_format": "currency",             // 显示格式
"auto_fill": true,                       // 自动填充
"computed_field": "field1 + field2"      // 计算字段
```

### 8.3 版本管理

**字段版本控制**：

```javascript
{
  // 基础字段信息
  "field_code": "F_REG_CAPITAL",
  "field_name": "注册资金",

  // 版本控制
  "version": 2,
  "version_history": [
    {
      "version": 1,
      "field_name": "注册资本",
      "change_time": "2025-01-01T00:00:00Z",
      "change_reason": "字段名称规范化"
    }
  ]
}
```

## 9. 数据一致性保障

### 9.1 事务支持

```javascript
// 使用MongoDB事务确保多字段操作的一致性
const session = client.startSession();

try {
  await session.withTransaction(async () => {
    // 同时更新企业的多个相关字段
    await db.enterprise_fields.updateMany(
      {
        enterprise_code: "E001",
        l1_name: "基本信息",
      },
      {
        $set: { update_time: new Date() },
      },
      { session }
    );

    await db.enterprise_fields.insertOne(
      {
        enterprise_code: "E001",
        field_name: "新字段",
        // ... 其他字段
      },
      { session }
    );
  });
} finally {
  await session.endSession();
}
```

### 9.2 数据校验

**应用层校验**：

```javascript
// 确保企业字段完整性
async function validateEnterpriseFields(enterpriseCode) {
  const fieldCount = await db.enterprise_fields.countDocuments({
    enterprise_code: enterpriseCode,
    status: "active",
  });

  const expectedFieldCount = 1500; // 期望的字段总数

  if (fieldCount !== expectedFieldCount) {
    console.warn(
      `企业 ${enterpriseCode} 字段不完整：${fieldCount}/${expectedFieldCount}`
    );
    // 执行数据修复逻辑
    await repairEnterpriseFields(enterpriseCode);
  }
}
```

**数据库层校验**：

```javascript
// 字段值类型校验
db.enterprise_fields.createIndex(
  { enterprise_code: 1, field_code: 1 },
  {
    unique: true,
    partialFilterExpression: { status: "active" },
  }
);
```

## 10. 监控和维护

### 10.1 性能监控指标

**查询性能指标**：

- 平均查询响应时间
- 索引命中率
- 慢查询分析
- 并发连接数

**存储指标**：

- 文档总数
- 索引大小
- 存储空间使用率
- 分片均衡度

### 10.2 日常维护

**索引维护**：

```javascript
// 定期重建索引
db.enterprise_fields.reIndex();

// 分析索引使用情况
db.enterprise_fields.aggregate([{ $indexStats: {} }]);
```

**数据清理**：

```javascript
// 清理无效状态的数据
db.enterprise_fields.deleteMany({
  status: "inactive",
  update_time: { $lt: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000) }, // 90天前
});
```

## 11. 前端集成指南

### 11.1 API 设计建议

**RESTful API 设计**：

```javascript
// 获取企业字段层级结构
GET /api/enterprises/{code}/fields/hierarchy

// 获取特定分类下的字段
GET /api/enterprises/{code}/fields?l1={l1}&l2={l2}&l3={l3}

// 更新单个字段
PUT /api/enterprises/{code}/fields/{fieldCode}

// 批量更新字段
PATCH /api/enterprises/{code}/fields

// 四级联动API
GET /api/categories/level1
GET /api/categories/level2?l1={l1_code}
GET /api/categories/level3?l1={l1_code}&l2={l2_code}
GET /api/fields?l1={l1_code}&l2={l2_code}&l3={l3_code}
```

### 11.2 前端缓存策略

**分级缓存**：

```javascript
// 一级分类缓存（变化频率低）
cache.set("level1_categories", data, 3600); // 1小时

// 二级分类缓存
cache.set(`level2_${l1_code}`, data, 1800); // 30分钟

// 字段数据缓存（变化频率高）
cache.set(`enterprise_${code}_fields`, data, 300); // 5分钟
```

### 11.3 组件设计建议

**四级联动组件**：

```jsx
<CascadeFieldSelector
  enterprise={enterpriseCode}
  levels={["l1", "l2", "l3", "field"]}
  onChange={handleFieldSelect}
  showFieldCount={true}
  enableSearch={true}
/>
```

**树形展示组件**：

```jsx
<EnterpriseFieldTree
  enterprise={enterpriseCode}
  onFieldEdit={handleFieldEdit}
  showProgress={true}
  groupBy="category"
/>
```

## 12. 安全考虑

### 12.1 数据权限

**字段级权限控制**：

```javascript
// 用户只能访问授权的字段
const authorizedFields = await db.enterprise_fields.find({
  enterprise_code: enterpriseCode,
  field_code: { $in: userPermissions.allowedFields },
  l1_code: { $in: userPermissions.allowedCategories },
});
```

**敏感数据保护**：

```javascript
// 敏感字段加密存储
{
  field_name: "银行账号",
  value: "encrypted:AES256:xxxxx",
  is_sensitive: true,
  encryption_method: "AES256"
}
```

### 12.2 操作审计

**变更日志**：

```javascript
// 字段变更历史记录
{
  field_code: "F_REG_CAPITAL",
  change_log: [
    {
      user: "user123",
      action: "update",
      old_value: "1000万元",
      new_value: "2000万元",
```
