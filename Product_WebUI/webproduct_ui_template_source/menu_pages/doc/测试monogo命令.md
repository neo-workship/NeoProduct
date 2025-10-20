- group card

```js
db.getCollection("一企一档").aggregate([
  { $unwind: "$fields" },
  {
    $match: {
      "fields.path_name": "基本信息.登记信息.企业资金组成情况",
      "fields.field_name": { $in: ["注册资金"] },
    },
  },
  {
    $group: {
      _id: null,
      average_value: { $avg: { $toDouble: "$fields.value" } },
      max_value: { $max: { $toDouble: "$fields.value" } },
    },
  },
  {
    $project: {
      _id: 0,
      平均值: "$average_value",
      最大值: "$max_value",
    },
  },
]);
```

- aggregate flat card

```js
db.getCollection("一企一档").aggregate([
  {
    $match: {
      enterprise_name: "福州企展控股有限公司",
    },
  },
  {
    $unwind: "$fields",
  },
  {
    $match: {
      "fields.field_name": "注册资金",
    },
  },
  {
    $project: {
      enterprise_code: 1,
      enterprise_name: 1,
      field_value: "$fields.value",
      field_name: "$fields.field_name",
    },
  },
]);
```

- aggregate full card

```js
db.getCollection("一企一档").aggregate([
  {
    $match: {
      enterprise_name: {
        $regex: "企展",
        $options: "i",
      },
      fields: {
        $elemMatch: {
          path_name: "基本信息.登记信息.企业资金组成情况",
          field_name: "注册资金",
        },
      },
    },
  },
  {
    $project: {
      _id: 1,
      enterprise_code: 1,
      enterprise_name: 1,
      fields: {
        $filter: {
          input: "$fields",
          cond: {
            $and: [
              {
                $eq: ["$$this.path_name", "基本信息.登记信息.企业资金组成情况"],
              },
              {
                $in: ["$$this.field_name", ["注册资金"]],
              },
            ],
          },
        },
      },
    },
  },
]);
```

---

- aggregate full table

```js
db.getCollection("一企一档").find({
  enterprise_name: { $regex: "企展", $options: "i" },
});
```
