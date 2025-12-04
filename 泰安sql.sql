-- ============================================
-- 山东省泰安市大数据局测试数据库脚本
-- MySQL 8.0+
-- 创建日期: 2025-12-01
-- ============================================

-- 创建数据库
DROP DATABASE IF EXISTS taian_bigdata;
CREATE DATABASE taian_bigdata DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE taian_bigdata;

-- ============================================
-- 1. 部门信息表
-- ============================================
DROP TABLE IF EXISTS department;
CREATE TABLE department (
    dept_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '部门ID',
    dept_name VARCHAR(100) NOT NULL COMMENT '部门名称',
    dept_code VARCHAR(50) NOT NULL UNIQUE COMMENT '部门编码',
    parent_id INT DEFAULT 0 COMMENT '上级部门ID',
    dept_level INT DEFAULT 1 COMMENT '部门层级',
    dept_leader VARCHAR(50) COMMENT '部门负责人',
    contact_phone VARCHAR(20) COMMENT '联系电话',
    office_address VARCHAR(200) COMMENT '办公地址',
    dept_function TEXT COMMENT '部门职能',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    status TINYINT DEFAULT 1 COMMENT '状态 1-正常 0-停用'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='部门信息表';

-- ============================================
-- 2. 员工信息表
-- ============================================
DROP TABLE IF EXISTS employee;
CREATE TABLE employee (
    emp_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '员工ID',
    emp_name VARCHAR(50) NOT NULL COMMENT '员工姓名',
    emp_code VARCHAR(50) NOT NULL UNIQUE COMMENT '员工工号',
    dept_id INT NOT NULL COMMENT '所属部门ID',
    position VARCHAR(50) COMMENT '职位',
    job_title VARCHAR(50) COMMENT '职称',
    gender ENUM('男', '女') DEFAULT '男' COMMENT '性别',
    id_card VARCHAR(18) COMMENT '身份证号',
    phone VARCHAR(20) COMMENT '手机号',
    email VARCHAR(100) COMMENT '邮箱',
    education VARCHAR(20) COMMENT '学历',
    entry_date DATE COMMENT '入职日期',
    employment_type ENUM('在编', '聘用', '借调', '实习') DEFAULT '在编' COMMENT '用工类型',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    status TINYINT DEFAULT 1 COMMENT '状态 1-在职 0-离职',
    FOREIGN KEY (dept_id) REFERENCES department(dept_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='员工信息表';

-- ============================================
-- 3. 政务信息化项目表
-- ============================================
DROP TABLE IF EXISTS project;
CREATE TABLE project (
    project_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '项目ID',
    project_name VARCHAR(200) NOT NULL COMMENT '项目名称',
    project_code VARCHAR(50) NOT NULL UNIQUE COMMENT '项目编号',
    project_type ENUM('新建', '升级改造', '运维', '其他') DEFAULT '新建' COMMENT '项目类型',
    budget DECIMAL(15,2) COMMENT '预算金额(万元)',
    actual_cost DECIMAL(15,2) COMMENT '实际花费(万元)',
    responsible_dept_id INT COMMENT '负责部门ID',
    project_manager VARCHAR(50) COMMENT '项目经理',
    contractor VARCHAR(200) COMMENT '承建单位',
    start_date DATE COMMENT '开始日期',
    end_date DATE COMMENT '结束日期',
    project_status ENUM('立项', '实施中', '验收中', '已完成', '已暂停') DEFAULT '立项' COMMENT '项目状态',
    project_desc TEXT COMMENT '项目描述',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (responsible_dept_id) REFERENCES department(dept_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='政务信息化项目表';

-- ============================================
-- 4. 数据资源目录表
-- ============================================
DROP TABLE IF EXISTS data_catalog;
CREATE TABLE data_catalog (
    catalog_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '目录ID',
    catalog_name VARCHAR(200) NOT NULL COMMENT '目录名称',
    catalog_code VARCHAR(100) NOT NULL UNIQUE COMMENT '目录编码',
    data_provider_dept_id INT COMMENT '数据提供部门ID',
    data_type ENUM('基础数据', '主题数据', '部门数据', '其他') DEFAULT '部门数据' COMMENT '数据类型',
    data_format ENUM('结构化', '半结构化', '非结构化') DEFAULT '结构化' COMMENT '数据格式',
    update_frequency ENUM('实时', '每日', '每周', '每月', '每年', '不定期') DEFAULT '每日' COMMENT '更新频率',
    data_volume BIGINT COMMENT '数据量(条)',
    open_level ENUM('公开', '有条件公开', '不公开') DEFAULT '有条件公开' COMMENT '开放等级',
    security_level ENUM('公开', '内部', '秘密', '机密') DEFAULT '内部' COMMENT '安全等级',
    catalog_desc TEXT COMMENT '目录描述',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    status TINYINT DEFAULT 1 COMMENT '状态 1-启用 0-停用',
    FOREIGN KEY (data_provider_dept_id) REFERENCES department(dept_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据资源目录表';

-- ============================================
-- 5. 数据共享申请表
-- ============================================
DROP TABLE IF EXISTS data_share_request;
CREATE TABLE data_share_request (
    request_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '申请ID',
    request_no VARCHAR(50) NOT NULL UNIQUE COMMENT '申请单号',
    catalog_id INT NOT NULL COMMENT '申请的数据目录ID',
    applicant_dept_id INT NOT NULL COMMENT '申请部门ID',
    applicant_name VARCHAR(50) NOT NULL COMMENT '申请人',
    applicant_phone VARCHAR(20) COMMENT '申请人电话',
    apply_reason TEXT COMMENT '申请理由',
    use_purpose TEXT COMMENT '使用用途',
    request_date DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '申请日期',
    approve_status ENUM('待审批', '已通过', '已驳回', '已撤销') DEFAULT '待审批' COMMENT '审批状态',
    approver VARCHAR(50) COMMENT '审批人',
    approve_date DATETIME COMMENT '审批日期',
    approve_opinion TEXT COMMENT '审批意见',
    valid_days INT DEFAULT 90 COMMENT '有效天数',
    FOREIGN KEY (catalog_id) REFERENCES data_catalog(catalog_id),
    FOREIGN KEY (applicant_dept_id) REFERENCES department(dept_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据共享申请表';

-- ============================================
-- 6. 政务服务事项表
-- ============================================
DROP TABLE IF EXISTS government_service;
CREATE TABLE government_service (
    service_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '事项ID',
    service_name VARCHAR(200) NOT NULL COMMENT '事项名称',
    service_code VARCHAR(100) NOT NULL UNIQUE COMMENT '事项编码',
    service_type ENUM('行政许可', '行政给付', '行政确认', '公共服务', '其他') DEFAULT '公共服务' COMMENT '事项类型',
    responsible_dept_id INT COMMENT '责任部门ID',
    service_object VARCHAR(100) COMMENT '服务对象',
    apply_condition TEXT COMMENT '申请条件',
    required_materials TEXT COMMENT '所需材料',
    handling_process TEXT COMMENT '办理流程',
    promise_days INT COMMENT '承诺办理天数',
    charge_standard VARCHAR(200) COMMENT '收费标准',
    online_handling TINYINT DEFAULT 1 COMMENT '是否支持网上办理 1-是 0-否',
    one_time_handling TINYINT DEFAULT 0 COMMENT '是否一次办结 1-是 0-否',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    status TINYINT DEFAULT 1 COMMENT '状态 1-启用 0-停用',
    FOREIGN KEY (responsible_dept_id) REFERENCES department(dept_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='政务服务事项表';

-- ============================================
-- 7. 系统运维记录表
-- ============================================
DROP TABLE IF EXISTS system_maintenance;
CREATE TABLE system_maintenance (
    maintenance_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '记录ID',
    system_name VARCHAR(100) NOT NULL COMMENT '系统名称',
    maintenance_type ENUM('日常巡检', '故障处理', '系统升级', '数据备份', '安全加固', '其他') DEFAULT '日常巡检' COMMENT '运维类型',
    maintenance_date DATE NOT NULL COMMENT '运维日期',
    start_time TIME COMMENT '开始时间',
    end_time TIME COMMENT '结束时间',
    responsible_person VARCHAR(50) COMMENT '负责人',
    maintenance_content TEXT COMMENT '运维内容',
    problem_desc TEXT COMMENT '问题描述',
    solution TEXT COMMENT '解决方案',
    result ENUM('正常', '异常', '待处理') DEFAULT '正常' COMMENT '运维结果',
    remark TEXT COMMENT '备注',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统运维记录表';

-- ============================================
-- 8. 数据质量检查表
-- ============================================
DROP TABLE IF EXISTS data_quality_check;
CREATE TABLE data_quality_check (
    check_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '检查ID',
    catalog_id INT NOT NULL COMMENT '数据目录ID',
    check_date DATE NOT NULL COMMENT '检查日期',
    check_person VARCHAR(50) COMMENT '检查人',
    completeness_score DECIMAL(5,2) COMMENT '完整性得分',
    accuracy_score DECIMAL(5,2) COMMENT '准确性得分',
    timeliness_score DECIMAL(5,2) COMMENT '及时性得分',
    consistency_score DECIMAL(5,2) COMMENT '一致性得分',
    overall_score DECIMAL(5,2) COMMENT '综合得分',
    problem_desc TEXT COMMENT '问题描述',
    improvement_suggest TEXT COMMENT '改进建议',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (catalog_id) REFERENCES data_catalog(catalog_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据质量检查表';

-- ============================================
-- 插入测试数据
-- ============================================

-- 插入部门数据
INSERT INTO department (dept_name, dept_code, parent_id, dept_level, dept_leader, contact_phone, office_address, dept_function) VALUES
('泰安市大数据局', 'TABDJ', 0, 1, '张建国', '0538-8331234', '山东省泰安市泰山区东岳大街1号', '负责全市政务信息化建设、大数据发展应用和管理工作'),
('办公室', 'TABDJ-BGS', 1, 2, '李明华', '0538-8331235', '泰山区东岳大街1号208室', '负责机关日常运转、文秘、档案等工作'),
('规划发展科', 'TABDJ-GHFZK', 1, 2, '王淑英', '0538-8331236', '泰山区东岳大街1号308室', '负责大数据发展规划、政策制定等工作'),
('数据资源科', 'TABDJ-SJZYK', 1, 2, '刘建军', '0538-8331237', '泰山区东岳大街1号408室', '负责政务数据资源管理、共享开放等工作'),
('信息化建设科', 'TABDJ-XXHJSK', 1, 2, '陈晓东', '0538-8331238', '泰山区东岳大街1号508室', '负责政务信息化项目建设管理等工作'),
('网络安全科', 'TABDJ-WLAQK', 1, 2, '赵卫国', '0538-8331239', '泰山区东岳大街1号608室', '负责网络安全保障、信息安全管理等工作'),
('政务服务数据管理中心', 'TABDJ-ZWFWSJGLZX', 1, 2, '孙玉梅', '0538-8331240', '泰山区东岳大街1号708室', '负责政务服务数据归集、分析应用等工作');

-- 插入员工数据
INSERT INTO employee (emp_name, emp_code, dept_id, position, job_title, gender, phone, email, education, entry_date, employment_type) VALUES
('张建国', 'E001', 1, '局长', '正处级', '男', '13905381001', 'zhangjg@taian.gov.cn', '研究生', '2018-03-01', '在编'),
('李明华', 'E002', 2, '主任', '副处级', '男', '13905381002', 'limh@taian.gov.cn', '本科', '2015-06-15', '在编'),
('王淑英', 'E003', 3, '科长', '正科级', '女', '13905381003', 'wangsy@taian.gov.cn', '研究生', '2016-09-01', '在编'),
('刘建军', 'E004', 4, '科长', '正科级', '男', '13905381004', 'liujj@taian.gov.cn', '本科', '2017-03-15', '在编'),
('陈晓东', 'E005', 5, '科长', '正科级', '男', '13905381005', 'chenxd@taian.gov.cn', '研究生', '2016-11-20', '在编'),
('赵卫国', 'E006', 6, '科长', '正科级', '男', '13905381006', 'zhaowg@taian.gov.cn', '本科', '2015-08-10', '在编'),
('孙玉梅', 'E007', 7, '主任', '副处级', '女', '13905381007', 'sunym@taian.gov.cn', '研究生', '2017-05-01', '在编'),
('马志强', 'E008', 2, '副主任', '副科级', '男', '13905381008', 'mazq@taian.gov.cn', '本科', '2018-07-01', '在编'),
('周丽娟', 'E009', 3, '副科长', '副科级', '女', '13905381009', 'zhoulj@taian.gov.cn', '本科', '2019-03-15', '在编'),
('吴建设', 'E010', 4, '副科长', '副科级', '男', '13905381010', 'wujs@taian.gov.cn', '本科', '2019-06-01', '在编'),
('郑雪梅', 'E011', 5, '副科长', '副科级', '女', '13905381011', 'zhengxm@taian.gov.cn', '研究生', '2020-01-10', '在编'),
('黄国强', 'E012', 6, '副科长', '副科级', '男', '13905381012', 'huanggq@taian.gov.cn', '本科', '2019-09-01', '在编'),
('林芳芳', 'E013', 7, '副主任', '副科级', '女', '13905381013', 'linff@taian.gov.cn', '研究生', '2020-03-01', '在编'),
('何建华', 'E014', 3, '工程师', '中级', '男', '13905381014', 'hejh@taian.gov.cn', '本科', '2020-07-01', '聘用'),
('许文静', 'E015', 4, '工程师', '中级', '女', '13905381015', 'xuwj@taian.gov.cn', '本科', '2021-03-01', '聘用'),
('杨帆', 'E016', 5, '工程师', '中级', '男', '13905381016', 'yangf@taian.gov.cn', '研究生', '2021-06-15', '聘用'),
('田雨', 'E017', 6, '工程师', '中级', '女', '13905381017', 'tiany@taian.gov.cn', '本科', '2021-09-01', '聘用'),
('范小军', 'E018', 7, '助理工程师', '初级', '男', '13905381018', 'fanxj@taian.gov.cn', '本科', '2022-07-01', '聘用');

-- 插入项目数据
INSERT INTO project (project_name, project_code, project_type, budget, actual_cost, responsible_dept_id, project_manager, contractor, start_date, end_date, project_status, project_desc) VALUES
('泰安市政务云平台建设项目', 'PRJ2023001', '新建', 2500.00, 2450.00, 5, '陈晓东', '山东浪潮云信息技术有限公司', '2023-01-15', '2023-12-31', '已完成', '建设全市统一的政务云平台,为各部门提供云计算资源服务'),
('泰安市政务数据共享交换平台升级改造项目', 'PRJ2023002', '升级改造', 800.00, 780.00, 4, '刘建军', '北京东方通科技股份有限公司', '2023-03-01', '2023-11-30', '已完成', '升级改造现有数据共享交换平台,提升数据交换效率和安全性'),
('泰安市一体化政务服务平台建设项目', 'PRJ2024001', '新建', 1800.00, 1250.00, 7, '孙玉梅', '华为技术有限公司', '2024-01-10', '2024-12-31', '实施中', '建设全市一体化政务服务平台,实现政务服务"一网通办"'),
('泰安市智慧城市运行管理中心项目', 'PRJ2024002', '新建', 3200.00, 1800.00, 5, '陈晓东', '阿里云计算有限公司', '2024-04-01', '2025-06-30', '实施中', '建设城市运行管理中心,实现城市运行"一网统管"'),
('泰安市电子政务外网升级项目', 'PRJ2024003', '升级改造', 600.00, 350.00, 6, '赵卫国', '中国电信股份有限公司泰安分公司', '2024-05-15', '2024-12-31', '实施中', '升级电子政务外网带宽和安全设备'),
('泰安市大数据中心机房改造项目', 'PRJ2024004', '升级改造', 450.00, 0.00, 5, '陈晓东', '中国建筑第八工程局有限公司', '2024-10-01', '2025-03-31', '立项', '改造升级大数据中心机房基础设施'),
('泰安市公共数据开放平台建设项目', 'PRJ2024005', '新建', 500.00, 0.00, 4, '刘建军', '待定', '2024-11-01', '2025-08-31', '立项', '建设公共数据开放平台,推动政务数据向社会开放');

-- 插入数据资源目录
INSERT INTO data_catalog (catalog_name, catalog_code, data_provider_dept_id, data_type, data_format, update_frequency, data_volume, open_level, security_level, catalog_desc) VALUES
('泰安市人口基础信息库', 'DC001', 4, '基础数据', '结构化', '实时', 5680000, '不公开', '机密', '全市常住人口、流动人口基础信息'),
('泰安市法人单位信息库', 'DC002', 4, '基础数据', '结构化', '每日', 125000, '有条件公开', '内部', '全市法人单位和其他组织统一社会信用代码信息'),
('泰安市电子证照库', 'DC003', 7, '主题数据', '半结构化', '实时', 3200000, '不公开', '内部', '各类电子证照信息'),
('泰安市不动产登记信息', 'DC004', 4, '部门数据', '结构化', '实时', 1850000, '不公开', '机密', '不动产登记、交易等信息'),
('泰安市医保参保信息', 'DC005', 4, '部门数据', '结构化', '每日', 4820000, '不公开', '机密', '基本医疗保险参保人员信息'),
('泰安市社保缴纳信息', 'DC006', 4, '部门数据', '结构化', '每日', 3950000, '不公开', '机密', '社会保险缴纳记录信息'),
('泰安市企业年报信息', 'DC007', 4, '部门数据', '结构化', '每年', 98000, '公开', '公开', '市场主体年度报告信息'),
('泰安市行政许可信息', 'DC008', 7, '部门数据', '结构化', '每日', 256000, '有条件公开', '内部', '各类行政许可审批信息'),
('泰安市行政处罚信息', 'DC009', 7, '部门数据', '结构化', '每日', 45000, '公开', '公开', '行政处罚决定信息'),
('泰安市信用信息库', 'DC010', 4, '主题数据', '结构化', '每日', 680000, '有条件公开', '内部', '企业和个人信用信息'),
('泰安市空间地理信息', 'DC011', 4, '基础数据', '非结构化', '每月', 15000, '有条件公开', '内部', '地理信息、遥感影像等空间数据'),
('泰安市旅游资源信息', 'DC012', 4, '部门数据', '结构化', '每周', 8500, '公开', '公开', '泰安市旅游景点、酒店、旅行社等信息');

-- 插入数据共享申请
INSERT INTO data_share_request (request_no, catalog_id, applicant_dept_id, applicant_name, applicant_phone, apply_reason, use_purpose, approve_status, approver, approve_date, approve_opinion) VALUES
('SH202401001', 2, 7, '林芳芳', '13905381013', '政务服务事项办理需要核验法人信息', '用于企业开办、变更等事项的在线核验', '已通过', '刘建军', '2024-01-15 10:30:00', '同意共享,注意数据安全'),
('SH202402002', 3, 7, '孙玉梅', '13905381007', '政务服务需要调用电子证照', '实现电子证照在线核验和使用', '已通过', '刘建军', '2024-02-20 14:20:00', '同意共享'),
('SH202403003', 8, 5, '陈晓东', '13905381005', '智慧城市项目需要行政许可数据', '用于城市运行态势分析', '已通过', '刘建军', '2024-03-10 09:15:00', '同意共享,用于分析统计'),
('SH202404004', 5, 7, '林芳芳', '13905381013', '社保缴纳证明在线开具需要', '用于参保证明、缴费记录查询打印', '已通过', '刘建军', '2024-04-05 11:00:00', '同意共享相关信息'),
('SH202405005', 4, 7, '孙玉梅', '13905381007', '不动产查询服务需要', '提供不动产登记信息查询服务', '已通过', '刘建军', '2024-05-12 15:40:00', '同意共享,严格控制查询权限'),
('SH202406006', 12, 5, '陈晓东', '13905381005', '智慧城市旅游模块建设需要', '用于旅游大数据分析和展示', '已通过', '刘建军', '2024-06-18 10:25:00', '同意共享'),
('SH202407007', 10, 7, '林芳芳', '13905381013', '政务服务诚信评价需要', '建立政务服务诚信评价机制', '待审批', NULL, NULL, NULL),
('SH202408008', 1, 5, '郑雪梅', '13905381011', '城市人口分析需要人口数据', '用于城市运行人口态势分析', '已驳回', '刘建军', '2024-08-10 09:30:00', '人口数据涉及个人隐私,不予共享');

-- 插入政务服务事项
INSERT INTO government_service (service_name, service_code, service_type, responsible_dept_id, service_object, apply_condition, required_materials, handling_process, promise_days, charge_standard, online_handling, one_time_handling) VALUES
('企业名称预先核准', 'GS001', '行政许可', 7, '企业', '拟设立企业', '1.企业名称预先核准申请书\n2.全体股东身份证明', '1.在线填写申请表\n2.提交申请材料\n3.系统自动核名\n4.领取核准通知书', 1, '免费', 1, 1),
('个体工商户注册登记', 'GS002', '行政许可', 7, '个人', '具有经营能力的公民', '1.个体工商户开业登记申请书\n2.经营者身份证\n3.经营场所证明', '1.网上申报\n2.材料审核\n3.发放营业执照', 3, '免费', 1, 1),
('社会保障卡申领', 'GS003', '公共服务', 7, '个人', '本市户籍或参保人员', '1.身份证原件\n2.一寸白底彩色照片', '1.在线申请\n2.信息审核\n3.制卡\n4.邮寄或网点领取', 15, '免费', 1, 0),
('医保电子凭证申领', 'GS004', '公共服务', 7, '个人', '医保参保人员', '1.实名认证\n2.医保参保信息', '1.手机APP申请\n2.人脸识别认证\n3.即时领取', 0, '免费', 1, 1),
('不动产权证书补办', 'GS005', '行政确认', 7, '个人、企业', '不动产权利人,证书遗失或损毁', '1.补发申请书\n2.身份证明\n3.遗失声明\n4.原不动产权证书复印件', '1.提交申请\n2.公告\n3.审核\n4.发证', 10, '按规定收费', 1, 0),
('住房公积金提取', 'GS006', '公共服务', 7, '个人', '缴存公积金职工,符合提取条件', '1.提取申请表\n2.身份证\n3.提取证明材料(购房合同、租房合同等)', '1.在线申请\n2.材料审核\n3.审批\n4.资金划拨', 5, '免费', 1, 0),
('企业社保缴费证明打印', 'GS007', '公共服务', 7, '企业', '已参保缴费的企业', '1.企业统一社会信用代码\n2.经办人身份证', '1.在线查询\n2.打印证明', 0, '免费', 1, 1),
('税务登记证明开具', 'GS008', '公共服务', 7, '企业、个人', '已办理税务登记的纳税人', '1.统一社会信用代码或身份证\n2.授权委托书(非本人办理)', '1.在线申请\n2.信息核验\n3.电子证明开具', 1, '免费', 1, 1),
('无犯罪记录证明开具', 'GS009', '公共服务', 7, '个人', '本市户籍或长期居住人员', '1.身份证原件\n2.申请表\n3.用途说明', '1.网点申请\n2.公安部门核查\n3.出具证明', 7, '免费', 0, 0),
('出生医学证明补办', 'GS010', '行政确认', 7, '个人', '出生医学证明遗失者', '1.补办申请\n2.父母身份证\n3.户口本\n4.遗失声明', '1.提交申请\n2.医院核实\n3.补发证明', 15, '按规定收费', 1, 0);

-- 插入系统运维记录
INSERT INTO system_maintenance (system_name, maintenance_type, maintenance_date, start_time, end_time, responsible_person, maintenance_content, problem_desc, solution, result, remark) VALUES
('泰安市政务云平台', '日常巡检', '2024-11-01', '09:00:00', '11:00:00', '杨帆', '检查云平台各项服务运行状态、资源使用情况', '无', '无', '正常', '系统运行正常,资源使用率在合理范围内'),
('政务数据共享交换平台', '日常巡检', '2024-11-01', '14:00:00', '15:30:00', '许文静', '检查数据交换任务执行情况、接口调用状态', '部分接口响应时间较长', '优化数据库查询语句,增加缓存', '正常', '已完成优化'),
('一体化政务服务平台', '故障处理', '2024-11-05', '16:30:00', '18:45:00', '杨帆', '处理用户登录异常问题', '部分用户无法登录系统', '重启认证服务,清理异常会话', '正常', '问题已解决'),
('电子政务外网', '安全加固', '2024-11-08', '22:00:00', '23:30:00', '田雨', '安装安全补丁,升级防火墙策略', '无', '按照安全加固方案执行', '正常', '系统安全性得到提升'),
('泰安市政务云平台', '数据备份', '2024-11-10', '02:00:00', '04:30:00', '杨帆', '完成每周全量数据备份', '无', '无', '正常', '备份文件已存储至异地机房'),
('智慧城市运行管理平台', '系统升级', '2024-11-12', '20:00:00', '23:00:00', '郑雪梅', '升级系统至2.5版本,新增AI分析功能', '升级过程中出现数据迁移报错', '排查后发现字段类型不匹配,修改迁移脚本重新执行', '正常', '升级成功,新功能运行正常'),
('政务服务网上大厅', '日常巡检', '2024-11-15', '10:00:00', '11:30:00', '范小军', '检查网上大厅各功能模块运行状态', '无', '无', '正常', '访问量正常,系统稳定'),
('公共数据开放平台', '日常巡检', '2024-11-18', '15:00:00', '16:00:00', '许文静', '检查数据更新情况和平台访问日志', '发现部分数据未按时更新', '联系相关部门尽快更新数据', '待处理', '已通知相关部门'),
('电子证照系统', '故障处理', '2024-11-20', '14:20:00', '15:40:00', '杨帆', '处理证照生成服务异常', '证照生成失败,提示模板加载错误', '重新上传证照模板,重启生成服务', '正常', '问题已修复'),
('泰安市政务云平台', '日常巡检', '2024-11-22', '09:00:00', '11:00:00', '郑雪梅', '检查云平台各项服务运行状态', '无', '无', '正常', '系统运行平稳');

-- 插入数据质量检查记录
INSERT INTO data_quality_check (catalog_id, check_date, check_person, completeness_score, accuracy_score, timeliness_score, consistency_score, overall_score, problem_desc, improvement_suggest) VALUES
(1, '2024-10-15', '许文静', 98.50, 99.20, 99.80, 98.90, 99.10, '部分人员联系方式缺失', '加强数据采集,完善人口信息'),
(2, '2024-10-15', '许文静', 99.80, 99.50, 99.90, 99.70, 99.73, '数据质量良好', '保持数据更新频率'),
(3, '2024-10-20', '何建华', 95.30, 98.80, 96.50, 97.20, 96.95, '部分历史证照未完成电子化', '加快历史证照电子化进度'),
(4, '2024-10-22', '许文静', 99.60, 99.80, 99.95, 99.40, 99.69, '数据质量优秀', '继续保持'),
(5, '2024-10-25', '何建华', 98.20, 99.10, 98.50, 98.80, 98.65, '少量参保人员通讯地址不准确', '建议通过多渠道验证更新地址信息'),
(6, '2024-10-25', '何建华', 99.10, 98.90, 99.30, 99.00, 99.08, '整体数据质量较高', '无'),
(7, '2024-10-28', '许文静', 97.80, 98.50, 95.60, 98.20, 97.53, '部分企业年报数据更新不及时', '督促企业按时报送年报'),
(8, '2024-11-05', '何建华', 98.90, 99.40, 99.70, 99.20, 99.30, '数据质量优良', '无'),
(9, '2024-11-05', '何建华', 99.50, 99.30, 99.80, 99.60, 99.55, '数据质量优秀', '继续保持'),
(10, '2024-11-08', '许文静', 96.50, 97.80, 98.20, 97.60, 97.53, '部分企业信用信息待补充', '加强与相关部门的数据共享'),
(11, '2024-11-12', '何建华', 94.20, 96.50, 92.80, 95.30, 94.70, '部分空间数据更新滞后', '增加遥感数据采集频次'),
(12, '2024-11-15', '许文静', 98.60, 98.20, 97.50, 98.40, 98.18, '个别景点信息需要更新', '建立旅游信息动态更新机制');

-- ============================================
-- 创建视图 - 便于数据查询
-- ============================================

-- 部门员工统计视图
CREATE OR REPLACE VIEW v_dept_employee_stat AS
SELECT 
    d.dept_id,
    d.dept_name,
    d.dept_code,
    d.dept_leader,
    COUNT(e.emp_id) as employee_count,
    SUM(CASE WHEN e.employment_type = '在编' THEN 1 ELSE 0 END) as bianzhi_count,
    SUM(CASE WHEN e.employment_type = '聘用' THEN 1 ELSE 0 END) as pinyong_count
FROM department d
LEFT JOIN employee e ON d.dept_id = e.dept_id AND e.status = 1
WHERE d.status = 1
GROUP BY d.dept_id, d.dept_name, d.dept_code, d.dept_leader;

-- 项目进度统计视图
CREATE OR REPLACE VIEW v_project_stat AS
SELECT 
    project_status,
    COUNT(*) as project_count,
    SUM(budget) as total_budget,
    SUM(actual_cost) as total_cost,
    ROUND(AVG((actual_cost/budget)*100), 2) as avg_cost_rate
FROM project
GROUP BY project_status;

-- 数据共享申请统计视图
CREATE OR REPLACE VIEW v_data_share_stat AS
SELECT 
    d.dept_name as applicant_dept,
    COUNT(*) as total_requests,
    SUM(CASE WHEN dsr.approve_status = '已通过' THEN 1 ELSE 0 END) as approved_count,
    SUM(CASE WHEN dsr.approve_status = '待审批' THEN 1 ELSE 0 END) as pending_count,
    SUM(CASE WHEN dsr.approve_status = '已驳回' THEN 1 ELSE 0 END) as rejected_count
FROM data_share_request dsr
LEFT JOIN department d ON dsr.applicant_dept_id = d.dept_id
GROUP BY d.dept_name;

-- ============================================
-- 创建索引优化查询性能
-- ============================================

CREATE INDEX idx_employee_dept ON employee(dept_id);
CREATE INDEX idx_project_status ON project(project_status);
CREATE INDEX idx_project_dept ON project(responsible_dept_id);
CREATE INDEX idx_catalog_dept ON data_catalog(data_provider_dept_id);
CREATE INDEX idx_share_catalog ON data_share_request(catalog_id);
CREATE INDEX idx_share_dept ON data_share_request(applicant_dept_id);
CREATE INDEX idx_share_status ON data_share_request(approve_status);
CREATE INDEX idx_service_dept ON government_service(responsible_dept_id);
CREATE INDEX idx_maintenance_date ON system_maintenance(maintenance_date);
CREATE INDEX idx_quality_catalog ON data_quality_check(catalog_id);
CREATE INDEX idx_quality_date ON data_quality_check(check_date);

-- ============================================
-- 数据统计查询示例
-- ============================================

-- 1. 查询各部门人员统计
-- SELECT * FROM v_dept_employee_stat;

-- 2. 查询项目进度统计
-- SELECT * FROM v_project_stat;

-- 3. 查询数据共享申请统计
-- SELECT * FROM v_data_share_stat;

-- 4. 查询本月系统运维情况
-- SELECT 
--     system_name,
--     COUNT(*) as maintenance_count,
--     SUM(CASE WHEN result = '正常' THEN 1 ELSE 0 END) as normal_count
-- FROM system_maintenance
-- WHERE DATE_FORMAT(maintenance_date, '%Y-%m') = DATE_FORMAT(CURDATE(), '%Y-%m')
-- GROUP BY system_name;

-- 5. 查询数据质量得分情况
-- SELECT 
--     dc.catalog_name,
--     dqc.check_date,
--     dqc.overall_score,
--     dqc.problem_desc
-- FROM data_quality_check dqc
-- JOIN data_catalog dc ON dqc.catalog_id = dc.catalog_id
-- WHERE dqc.overall_score < 98
-- ORDER BY dqc.overall_score;

-- ============================================
-- 脚本执行完成
-- ============================================
SELECT '数据库创建完成!' as message;
SELECT '共创建8个数据表,插入测试数据若干' as info;
SELECT '数据库名称: taian_bigdata' as db_name;