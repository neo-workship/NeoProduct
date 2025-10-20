self.chat_messages_container (最顶层容器)
└── ai_message_container (单条 AI 消息容器)
└── chat_content_container (消息内容容器)
├── think_expansion (思考过程展开组件，可选)
│ └── think_label (思考内容标签)
└── reply_label (AI 回复内容，markdown 组件)

self.welcome_message_container (欢迎消息容器，与 chat_messages_container 平级)

------------------------------ 查询优化
对 \services\mongodb_service\main.py 中 /api/v1/enterprises/execute_mongo_cmd 添加对 $group 聚合操作的支持，要按以下步骤处理，按我指令进行操作，第一次你告诉我是否明白要处理的任务和目的。

1、 \services\mongodb_service\main.py 中\_parse_query_type 函数，在对.aggregate判断中，通过关键字识别是否有$group操作，如有返回 group，否则返回 aggregate。

2、 在\_parse_query_parameters_with_json5 中添加对 query_type==group 的处理逻辑，主要是进行字段规范化处理：
如发现以下数值统计，添加对应的中文别名，如：$sum -> 求和+field_name 、$avg -> 平均值+field_name、$min -> 最小值+field_name、$max -> 最大值+field_name、$stdDevPop -> 总体标准差+field_name、$stdDevSamp -> 样本标准差+field_name、$count -> 计数+field_name 等等。

3 在\_classify_query_result_new_format 中添加对 query_type==group 的处理逻辑,在\services\mongodb_service\schemas.py 中添加对应分组操作结果的数据模型。一般包括以下2种模型。
按单个字段分组
   [
      { "_id": "技术部", "count": 45 },
      { "_id": "销售部", "count": 30 },
      { "_id": "人事部", "count": 12 }
   ]
按多个字段分组
   [
      { "_id": { "dept": "技术部", "city": "北京" }, "count": 20 },
      { "_id": { "dept": "技术部", "city": "上海" }, "count": 25 },
      { "_id": { "dept": "销售部", "city": "北京" }, "count": 15 }
   ]
