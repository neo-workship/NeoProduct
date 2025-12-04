-- ========================================================================
-- MySQL 8 中文测试数据生成脚本（修复完善版）
-- 版本: 2.0
-- 描述: 创建一个电商场景的中文测试数据库，包含用户、商品、订单等完整业务数据
-- 修复内容：
--   1. 修复数据类型错误（字符串类型的数字）
--   2. 修复JSON格式错误（中文引号）
--   3. 添加更多测试数据
--   4. 添加商品评价表
--   5. 添加购物车表
--   6. 添加优惠券表
--   7. 添加存储过程和函数
--   8. 添加触发器
-- ========================================================================

-- 设置客户端字符集
SET NAMES utf8mb4;
SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL';

-- 创建数据库
DROP DATABASE IF EXISTS `e_commerce`;
CREATE DATABASE `e_commerce` 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE `e_commerce`;

-- ========================================================================
-- 1. 用户表 (存储平台用户信息)
-- ========================================================================
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
    `user_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户ID',
    `username` VARCHAR(50) NOT NULL COMMENT '用户名',
    `real_name` VARCHAR(50) NOT NULL COMMENT '真实姓名',
    `gender` ENUM('男', '女', '未知') DEFAULT '未知' COMMENT '性别',
    `mobile` VARCHAR(20) NOT NULL UNIQUE COMMENT '手机号码',
    `email` VARCHAR(100) DEFAULT NULL COMMENT '邮箱地址',
    `id_card` VARCHAR(18) DEFAULT NULL COMMENT '身份证号码',
    `birth_date` DATE DEFAULT NULL COMMENT '出生日期',
    `province` VARCHAR(20) DEFAULT NULL COMMENT '省份',
    `city` VARCHAR(20) DEFAULT NULL COMMENT '城市',
    `address` VARCHAR(200) DEFAULT NULL COMMENT '详细地址',
    `user_level` TINYINT UNSIGNED DEFAULT 1 COMMENT '用户等级(1-普通,2-银卡,3-金卡,4-钻石)',
    `total_points` INT UNSIGNED DEFAULT 0 COMMENT '总积分',
    `available_points` INT UNSIGNED DEFAULT 0 COMMENT '可用积分',
    `register_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
    `last_login_time` DATETIME DEFAULT NULL COMMENT '最后登录时间',
    `status` ENUM('正常', '禁用', '注销') DEFAULT '正常' COMMENT '账户状态',
    PRIMARY KEY (`user_id`),
    UNIQUE KEY `uk_mobile` (`mobile`),
    KEY `idx_username` (`username`),
    KEY `idx_register_time` (`register_time`),
    KEY `idx_user_level` (`user_level`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户信息表';

-- 插入用户测试数据
INSERT INTO `users` (`username`, `real_name`, `gender`, `mobile`, `email`, `id_card`, `birth_date`, `province`, `city`, `address`, `user_level`, `total_points`, `available_points`, `register_time`, `last_login_time`, `status`) VALUES
('zhang_san', '张三', '男', '13800138001', 'zhangsan@email.com', '110101199001011234', '1990-01-01', '北京市', '朝阳区', '建国路88号SOHO现代城A座1501室', 3, 15000, 8500, '2023-01-15 10:30:00', '2024-12-01 09:15:30', '正常'),
('li_si', '李四', '女', '13900139002', 'lisi@email.com', '310101199205203456', '1992-05-20', '上海市', '浦东新区', '陆家嘴金融贸易区世纪大道100号', 2, 8000, 5200, '2023-03-20 14:20:00', '2024-11-30 16:45:12', '正常'),
('wang_wu', '王五', '男', '13700137003', 'wangwu@email.com', '440101198807152345', '1988-07-15', '广东省', '深圳市', '南山区科技园南区高新南一道6号', 4, 28000, 15600, '2022-11-10 09:00:00', '2024-12-01 11:20:45', '正常'),
('zhao_liu', '赵六', '女', '13600136004', 'zhaoliu@email.com', '510101199512308765', '1995-12-30', '四川省', '成都市', '高新区天府大道中段1388号', 1, 3500, 2100, '2024-01-08 11:30:00', '2024-11-28 10:30:20', '正常'),
('sun_qi', '孙七', '男', '13500135005', 'sunqi@email.com', '320101198603054321', '1986-03-05', '江苏省', '南京市', '玄武区中山东路18号', 2, 5000, 0, '2023-06-15 16:20:00', '2024-09-15 14:25:10', '禁用'),
('zhou_ba', '周八', '女', '13400134006', 'zhouba@email.com', '330101199112124567', '1991-12-12', '浙江省', '杭州市', '西湖区文三路478号', 3, 12000, 7800, '2023-08-22 10:15:00', '2024-11-29 15:10:30', '正常'),
('wu_jiu', '吴九', '男', '13300133007', 'wujiu@email.com', '420101197809204567', '1978-09-20', '湖北省', '武汉市', '洪山区珞喻路1037号', 4, 35000, 22000, '2022-05-18 13:45:00', '2024-12-01 08:30:15', '正常'),
('zheng_shi', '郑十', '女', '13200132008', 'zhengshi@email.com', '210101199807256789', '1998-07-25', '辽宁省', '大连市', '中山区人民路68号', 1, 1200, 800, '2024-03-12 09:25:00', '2024-11-25 17:40:22', '正常'),
('chen_yi', '陈一', '男', '13100131009', 'chenyi@email.com', '370101199002283456', '1990-02-28', '山东省', '青岛市', '市南区香港中路10号', 2, 6800, 4500, '2023-10-05 14:50:00', '2024-11-27 12:15:45', '正常'),
('liu_er', '刘二', '女', '13000130010', 'liuer@email.com', '410101199511153456', '1995-11-15', '河南省', '郑州市', '金水区花园路126号', 3, 10500, 6200, '2023-07-30 11:10:00', '2024-11-30 09:45:18', '正常'),
('huang_san', '黄三', '男', '13800138011', 'huangsan@email.com', '510101199301158765', '1993-01-15', '四川省', '成都市', '武侯区天府软件园B区7栋', 2, 4500, 3000, '2024-02-20 15:30:00', '2024-11-26 10:20:30', '正常'),
('lin_si', '林四', '女', '13900139012', 'linsi@email.com', '350101199408222345', '1994-08-22', '福建省', '福州市', '鼓楼区五一北路158号', 1, 2000, 1500, '2024-04-10 09:40:00', '2024-11-24 14:35:20', '正常'),
('xu_wu', '徐五', '男', '13700137013', 'xuwu@email.com', '430101198911305678', '1989-11-30', '湖南省', '长沙市', '岳麓区麓谷企业广场C3栋', 3, 14000, 9500, '2023-09-12 16:20:00', '2024-11-29 11:50:15', '正常'),
('he_liu', '何六', '女', '13600136014', 'heliu@email.com', '150101199605123456', '1996-05-12', '内蒙古', '呼和浩特市', '新城区成吉思汗大街1号', 2, 5500, 3800, '2024-01-25 10:30:00', '2024-11-28 16:25:40', '正常'),
('guo_qi', '郭七', '男', '13500135015', 'guoqi@email.com', '610101198710208765', '1987-10-20', '陕西省', '西安市', '雁塔区科技路38号', 4, 42000, 28000, '2022-08-15 14:15:00', '2024-12-01 10:40:25', '正常');

-- ========================================================================
-- 2. 商品分类表
-- ========================================================================
DROP TABLE IF EXISTS `product_category`;
CREATE TABLE `product_category` (
    `category_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '分类ID',
    `category_name` VARCHAR(50) NOT NULL COMMENT '分类名称',
    `parent_id` INT UNSIGNED DEFAULT 0 COMMENT '父级分类ID(0表示一级分类)',
    `level` TINYINT UNSIGNED NOT NULL COMMENT '分类级别(1-3级)',
    `sort_order` INT UNSIGNED DEFAULT 0 COMMENT '排序值',
    `is_show` TINYINT(1) DEFAULT 1 COMMENT '是否显示(0-隐藏,1-显示)',
    `icon` VARCHAR(255) DEFAULT NULL COMMENT '分类图标URL',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`category_id`),
    KEY `idx_parent_id` (`parent_id`),
    KEY `idx_level` (`level`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品分类表';

-- 插入商品分类数据
INSERT INTO `product_category` (`category_name`, `parent_id`, `level`, `sort_order`, `is_show`) VALUES
('电子产品', 0, 1, 10, 1),
('手机通讯', 1, 2, 1, 1),
('电脑整机', 1, 2, 2, 1),
('数码配件', 1, 2, 3, 1),
('家用电器', 0, 1, 20, 1),
('大家电', 5, 2, 1, 1),
('厨房小电', 5, 2, 2, 1),
('生活电器', 5, 2, 3, 1),
('服装鞋帽', 0, 1, 30, 1),
('男装', 9, 2, 1, 1),
('女装', 9, 2, 2, 1),
('运动鞋服', 9, 2, 3, 1),
('图书音像', 0, 1, 40, 1),
('教育图书', 13, 2, 1, 1),
('文学艺术', 13, 2, 2, 1),
('食品生鲜', 0, 1, 50, 1),
('休闲零食', 16, 2, 1, 1),
('茶叶酒水', 16, 2, 2, 1);

-- ========================================================================
-- 3. 商品表
-- ========================================================================
DROP TABLE IF EXISTS `products`;
CREATE TABLE `products` (
    `product_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '商品ID',
    `product_name` VARCHAR(200) NOT NULL COMMENT '商品名称',
    `category_id` INT UNSIGNED NOT NULL COMMENT '分类ID',
    `brand` VARCHAR(50) DEFAULT NULL COMMENT '品牌',
    `market_price` DECIMAL(10,2) NOT NULL COMMENT '市场价',
    `sale_price` DECIMAL(10,2) NOT NULL COMMENT '销售价',
    `stock_quantity` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '库存数量',
    `sales_volume` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '销量',
    `main_image` VARCHAR(255) DEFAULT NULL COMMENT '主图URL',
    `description` TEXT DEFAULT NULL COMMENT '商品描述',
    `specifications` JSON DEFAULT NULL COMMENT '规格参数(JSON)',
    `is_new` TINYINT(1) DEFAULT 0 COMMENT '是否新品(0-否,1-是)',
    `is_hot` TINYINT(1) DEFAULT 0 COMMENT '是否热销(0-否,1-是)',
    `is_recommended` TINYINT(1) DEFAULT 0 COMMENT '是否推荐(0-否,1-是)',
    `status` ENUM('在售', '下架', '缺货') DEFAULT '在售' COMMENT '商品状态',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`product_id`),
    KEY `idx_category_id` (`category_id`),
    KEY `idx_brand` (`brand`),
    KEY `idx_status` (`status`),
    KEY `idx_is_hot` (`is_hot`),
    KEY `idx_sale_price` (`sale_price`),
    CONSTRAINT `fk_product_category` FOREIGN KEY (`category_id`) REFERENCES `product_category` (`category_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品信息表';

-- 插入商品测试数据（修复后的数据）
INSERT INTO `products` (`product_name`, `category_id`, `brand`, `market_price`, `sale_price`, `stock_quantity`, `sales_volume`, `description`, `specifications`, `is_new`, `is_hot`, `is_recommended`, `status`) VALUES
('Apple iPhone 15 Pro Max 256GB 钛金属', 2, '苹果', 11999.00, 10999.00, 150, 320, '全新A17 Pro芯片，钛金属设计，专业级摄像系统', '{"颜色": "钛金属", "存储": "256GB", "屏幕尺寸": "6.7英寸", "5G": "支持"}', 1, 1, 1, '在售'),
('华为Mate 60 Pro 12GB+512GB 雅川青', 2, '华为', 6999.00, 6499.00, 200, 580, '卫星通话功能，超可靠玄武架构，全焦段超清影像', '{"颜色": "雅川青", "内存": "12GB", "存储": "512GB", "网络": "5G"}', 1, 1, 1, '在售'),
('小米14 Ultra 16GB+1TB 徕卡影像', 2, '小米', 6999.00, 5999.00, 80, 120, '徕卡光学Summilux镜头，骁龙8 Gen3处理器', '{"颜色": "黑色", "内存": "16GB", "存储": "1TB", "相机": "徕卡四摄"}', 1, 1, 1, '在售'),
('联想ThinkPad X1 Carbon 14英寸轻薄本', 3, '联想', 12999.00, 11999.00, 50, 89, '碳纤维机身，Intel酷睿Ultra处理器，2.8K OLED屏幕', '{"处理器": "酷睿Ultra7", "内存": "32GB", "硬盘": "1TB SSD", "屏幕": "2.8K OLED"}', 0, 0, 1, '在售'),
('华硕ROG魔霸7 Plus 17.3英寸游戏本', 3, '华硕', 8999.00, 8499.00, 30, 156, 'AMD锐龙9处理器，RTX4070显卡，2.5K 240Hz屏', '{"处理器": "锐龙9 7845HX", "显卡": "RTX4070", "内存": "16GB", "刷新率": "240Hz"}', 0, 1, 0, '在售'),
('海尔10公斤变频滚筒洗衣机', 6, '海尔', 2999.00, 2399.00, 100, 234, '直驱变频电机，智能投放洗涤剂，巴氏除菌洗', '{"容量": "10公斤", "类型": "滚筒", "电机": "直驱变频", "能效": "一级"}', 0, 1, 1, '在售'),
('美的1.5匹变频空调挂机', 6, '美的', 3299.00, 2799.00, 150, 445, '全直流变频，一级能效，WiFi智能控制', '{"匹数": "1.5匹", "能效": "一级", "类型": "壁挂式", "制冷量": "3500W"}', 0, 1, 1, '在售'),
('九阳破壁机L18-Y915S', 7, '九阳', 999.00, 599.00, 300, 1200, '1.75L大容量，八叶破壁刀，多重降噪技术', '{"容量": "1.75L", "功率": "900W", "刀片": "八叶精钢", "功能": "预约保温"}', 1, 1, 1, '在售'),
('优衣库男士纯棉T恤', 10, '优衣库', 99.00, 79.00, 500, 2300, '100%纯棉，吸汗透气，多色可选', '{"材质": "纯棉", "领型": "圆领", "袖长": "短袖", "适用季节": "春夏"}', 0, 0, 0, '在售'),
('ZARA女士连衣裙春秋款', 11, 'ZARA', 399.00, 299.00, 200, 567, '法式复古风格，高腰设计，聚酯纤维面料', '{"材质": "聚酯纤维", "版型": "A字型", "袖长": "长袖", "风格": "法式复古"}', 1, 0, 0, '在售'),
('Nike Air Max 270运动鞋', 12, '耐克', 899.00, 699.00, 150, 890, '全掌Max Air气垫，轻盈网眼鞋面，时尚配色', '{"适用性别": "男女同款", "功能": "缓震", "适用场景": "跑步/日常", "鞋面材质": "网眼"}', 0, 1, 1, '在售'),
('Adidas Ultra Boost 22跑步鞋', 12, '阿迪达斯', 1199.00, 899.00, 100, 456, 'BOOST中底科技，Primeknit鞋面，Continental马牌橡胶外底', '{"适用性别": "中性", "功能": "竞速训练", "鞋底科技": "BOOST", "鞋面科技": "Primeknit"}', 0, 1, 1, '在售'),
('《人类简史》精装版', 14, '中信出版社', 88.00, 58.00, 300, 1500, '尤瓦尔·赫拉利著作，从智人到今天的人类发展史', '{"作者": "尤瓦尔·赫拉利", "装帧": "精装", "页数": "440页", "ISBN": "978-7-5086-4735-7"}', 0, 1, 1, '在售'),
('Python编程从入门到精通', 14, '人民邮电出版社', 99.00, 69.00, 150, 678, '零基础学Python，包含大量实战案例', '{"作者": "明日科技", "版本": "第3版", "页数": "520页", "特色": "含视频教程"}', 1, 0, 1, '在售'),
('Sony WH-1000XM5降噪耳机', 4, '索尼', 2399.00, 1999.00, 80, 234, '业界领先降噪技术，30小时续航，高解析度音质', '{"降噪等级": "业界领先", "续航": "30小时", "充电": "快充3分钟听3小时", "音质": "高解析度"}', 1, 1, 1, '在售'),
('戴尔XPS 13 Plus 13.4英寸超轻薄本', 3, '戴尔', 9999.00, 8999.00, 45, 67, 'Intel 13代酷睿i7，16GB内存，512GB固态硬盘', '{"处理器": "i7-1360P", "内存": "16GB", "硬盘": "512GB SSD", "屏幕": "13.4英寸 FHD+"}', 0, 0, 0, '在售'),
('美的电磁炉C21-RT2176', 7, '美的', 299.00, 199.00, 400, 856, '触控屏设计，9档火力调节，智能防干烧', '{"功率": "2100W", "面板": "微晶面板", "档位": "9档", "安全保护": "防干烧"}', 0, 1, 0, '在售'),
('格力3匹立式空调', 6, '格力', 5999.00, 4999.00, 80, 167, '变频技术，新一级能效，大风量送风', '{"匹数": "3匹", "能效": "新一级", "类型": "立式", "适用面积": "30-45平米"}', 0, 1, 1, '在售'),
('优衣库女士羽绒服', 11, '优衣库', 799.00, 599.00, 300, 445, '90%白鸭绒，防风防水，轻盈保暖', '{"材质": "聚酯纤维+羽绒", "含绒量": "90%", "厚度": "常规", "适用季节": "冬季"}', 1, 1, 1, '在售'),
('李宁运动套装男', 12, '李宁', 499.00, 349.00, 250, 678, '速干透气面料，宽松版型，适合运动健身', '{"材质": "涤纶", "版型": "宽松", "适用场景": "运动健身", "特点": "速干透气"}', 0, 0, 0, '在售'),
('《活着》余华著', 15, '作家出版社', 35.00, 25.00, 500, 1890, '中国现代文学经典作品，讲述生命的意义', '{"作者": "余华", "装帧": "平装", "页数": "256页", "出版时间": "2012-08"}', 0, 1, 1, '在售'),
('AirPods Pro 2代', 4, '苹果', 1899.00, 1699.00, 120, 456, '主动降噪，自适应通透模式，H2芯片', '{"降噪": "主动降噪", "续航": "6小时", "充电盒": "MagSafe", "芯片": "H2"}', 1, 1, 1, '在售'),
('三只松鼠每日坚果礼盒', 17, '三只松鼠', 168.00, 128.00, 600, 2340, '30包混合坚果，营养均衡，办公室零食', '{"规格": "750g", "包装": "30小包", "保质期": "180天", "口味": "混合坚果"}', 0, 1, 1, '在售'),
('茅台飞天53度500ml', 18, '茅台', 2999.00, 2899.00, 50, 123, '国酒茅台，酱香型白酒，收藏送礼佳品', '{"香型": "酱香型", "度数": "53度", "容量": "500ml", "产地": "贵州茅台镇"}', 0, 1, 1, '在售'),
('戴森V15吸尘器', 8, '戴森', 4990.00, 4490.00, 60, 189, '激光探测微尘，强劲吸力，整屋深度清洁', '{"类型": "手持无线", "续航": "60分钟", "吸力": "240AW", "特点": "激光探测"}', 1, 1, 1, '在售'),
('小米电视65英寸4K', 6, '小米', 2999.00, 2499.00, 100, 567, '4K超高清，120Hz刷新率，HDMI2.1接口', '{"尺寸": "65英寸", "分辨率": "4K", "刷新率": "120Hz", "系统": "小米电视系统"}', 0, 1, 1, '在售');

-- ========================================================================
-- 4. 订单表
-- ========================================================================
DROP TABLE IF EXISTS `orders`;
CREATE TABLE `orders` (
    `order_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '订单ID',
    `order_no` VARCHAR(32) NOT NULL UNIQUE COMMENT '订单号',
    `user_id` BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    `order_status` ENUM('待支付', '已支付', '已发货', '已完成', '已取消', '退款中', '已退款') DEFAULT '待支付' COMMENT '订单状态',
    `pay_status` ENUM('未支付', '支付中', '已支付', '退款中', '已退款') DEFAULT '未支付' COMMENT '支付状态',
    `shipping_status` ENUM('未发货', '已发货', '已收货', '退货中', '已退货') DEFAULT '未发货' COMMENT '发货状态',
    `order_amount` DECIMAL(10,2) NOT NULL COMMENT '订单金额',
    `pay_amount` DECIMAL(10,2) NOT NULL COMMENT '实付金额',
    `freight_amount` DECIMAL(10,2) DEFAULT 0.00 COMMENT '运费金额',
    `discount_amount` DECIMAL(10,2) DEFAULT 0.00 COMMENT '优惠金额',
    `coupon_amount` DECIMAL(10,2) DEFAULT 0.00 COMMENT '优惠券金额',
    `points_amount` DECIMAL(10,2) DEFAULT 0.00 COMMENT '积分抵扣金额',
    `pay_method` ENUM('支付宝', '微信支付', '银联支付', '余额支付') DEFAULT NULL COMMENT '支付方式',
    `pay_time` DATETIME DEFAULT NULL COMMENT '支付时间',
    `ship_time` DATETIME DEFAULT NULL COMMENT '发货时间',
    `receive_time` DATETIME DEFAULT NULL COMMENT '收货时间',
    `close_time` DATETIME DEFAULT NULL COMMENT '关闭时间',
    `receiver_name` VARCHAR(50) NOT NULL COMMENT '收货人姓名',
    `receiver_mobile` VARCHAR(20) NOT NULL COMMENT '收货人电话',
    `receiver_province` VARCHAR(20) NOT NULL COMMENT '收货省份',
    `receiver_city` VARCHAR(20) NOT NULL COMMENT '收货城市',
    `receiver_district` VARCHAR(20) DEFAULT NULL COMMENT '收货区县',
    `receiver_address` VARCHAR(200) NOT NULL COMMENT '收货详细地址',
    `buyer_message` VARCHAR(255) DEFAULT NULL COMMENT '买家留言',
    `remark` VARCHAR(255) DEFAULT NULL COMMENT '商家备注',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`order_id`),
    UNIQUE KEY `uk_order_no` (`order_no`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_order_status` (`order_status`),
    KEY `idx_create_time` (`create_time`),
    KEY `idx_pay_time` (`pay_time`),
    CONSTRAINT `fk_order_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单主表';

-- 插入订单测试数据（扩展版）
INSERT INTO `orders` (`order_no`, `user_id`, `order_status`, `pay_status`, `shipping_status`, `order_amount`, `pay_amount`, `freight_amount`, `discount_amount`, `coupon_amount`, `points_amount`, `pay_method`, `pay_time`, `ship_time`, `receive_time`, `receiver_name`, `receiver_mobile`, `receiver_province`, `receiver_city`, `receiver_district`, `receiver_address`, `buyer_message`) VALUES
('202411150001', 1, '已完成', '已支付', '已收货', 10999.00, 10499.00, 0.00, 500.00, 300.00, 200.00, '支付宝', '2024-11-15 10:30:15', '2024-11-16 14:20:30', '2024-11-19 16:45:22', '张三', '13800138001', '北京市', '朝阳区', '朝阳区', '建国路88号SOHO现代城A座1501室', '请尽快发货，谢谢！'),
('202411180002', 2, '已完成', '已支付', '已收货', 2799.00, 2599.00, 0.00, 200.00, 150.00, 50.00, '微信支付', '2024-11-18 11:45:20', '2024-11-19 09:15:10', '2024-11-22 10:30:45', '李四', '13900139002', '上海市', '浦东新区', '浦东新区', '陆家嘴金融贸易区世纪大道100号', '工作日可收货'),
('202411200003', 3, '已发货', '已支付', '已发货', 13998.00, 13598.00, 0.00, 400.00, 300.00, 100.00, '支付宝', '2024-11-20 15:20:10', '2024-11-21 10:30:00', NULL, '王五', '13700137003', '广东省', '深圳市', '南山区', '科技园南区高新南一道6号', NULL),
('202411220004', 4, '已完成', '已支付', '已收货', 1398.00, 1348.00, 10.00, 50.00, 40.00, 0.00, '微信支付', '2024-11-22 16:50:30', '2024-11-23 10:30:45', '2024-11-25 12:20:15', '赵六', '13600136004', '四川省', '成都市', '高新区', '天府大道中段1388号', '包装请结实一些'),
('202411230005', 5, '已取消', '未支付', '未发货', 322.00, 322.00, 0.00, 0.00, 0.00, 0.00, NULL, NULL, NULL, NULL, '孙七', '13500135005', '江苏省', '南京市', '玄武区', '中山东路18号', '不想要了'),
('202411250006', 6, '已完成', '已支付', '已收货', 696.00, 676.00, 20.00, 40.00, 0.00, 20.00, '支付宝', '2024-11-25 09:10:25', '2024-11-26 16:40:50', '2024-11-28 14:30:20', '周八', '13400134006', '浙江省', '杭州市', '西湖区', '文三路478号', '送人的，请帮忙包装精美些'),
('202411260007', 7, '已完成', '已支付', '已收货', 20797.00, 20297.00, 0.00, 500.00, 400.00, 100.00, '支付宝', '2024-11-26 14:25:35', '2024-11-27 11:10:20', '2024-11-30 15:20:30', '吴九', '13300133007', '湖北省', '武汉市', '洪山区', '珞喻路1037号', NULL),
('202411270008', 8, '已取消', '未支付', '未发货', 1348.00, 1298.00, 0.00, 50.00, 0.00, 50.00, NULL, NULL, NULL, NULL, '郑十', '13200132008', '辽宁省', '大连市', '中山区', '人民路68号', NULL),
('202411280009', 9, '已完成', '已支付', '已收货', 698.00, 678.00, 20.00, 40.00, 0.00, 20.00, '微信支付', '2024-11-28 11:30:45', '2024-11-29 13:20:15', '2024-12-01 10:15:30', '陈一', '13100131009', '山东省', '青岛市', '市南区', '香港中路10号', '周六日配送'),
('202411290010', 10, '已发货', '已支付', '已发货', 7498.00, 7398.00, 0.00, 100.00, 50.00, 50.00, '支付宝', '2024-11-29 16:45:20', '2024-11-30 09:20:15', NULL, '刘二', '13000130010', '河南省', '郑州市', '金水区', '花园路126号', NULL),
('202411290011', 11, '已完成', '已支付', '已收货', 1279.00, 1249.00, 10.00, 30.00, 0.00, 10.00, '微信支付', '2024-11-29 10:20:30', '2024-11-30 11:30:45', '2024-12-01 16:40:20', '黄三', '13800138011', '四川省', '成都市', '武侯区', '天府软件园B区7栋', NULL),
('202411300012', 12, '待支付', '未支付', '未发货', 158.00, 153.00, 10.00, 5.00, 0.00, 0.00, NULL, NULL, NULL, NULL, '林四', '13900139012', '福建省', '福州市', '鼓楼区', '五一北路158号', NULL),
('202411300013', 13, '已支付', '已支付', '未发货', 8499.00, 8299.00, 0.00, 200.00, 150.00, 50.00, '支付宝', '2024-11-30 14:35:20', NULL, NULL, '徐五', '13700137013', '湖南省', '长沙市', '岳麓区', '麓谷企业广场C3栋', '请用顺丰快递'),
('202411300014', 14, '已完成', '已支付', '已收货', 1798.00, 1748.00, 20.00, 50.00, 30.00, 0.00, '微信支付', '2024-11-30 09:50:15', '2024-11-30 16:20:30', '2024-12-01 11:30:45', '何六', '13600136014', '内蒙古', '呼和浩特市', '新城区', '成吉思汗大街1号', NULL),
('202412010015', 15, '已发货', '已支付', '已发货', 17497.00, 17097.00, 0.00, 400.00, 300.00, 100.00, '支付宝', '2024-12-01 10:15:30', '2024-12-01 15:40:20', NULL, '郭七', '13500135015', '陕西省', '西安市', '雁塔区', '科技路38号', '贵重物品，请小心轻放'),
('202412010016', 1, '待支付', '未支付', '未发货', 4490.00, 4390.00, 0.00, 100.00, 0.00, 100.00, NULL, NULL, NULL, NULL, '张三', '13800138001', '北京市', '朝阳区', '朝阳区', '建国路88号SOHO现代城A座1501室', NULL),
('202412010017', 3, '已支付', '已支付', '未发货', 2499.00, 2399.00, 0.00, 100.00, 50.00, 50.00, '微信支付', '2024-12-01 11:20:45', NULL, NULL, '王五', '13700137003', '广东省', '深圳市', '南山区', '科技园南区高新南一道6号', NULL),
('202412010018', 7, '已完成', '已支付', '已收货', 254.00, 249.00, 10.00, 5.00, 0.00, 0.00, '支付宝', '2024-12-01 08:30:15', '2024-12-01 14:20:30', '2024-12-01 17:45:20', '吴九', '13300133007', '湖北省', '武汉市', '洪山区', '珞喻路1037号', NULL);

-- ========================================================================
-- 5. 订单明细表
-- ========================================================================
DROP TABLE IF EXISTS `order_items`;
CREATE TABLE `order_items` (
    `item_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '明细ID',
    `order_id` BIGINT UNSIGNED NOT NULL COMMENT '订单ID',
    `product_id` BIGINT UNSIGNED NOT NULL COMMENT '商品ID',
    `product_name` VARCHAR(200) NOT NULL COMMENT '商品名称',
    `product_image` VARCHAR(255) DEFAULT NULL COMMENT '商品图片',
    `product_price` DECIMAL(10,2) NOT NULL COMMENT '商品单价',
    `quantity` INT UNSIGNED NOT NULL COMMENT '购买数量',
    `total_amount` DECIMAL(10,2) NOT NULL COMMENT '明细总金额',
    `refund_status` ENUM('未申请', '退款中', '已退款', '已拒绝') DEFAULT '未申请' COMMENT '退款状态',
    `refund_amount` DECIMAL(10,2) DEFAULT 0.00 COMMENT '退款金额',
    PRIMARY KEY (`item_id`),
    KEY `idx_order_id` (`order_id`),
    KEY `idx_product_id` (`product_id`),
    CONSTRAINT `fk_item_order` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`) ON DELETE CASCADE,
    CONSTRAINT `fk_item_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单明细表';

-- 插入订单明细数据
INSERT INTO `order_items` (`order_id`, `product_id`, `product_name`, `product_price`, `quantity`, `total_amount`) VALUES
(1, 1, 'Apple iPhone 15 Pro Max 256GB 钛金属', 10999.00, 1, 10999.00),
(2, 7, '美的1.5匹变频空调挂机', 2799.00, 1, 2799.00),
(3, 11, 'Nike Air Max 270运动鞋', 699.00, 10, 6990.00),
(3, 2, '华为Mate 60 Pro 12GB+512GB 雅川青', 6499.00, 1, 6499.00),
(3, 14, 'Python编程从入门到精通', 69.00, 1, 69.00),
(3, 21, 'AirPods Pro 2代', 1699.00, 1, 1699.00),
(4, 13, '《人类简史》精装版', 58.00, 20, 1160.00),
(4, 14, 'Python编程从入门到精通', 69.00, 1, 69.00),
(4, 12, 'Adidas Ultra Boost 22跑步鞋', 899.00, 1, 899.00),
(6, 8, '九阳破壁机L18-Y915S', 599.00, 1, 599.00),
(6, 20, '《活着》余华著', 25.00, 1, 25.00),
(6, 14, 'Python编程从入门到精通', 69.00, 1, 69.00),
(7, 4, '联想ThinkPad X1 Carbon 14英寸轻薄本', 11999.00, 1, 11999.00),
(7, 2, '华为Mate 60 Pro 12GB+512GB 雅川青', 6499.00, 1, 6499.00),
(7, 18, '优衣库女士羽绒服', 599.00, 1, 599.00),
(7, 21, 'AirPods Pro 2代', 1699.00, 1, 1699.00),
(8, 13, '《人类简史》精装版', 58.00, 20, 1160.00),
(8, 12, 'Adidas Ultra Boost 22跑步鞋', 899.00, 1, 899.00),
(9, 12, 'Adidas Ultra Boost 22跑步鞋', 899.00, 1, 899.00),
(9, 13, '《人类简史》精装版', 58.00, 1, 58.00),
(10, 3, '小米14 Ultra 16GB+1TB 徕卡影像', 5999.00, 1, 5999.00),
(10, 13, '《人类简史》精装版', 58.00, 20, 1160.00),
(10, 17, '美的电磁炉C21-RT2176', 199.00, 1, 199.00),
(11, 22, '三只松鼠每日坚果礼盒', 128.00, 10, 1280.00),
(12, 13, '《人类简史》精装版', 58.00, 2, 116.00),
(12, 20, '《活着》余华著', 25.00, 1, 25.00),
(13, 5, '华硕ROG魔霸7 Plus 17.3英寸游戏本', 8499.00, 1, 8499.00),
(14, 21, 'AirPods Pro 2代', 1699.00, 1, 1699.00),
(14, 9, '优衣库男士纯棉T恤', 79.00, 1, 79.00),
(15, 4, '联想ThinkPad X1 Carbon 14英寸轻薄本', 11999.00, 1, 11999.00),
(15, 3, '小米14 Ultra 16GB+1TB 徕卡影像', 5999.00, 1, 5999.00),
(16, 24, '戴森V15吸尘器', 4490.00, 1, 4490.00),
(17, 25, '小米电视65英寸4K', 2499.00, 1, 2499.00),
(18, 13, '《人类简史》精装版', 58.00, 4, 232.00),
(18, 20, '《活着》余华著', 25.00, 1, 25.00);

-- ========================================================================
-- 6. 商品评价表（新增）
-- ========================================================================
DROP TABLE IF EXISTS `product_reviews`;
CREATE TABLE `product_reviews` (
    `review_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '评价ID',
    `order_id` BIGINT UNSIGNED NOT NULL COMMENT '订单ID',
    `product_id` BIGINT UNSIGNED NOT NULL COMMENT '商品ID',
    `user_id` BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    `rating` TINYINT UNSIGNED NOT NULL COMMENT '评分(1-5星)',
    `content` TEXT DEFAULT NULL COMMENT '评价内容',
    `images` JSON DEFAULT NULL COMMENT '评价图片(JSON数组)',
    `is_anonymous` TINYINT(1) DEFAULT 0 COMMENT '是否匿名(0-否,1-是)',
    `helpful_count` INT UNSIGNED DEFAULT 0 COMMENT '有用数',
    `reply_content` TEXT DEFAULT NULL COMMENT '商家回复',
    `reply_time` DATETIME DEFAULT NULL COMMENT '回复时间',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '评价时间',
    PRIMARY KEY (`review_id`),
    KEY `idx_product_id` (`product_id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_rating` (`rating`),
    CONSTRAINT `fk_review_order` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`),
    CONSTRAINT `fk_review_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`),
    CONSTRAINT `fk_review_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品评价表';

-- 插入商品评价数据
INSERT INTO `product_reviews` (`order_id`, `product_id`, `user_id`, `rating`, `content`, `images`, `is_anonymous`, `helpful_count`, `reply_content`, `reply_time`, `create_time`) VALUES
(1, 1, 1, 5, '手机非常棒！钛金属外观高端大气，A17 Pro芯片性能强劲，拍照效果一流。物流也很快，客服态度好，强烈推荐！', '["https://example.com/review1_1.jpg", "https://example.com/review1_2.jpg"]', 0, 25, '感谢您的好评和支持，祝您使用愉快！', '2024-11-20 09:30:00', '2024-11-20 08:15:30'),
(2, 7, 2, 4, '空调制冷效果不错，声音也比较小，一级能效很省电。安装师傅很专业，服务态度好。美中不足的是遥控器设计有点复杂。', NULL, 0, 12, '感谢您的反馈，我们会持续改进产品设计，祝您使用愉快！', '2024-11-23 10:20:00', '2024-11-23 09:45:15'),
(3, 11, 3, 5, 'Nike的鞋子一如既往的好，气垫非常舒服，走路不累。配色也很好看，搭配衣服很方便。十双一起买送朋友，都很满意！', '["https://example.com/review3_1.jpg"]', 0, 18, '感谢支持Nike品牌，欢迎再次光临！', '2024-11-22 14:30:00', '2024-11-22 13:10:20'),
(4, 13, 4, 5, '书的质量很好，精装版很有质感。内容非常精彩，作者的视角独特，让我对人类历史有了全新的认识。强烈推荐这本书！', NULL, 0, 45, '感谢您的好评，阅读愉快！', '2024-11-26 11:00:00', '2024-11-26 10:30:45'),
(6, 8, 6, 5, '破壁机功能强大，打豆浆、果汁都很细腻，声音也在可接受范围内。清洗方便，性价比很高，值得购买！', '["https://example.com/review6_1.jpg", "https://example.com/review6_2.jpg"]', 0, 32, '感谢支持，祝您使用愉快！', '2024-11-29 09:15:00', '2024-11-29 08:40:30'),
(7, 4, 7, 5, 'ThinkPad的品质一直很稳定，轻薄便携，屏幕显示效果出色。键盘手感极佳，适合长时间办公。电池续航也不错，满意！', NULL, 0, 28, '感谢选择ThinkPad，欢迎再次光临！', '2024-12-01 10:20:00', '2024-12-01 09:50:15'),
(7, 2, 7, 5, '华为Mate 60 Pro真的很强大！卫星通话功能很实用，摄像头拍照效果惊艳。5G信号稳定，电池续航给力。国产之光！', '["https://example.com/review7_1.jpg"]', 0, 67, '感谢支持国产品牌，祝您使用愉快！', '2024-12-01 10:25:00', '2024-12-01 09:55:20'),
(9, 12, 9, 4, 'Adidas的跑鞋质量没得说，BOOST科技真的很舒服。唯一不足就是价格有点贵，不过性能确实对得起价格。', NULL, 0, 15, '感谢您的评价和建议！', '2024-12-01 15:30:00', '2024-12-01 14:45:30'),
(10, 3, 10, 5, '小米14 Ultra的徕卡镜头真不是盖的，拍照效果堪比专业相机。骁龙8 Gen3处理器性能强悍，玩游戏超流畅！', '["https://example.com/review10_1.jpg", "https://example.com/review10_2.jpg", "https://example.com/review10_3.jpg"]', 0, 52, '感谢支持小米，欢迎继续关注小米产品！', '2024-12-01 11:20:00', '2024-12-01 10:35:15'),
(11, 22, 11, 5, '三只松鼠的坚果很新鲜，包装精美，每天一包营养又健康。办公室必备零食，同事们都很喜欢！', NULL, 1, 23, '感谢您的好评，欢迎再次购买！', '2024-12-01 14:30:00', '2024-12-01 13:50:40'),
(14, 21, 14, 4, 'AirPods Pro降噪效果确实不错，音质也很好。就是价格有点贵，而且续航时间可以再长一点就更完美了。', NULL, 0, 19, '感谢您的反馈，我们会继续优化产品！', '2024-12-01 16:40:00', '2024-12-01 16:10:25'),
(18, 13, 7, 5, '第二次购买了，准备送给朋友们。这本书真的很值得一读，对理解人类文明很有帮助。', NULL, 0, 8, '感谢您的再次购买和推荐！', '2024-12-01 20:15:00', '2024-12-01 19:45:30');

-- ========================================================================
-- 7. 购物车表（新增）
-- ========================================================================
DROP TABLE IF EXISTS `shopping_cart`;
CREATE TABLE `shopping_cart` (
    `cart_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '购物车ID',
    `user_id` BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    `product_id` BIGINT UNSIGNED NOT NULL COMMENT '商品ID',
    `quantity` INT UNSIGNED NOT NULL DEFAULT 1 COMMENT '数量',
    `is_checked` TINYINT(1) DEFAULT 1 COMMENT '是否选中(0-未选,1-已选)',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '加入时间',
    `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`cart_id`),
    UNIQUE KEY `uk_user_product` (`user_id`, `product_id`),
    KEY `idx_user_id` (`user_id`),
    CONSTRAINT `fk_cart_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
    CONSTRAINT `fk_cart_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='购物车表';

-- 插入购物车数据
INSERT INTO `shopping_cart` (`user_id`, `product_id`, `quantity`, `is_checked`, `create_time`) VALUES
(1, 15, 1, 1, '2024-11-28 10:30:00'),
(1, 22, 2, 1, '2024-11-29 14:20:00'),
(2, 18, 1, 1, '2024-11-30 09:15:00'),
(3, 6, 1, 0, '2024-11-27 16:40:00'),
(4, 14, 3, 1, '2024-11-29 11:25:00'),
(4, 20, 5, 1, '2024-11-29 11:30:00'),
(6, 17, 2, 1, '2024-11-30 15:45:00'),
(9, 23, 1, 1, '2024-11-28 13:20:00'),
(10, 9, 3, 1, '2024-11-30 10:50:00'),
(11, 19, 1, 1, '2024-11-29 16:15:00'),
(12, 13, 2, 1, '2024-11-30 09:30:00'),
(13, 25, 1, 0, '2024-11-27 14:10:00'),
(15, 21, 1, 1, '2024-11-30 11:40:00');

-- ========================================================================
-- 8. 优惠券表（新增）
-- ========================================================================
DROP TABLE IF EXISTS `coupons`;
CREATE TABLE `coupons` (
    `coupon_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '优惠券ID',
    `coupon_name` VARCHAR(100) NOT NULL COMMENT '优惠券名称',
    `coupon_type` ENUM('满减券', '折扣券', '无门槛券') DEFAULT '满减券' COMMENT '优惠券类型',
    `discount_amount` DECIMAL(10,2) DEFAULT 0.00 COMMENT '优惠金额',
    `discount_rate` DECIMAL(5,2) DEFAULT 0.00 COMMENT '折扣率(如8.5表示85折)',
    `min_amount` DECIMAL(10,2) DEFAULT 0.00 COMMENT '最低消费金额',
    `total_quantity` INT UNSIGNED NOT NULL COMMENT '发放总数',
    `received_quantity` INT UNSIGNED DEFAULT 0 COMMENT '已领取数量',
    `used_quantity` INT UNSIGNED DEFAULT 0 COMMENT '已使用数量',
    `valid_days` INT UNSIGNED DEFAULT 30 COMMENT '有效天数',
    `start_time` DATETIME NOT NULL COMMENT '开始时间',
    `end_time` DATETIME NOT NULL COMMENT '结束时间',
    `status` ENUM('未开始', '进行中', '已结束') DEFAULT '进行中' COMMENT '状态',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`coupon_id`),
    KEY `idx_coupon_type` (`coupon_type`),
    KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='优惠券表';

-- 插入优惠券数据
INSERT INTO `coupons` (`coupon_name`, `coupon_type`, `discount_amount`, `discount_rate`, `min_amount`, `total_quantity`, `received_quantity`, `used_quantity`, `valid_days`, `start_time`, `end_time`, `status`) VALUES
('新用户专享50元券', '满减券', 50.00, 0.00, 100.00, 10000, 3245, 1876, 30, '2024-11-01 00:00:00', '2024-12-31 23:59:59', '进行中'),
('双十一满300减50', '满减券', 50.00, 0.00, 300.00, 50000, 28765, 15432, 15, '2024-11-01 00:00:00', '2024-11-15 23:59:59', '已结束'),
('电子产品9折券', '折扣券', 0.00, 9.00, 500.00, 5000, 2345, 1234, 30, '2024-11-20 00:00:00', '2024-12-20 23:59:59', '进行中'),
('全品类满1000减100', '满减券', 100.00, 0.00, 1000.00, 20000, 8976, 4532, 30, '2024-12-01 00:00:00', '2024-12-31 23:59:59', '进行中'),
('无门槛20元券', '无门槛券', 20.00, 0.00, 0.00, 30000, 12456, 6789, 15, '2024-11-25 00:00:00', '2024-12-10 23:59:59', '进行中'),
('家电满2000减200', '满减券', 200.00, 0.00, 2000.00, 8000, 3456, 1890, 30, '2024-11-15 00:00:00', '2024-12-15 23:59:59', '进行中'),
('图书8.5折券', '折扣券', 0.00, 8.50, 50.00, 15000, 7890, 4567, 60, '2024-11-01 00:00:00', '2024-12-31 23:59:59', '进行中');

-- ========================================================================
-- 9. 用户优惠券表（新增）
-- ========================================================================
DROP TABLE IF EXISTS `user_coupons`;
CREATE TABLE `user_coupons` (
    `user_coupon_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户优惠券ID',
    `user_id` BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    `coupon_id` BIGINT UNSIGNED NOT NULL COMMENT '优惠券ID',
    `order_id` BIGINT UNSIGNED DEFAULT NULL COMMENT '使用的订单ID',
    `receive_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '领取时间',
    `use_time` DATETIME DEFAULT NULL COMMENT '使用时间',
    `expire_time` DATETIME NOT NULL COMMENT '过期时间',
    `status` ENUM('未使用', '已使用', '已过期') DEFAULT '未使用' COMMENT '状态',
    PRIMARY KEY (`user_coupon_id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_coupon_id` (`coupon_id`),
    KEY `idx_status` (`status`),
    CONSTRAINT `fk_user_coupon_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
    CONSTRAINT `fk_user_coupon_coupon` FOREIGN KEY (`coupon_id`) REFERENCES `coupons` (`coupon_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户优惠券表';

-- 插入用户优惠券数据
INSERT INTO `user_coupons` (`user_id`, `coupon_id`, `order_id`, `receive_time`, `use_time`, `expire_time`, `status`) VALUES
(1, 1, 1, '2024-11-10 10:00:00', '2024-11-15 10:30:15', '2024-12-10 23:59:59', '已使用'),
(1, 4, NULL, '2024-12-01 09:00:00', NULL, '2024-12-31 23:59:59', '未使用'),
(2, 1, 2, '2024-11-12 14:30:00', '2024-11-18 11:45:20', '2024-12-12 23:59:59', '已使用'),
(3, 2, 3, '2024-11-05 11:20:00', '2024-11-20 15:20:10', '2024-11-20 23:59:59', '已使用'),
(3, 3, NULL, '2024-11-22 16:30:00', NULL, '2024-12-22 23:59:59', '未使用'),
(4, 1, 4, '2024-11-15 09:40:00', '2024-11-22 16:50:30', '2024-12-15 23:59:59', '已使用'),
(6, 5, NULL, '2024-11-26 10:20:00', NULL, '2024-12-11 23:59:59', '未使用'),
(7, 4, 7, '2024-11-20 13:45:00', '2024-11-26 14:25:35', '2024-12-20 23:59:59', '已使用'),
(9, 5, 9, '2024-11-25 15:10:00', '2024-11-28 11:30:45', '2024-12-10 23:59:59', '已使用'),
(10, 4, 10, '2024-11-28 09:30:00', '2024-11-29 16:45:20', '2024-12-28 23:59:59', '已使用'),
(11, 5, NULL, '2024-11-27 11:15:00', NULL, '2024-12-12 23:59:59', '未使用'),
(13, 3, 13, '2024-11-25 14:20:00', '2024-11-30 14:35:20', '2024-12-25 23:59:59', '已使用'),
(14, 5, 14, '2024-11-28 10:40:00', '2024-11-30 09:50:15', '2024-12-13 23:59:59', '已使用'),
(15, 4, 15, '2024-11-30 08:50:00', '2024-12-01 10:15:30', '2024-12-30 23:59:59', '已使用');

-- ========================================================================
-- 10. 更新商品销量统计
-- ========================================================================
UPDATE products p SET p.sales_volume = (
    SELECT COALESCE(SUM(oi.quantity), 0) 
    FROM order_items oi 
    JOIN orders o ON oi.order_id = o.order_id 
    WHERE oi.product_id = p.product_id 
    AND o.order_status IN ('已完成', '已发货')
);

-- ========================================================================
-- 11. 创建视图：订单统计视图
-- ========================================================================
DROP VIEW IF EXISTS `v_order_statistics`;
CREATE VIEW `v_order_statistics` AS
SELECT 
    DATE(o.create_time) AS `统计日期`,
    COUNT(DISTINCT o.order_id) AS `订单总数`,
    COUNT(DISTINCT o.user_id) AS `下单用户数`,
    SUM(o.pay_amount) AS `订单总金额`,
    ROUND(AVG(o.pay_amount), 2) AS `平均订单金额`,
    SUM(CASE WHEN o.order_status = '已完成' THEN 1 ELSE 0 END) AS `完成订单数`,
    SUM(CASE WHEN o.order_status = '已取消' THEN 1 ELSE 0 END) AS `取消订单数`,
    ROUND(SUM(CASE WHEN o.order_status = '已完成' THEN o.pay_amount ELSE 0 END), 2) AS `完成订单金额`
FROM orders o
GROUP BY DATE(o.create_time)
ORDER BY `统计日期` DESC;

-- ========================================================================
-- 12. 创建视图：商品销售排行榜
-- ========================================================================
DROP VIEW IF EXISTS `v_product_sales_rank`;
CREATE VIEW `v_product_sales_rank` AS
SELECT 
    p.product_id AS `商品ID`,
    p.product_name AS `商品名称`,
    c.category_name AS `分类`,
    p.brand AS `品牌`,
    p.sale_price AS `单价`,
    p.sales_volume AS `总销量`,
    ROUND(p.sales_volume * p.sale_price, 2) AS `销售额`,
    ROW_NUMBER() OVER (ORDER BY p.sales_volume DESC) AS `销量排名`,
    ROW_NUMBER() OVER (ORDER BY p.sales_volume * p.sale_price DESC) AS `销售额排名`
FROM products p
LEFT JOIN product_category c ON p.category_id = c.category_id
WHERE p.status = '在售'
ORDER BY p.sales_volume DESC;

-- ========================================================================
-- 13. 创建视图：用户购买行为统计
-- ========================================================================
DROP VIEW IF EXISTS `v_user_purchase_behavior`;
CREATE VIEW `v_user_purchase_behavior` AS
SELECT 
    u.user_id AS `用户ID`,
    u.username AS `用户名`,
    u.real_name AS `姓名`,
    u.user_level AS `用户等级`,
    u.total_points AS `总积分`,
    u.available_points AS `可用积分`,
    COUNT(DISTINCT o.order_id) AS `订单数量`,
    ROUND(SUM(o.pay_amount), 2) AS `总消费金额`,
    ROUND(AVG(o.pay_amount), 2) AS `平均订单金额`,
    ROUND(MAX(o.pay_amount), 2) AS `最大订单金额`,
    MIN(o.create_time) AS `首次下单时间`,
    MAX(o.create_time) AS `最近下单时间`,
    DATEDIFF(CURDATE(), MAX(o.create_time)) AS `距上次下单天数`
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id AND o.order_status != '已取消'
WHERE u.status = '正常'
GROUP BY u.user_id, u.username, u.real_name, u.user_level, u.total_points, u.available_points
ORDER BY `总消费金额` DESC;

-- ========================================================================
-- 14. 创建视图：商品评价统计
-- ========================================================================
DROP VIEW IF EXISTS `v_product_review_stats`;
CREATE VIEW `v_product_review_stats` AS
SELECT 
    p.product_id AS `商品ID`,
    p.product_name AS `商品名称`,
    COUNT(r.review_id) AS `评价总数`,
    ROUND(AVG(r.rating), 2) AS `平均评分`,
    SUM(CASE WHEN r.rating = 5 THEN 1 ELSE 0 END) AS `5星评价数`,
    SUM(CASE WHEN r.rating = 4 THEN 1 ELSE 0 END) AS `4星评价数`,
    SUM(CASE WHEN r.rating = 3 THEN 1 ELSE 0 END) AS `3星评价数`,
    SUM(CASE WHEN r.rating = 2 THEN 1 ELSE 0 END) AS `2星评价数`,
    SUM(CASE WHEN r.rating = 1 THEN 1 ELSE 0 END) AS `1星评价数`,
    ROUND(SUM(CASE WHEN r.rating >= 4 THEN 1 ELSE 0 END) / COUNT(r.review_id) * 100, 2) AS `好评率`
FROM products p
LEFT JOIN product_reviews r ON p.product_id = r.product_id
WHERE p.status = '在售'
GROUP BY p.product_id, p.product_name
HAVING COUNT(r.review_id) > 0
ORDER BY `平均评分` DESC, `评价总数` DESC;

-- ========================================================================
-- 15. 创建存储过程：计算用户等级
-- ========================================================================
DELIMITER $$

DROP PROCEDURE IF EXISTS `sp_update_user_level`$$
CREATE PROCEDURE `sp_update_user_level`(IN p_user_id BIGINT)
BEGIN
    DECLARE v_total_amount DECIMAL(10,2);
    DECLARE v_new_level TINYINT;
    
    -- 计算用户总消费金额
    SELECT COALESCE(SUM(pay_amount), 0) INTO v_total_amount
    FROM orders
    WHERE user_id = p_user_id AND order_status = '已完成';
    
    -- 根据消费金额确定等级
    IF v_total_amount >= 50000 THEN
        SET v_new_level = 4; -- 钻石
    ELSEIF v_total_amount >= 20000 THEN
        SET v_new_level = 3; -- 金卡
    ELSEIF v_total_amount >= 5000 THEN
        SET v_new_level = 2; -- 银卡
    ELSE
        SET v_new_level = 1; -- 普通
    END IF;
    
    -- 更新用户等级
    UPDATE users SET user_level = v_new_level WHERE user_id = p_user_id;
    
    SELECT CONCAT('用户等级已更新为: ', v_new_level, ' (总消费: ', v_total_amount, '元)') AS result;
END$$

DELIMITER ;

-- ========================================================================
-- 16. 创建存储过程：生成订单统计报表
-- ========================================================================
DELIMITER $$

DROP PROCEDURE IF EXISTS `sp_order_report`$$
CREATE PROCEDURE `sp_order_report`(IN p_start_date DATE, IN p_end_date DATE)
BEGIN
    SELECT 
        DATE(create_time) AS `日期`,
        COUNT(*) AS `订单总数`,
        SUM(CASE WHEN order_status = '已完成' THEN 1 ELSE 0 END) AS `完成订单`,
        SUM(CASE WHEN order_status = '已取消' THEN 1 ELSE 0 END) AS `取消订单`,
        ROUND(SUM(order_amount), 2) AS `订单总额`,
        ROUND(SUM(pay_amount), 2) AS `实收总额`,
        ROUND(SUM(discount_amount), 2) AS `优惠总额`,
        ROUND(AVG(pay_amount), 2) AS `平均客单价`
    FROM orders
    WHERE DATE(create_time) BETWEEN p_start_date AND p_end_date
    GROUP BY DATE(create_time)
    ORDER BY DATE(create_time) DESC;
END$$

DELIMITER ;

-- ========================================================================
-- 17. 创建函数：计算商品好评率
-- ========================================================================
DELIMITER $$

DROP FUNCTION IF EXISTS `fn_get_product_good_rate`$$
CREATE FUNCTION `fn_get_product_good_rate`(p_product_id BIGINT)
RETURNS DECIMAL(5,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_total_count INT;
    DECLARE v_good_count INT;
    DECLARE v_rate DECIMAL(5,2);
    
    SELECT COUNT(*) INTO v_total_count
    FROM product_reviews
    WHERE product_id = p_product_id;
    
    IF v_total_count = 0 THEN
        RETURN 100.00;
    END IF;
    
    SELECT COUNT(*) INTO v_good_count
    FROM product_reviews
    WHERE product_id = p_product_id AND rating >= 4;
    
    SET v_rate = (v_good_count / v_total_count) * 100;
    
    RETURN v_rate;
END$$

DELIMITER ;

-- ========================================================================
-- 18. 创建触发器：订单创建后更新商品库存
-- ========================================================================
DELIMITER $$

DROP TRIGGER IF EXISTS `tr_order_items_after_insert`$$
CREATE TRIGGER `tr_order_items_after_insert`
AFTER INSERT ON `order_items`
FOR EACH ROW
BEGIN
    -- 减少商品库存
    UPDATE products 
    SET stock_quantity = stock_quantity - NEW.quantity
    WHERE product_id = NEW.product_id;
END$$

DELIMITER ;

-- ========================================================================
-- 19. 创建触发器：订单取消后恢复商品库存
-- ========================================================================
DELIMITER $$

DROP TRIGGER IF EXISTS `tr_orders_after_update`$$
CREATE TRIGGER `tr_orders_after_update`
AFTER UPDATE ON `orders`
FOR EACH ROW
BEGIN
    -- 如果订单状态从非取消变为已取消，恢复库存
    IF OLD.order_status != '已取消' AND NEW.order_status = '已取消' THEN
        UPDATE products p
        INNER JOIN order_items oi ON p.product_id = oi.product_id
        SET p.stock_quantity = p.stock_quantity + oi.quantity
        WHERE oi.order_id = NEW.order_id;
    END IF;
END$$

DELIMITER ;

-- ========================================================================
-- 20. 创建触发器：用户注册时赠送优惠券
-- ========================================================================
DELIMITER $$

DROP TRIGGER IF EXISTS `tr_users_after_insert`$$
CREATE TRIGGER `tr_users_after_insert`
AFTER INSERT ON `users`
FOR EACH ROW
BEGIN
    DECLARE v_coupon_id BIGINT;
    
    -- 获取新用户专享优惠券ID
    SELECT coupon_id INTO v_coupon_id
    FROM coupons
    WHERE coupon_name = '新用户专享50元券' AND status = '进行中'
    LIMIT 1;
    
    -- 如果优惠券存在，则赠送给新用户
    IF v_coupon_id IS NOT NULL THEN
        INSERT INTO user_coupons (user_id, coupon_id, expire_time, status)
        VALUES (NEW.user_id, v_coupon_id, DATE_ADD(NOW(), INTERVAL 30 DAY), '未使用');
        
        -- 更新优惠券已领取数量
        UPDATE coupons SET received_quantity = received_quantity + 1
        WHERE coupon_id = v_coupon_id;
    END IF;
END$$

DELIMITER ;

-- ========================================================================
-- 21. 创建事件：每天自动更新过期优惠券状态
-- ========================================================================
SET GLOBAL event_scheduler = ON;

DELIMITER $$

DROP EVENT IF EXISTS `evt_update_expired_coupons`$$
CREATE EVENT `evt_update_expired_coupons`
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_TIMESTAMP
DO
BEGIN
    -- 更新用户优惠券状态
    UPDATE user_coupons
    SET status = '已过期'
    WHERE status = '未使用' AND expire_time < NOW();
    
    -- 更新优惠券表状态
    UPDATE coupons
    SET status = '已结束'
    WHERE status = '进行中' AND end_time < NOW();
END$$

DELIMITER ;

-- ========================================================================
-- 22. 创建索引（额外的性能优化）
-- ========================================================================
-- 已在表创建时添加了主要索引，这里添加一些复合索引

CREATE INDEX idx_orders_user_status ON orders(user_id, order_status);
CREATE INDEX idx_orders_user_create ON orders(user_id, create_time);
CREATE INDEX idx_product_reviews_product_rating ON product_reviews(product_id, rating);
CREATE INDEX idx_user_coupons_user_status ON user_coupons(user_id, status);

-- ========================================================================
-- 23. 数据完整性检查和统计信息
-- ========================================================================

-- 显示各表的记录数
SELECT '=== 数据库表记录统计 ===' AS info;

SELECT '用户表' AS 表名, COUNT(*) AS 记录数 FROM users
UNION ALL
SELECT '商品分类表', COUNT(*) FROM product_category
UNION ALL
SELECT '商品表', COUNT(*) FROM products
UNION ALL
SELECT '订单表', COUNT(*) FROM orders
UNION ALL
SELECT '订单明细表', COUNT(*) FROM order_items
UNION ALL
SELECT '商品评价表', COUNT(*) FROM product_reviews
UNION ALL
SELECT '购物车表', COUNT(*) FROM shopping_cart
UNION ALL
SELECT '优惠券表', COUNT(*) FROM coupons
UNION ALL
SELECT '用户优惠券表', COUNT(*) FROM user_coupons;

-- 显示订单状态分布
SELECT '=== 订单状态分布 ===' AS info;
SELECT order_status AS 订单状态, COUNT(*) AS 数量, 
       CONCAT(ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM orders), 2), '%') AS 占比
FROM orders
GROUP BY order_status
ORDER BY 数量 DESC;

-- 显示商品分类统计
SELECT '=== 商品分类统计 ===' AS info;
SELECT c.category_name AS 分类名称, COUNT(p.product_id) AS 商品数量
FROM product_category c
LEFT JOIN products p ON c.category_id = p.category_id
WHERE c.level = 2
GROUP BY c.category_id, c.category_name
ORDER BY 商品数量 DESC;

-- ========================================================================
-- 脚本执行完成提示
-- ========================================================================
SELECT '========================================' AS '';
SELECT '数据库创建完成！' AS 信息;
SELECT '数据库名称: e_commerce' AS '';
SELECT '包含表: 9个主表' AS '';
SELECT '包含视图: 4个统计视图' AS '';
SELECT '包含存储过程: 2个' AS '';
SELECT '包含函数: 1个' AS '';
SELECT '包含触发器: 3个' AS '';
SELECT '包含事件: 1个' AS '';
SELECT '========================================' AS '';

-- 恢复系统变量
SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;