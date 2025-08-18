self.chat_messages_container (最顶层容器)
└── ai_message_container (单条 AI 消息容器)
└── chat_content_container (消息内容容器)
├── think_expansion (思考过程展开组件，可选)
│ └── think_label (思考内容标签)
└── reply_label (AI 回复内容，markdown 组件)

self.welcome_message_container (欢迎消息容器，与 chat_messages_container 平级)
