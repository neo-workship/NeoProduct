self.chat_messages_container (最顶层容器)
└── ai_message_container (单条 AI 消息容器)
└── chat_content_container (消息内容容器)
├── think_expansion (思考过程展开组件，可选)
│ └── think_label (思考内容标签)
└── reply_label (AI 回复内容，markdown 组件)

self.welcome_message_container (欢迎消息容器，与 chat_messages_container 平级)


------------------------------ 查询优化
对 \services\mongodb_service\main.py 中 /api/v1/enterprises/execute_mongo_cmd 添加对 $group 聚合操作的支持，要按以下步骤处理：

1 \services\mongodb_service\main.py 中_parse_query_type函数，在aggregate判断中，通过关键字识别是否有$group操作，则返回group，否则还是返回aggregate
2 在_parse_query_parameters_with_json5中添加对query_type==group的处理逻辑

累加器操作符
    数值统计类
        $sum - 求和
        $avg - 平均值
        $min - 最小值
        $max - 最大值
        $stdDevPop - 总体标准差
        $stdDevSamp - 样本标准差
    计数类
        $count - 计数（在 $group 中通常用 $sum: 1）
    数组操作类
        $push - 收集所有值到数组
        $addToSet - 收集唯一值到数组
        $first - 获取分组中第一个值
        $last - 获取分组中最后一个值

3 在_classify_query_result_new_format 中添加对query_type==group的处理逻辑

1. 按单个字段分组
javascript// 查询：db.collection.aggregate([{$group: {_id: "$department", count: {$sum: 1}}}])
[
  { "_id": "技术部", "count": 45 },
  { "_id": "销售部", "count": 30 },
  { "_id": "人事部", "count": 12 }
]
2. 按多个字段分组
javascript// 查询：db.collection.aggregate([{$group: {_id: {dept: "$department", city: "$city"}, count: {$sum: 1}}}])
[
  { "_id": { "dept": "技术部", "city": "北京" }, "count": 20 },
  { "_id": { "dept": "技术部", "city": "上海" }, "count": 25 },
  { "_id": { "dept": "销售部", "city": "北京" }, "count": 15 }
]
