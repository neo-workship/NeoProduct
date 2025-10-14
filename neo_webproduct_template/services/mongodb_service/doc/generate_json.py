def generate_hierarchy_structure_json(self, file_path: str, 
                                      output_path: str = "./hierarchy_structure.json",
                                      sheet_name: Optional[str] = None) -> Dict[str, Any]:
    """
    基于read_excel_with_merged_cells改造的函数，专门用于生成层级结构JSON数据
    
    Args:
        file_path: Excel文件路径
        output_path: 输出JSON文件路径
        sheet_name: 工作表名称，默认为None（第一个工作表）
    
    Returns:
        Dict[str, Any]: 层级结构数据
    """
    from pathlib import Path
    import json
    
    # 使用openpyxl读取Excel文件以处理合并单元格
    workbook = load_workbook(file_path)
    if sheet_name is None:
        worksheet = workbook.active
    else:
        worksheet = workbook[sheet_name]
        
    # 获取所有数据
    data = []
    for row in worksheet.iter_rows(values_only=True):
        data.append(list(row))
        
    # 处理合并单元格 - 填充合并单元格的值
    merged_ranges = worksheet.merged_cells.ranges
    for merged_range in merged_ranges:
        merge_value = worksheet[merged_range.coord.split(':')[0]].value 
        for row_idx in range(merged_range.min_row - 1, merged_range.max_row):
            for col_idx in range(merged_range.min_col - 1, merged_range.max_col):
                if row_idx < len(data) and col_idx < len(data[row_idx]):
                    data[row_idx][col_idx] = merge_value
    
    # 初始化层级结构数据
    hierarchy_structure = {
        "l1_categories": [],
        "metadata": {
            "total_l1": 0,
            "total_l2": 0,
            "total_l3": 0,
            "total_fields": 0,
            "generated_time": datetime.now().isoformat(),
            "version": "1.0",
            "source_file": file_path
        }
    }
    
    # 用于构建层级结构的字典和跟踪变量
    l1_dict = {}  # l1_code -> l1_data
    l2_dict = {}  # l2_code -> l2_data  
    l3_dict = {}  # l3_code -> l3_data
    
    current_l1 = {"name": "", "code": ""}
    current_l2 = {"name": "", "code": ""}
    current_l3 = {"name": "", "code": ""}
    
    l1_order = 0
    l2_order = 0
    l3_order = 0
    field_count = 0
    
    # 从第2行开始处理数据（第1行是标题）
    for row_idx, row_data in enumerate(data[1:], start=2):
        if len(row_data) < 5:
            continue
            
        # 提取各级分类数据
        level1 = row_data[1] if row_data[1] is not None else ""
        level2 = row_data[2] if row_data[2] is not None else ""
        level3 = row_data[3] if row_data[3] is not None else ""
        field_name = row_data[4] if row_data[4] is not None else ""
        remark = row_data[5] if len(row_data) > 5 and row_data[5] is not None else ""
        data_url = row_data[6] if len(row_data) > 6 and row_data[6] is not None else ""
        
        # 跳过空行
        if not any([level1, level2, level3, field_name]):
            continue
        
        # 处理一级分类
        if level1 and level1 != current_l1["name"]:
            l1_order += 1
            l2_order = 0
            l3_order = 0
            current_l1 = {
                "name": level1,
                "code": self.generate_code(level1, "l1")
            }
            
            if current_l1["code"] not in l1_dict:
                l1_data = {
                    "l1_code": current_l1["code"],
                    "l1_name": current_l1["name"],
                    "l1_order": l1_order,
                    "l2_categories": []
                }
                l1_dict[current_l1["code"]] = l1_data
                hierarchy_structure["l1_categories"].append(l1_data)
        
        # 处理二级分类
        if level2 and level2 != current_l2["name"]:
            l2_order += 1
            l3_order = 0
            current_l2 = {
                "name": level2,
                "code": self.generate_code(level2, "l2", current_l1["code"])
            }
            
            if current_l2["code"] not in l2_dict:
                l2_data = {
                    "l2_code": current_l2["code"],
                    "l2_name": current_l2["name"],
                    "l2_order": l2_order,
                    "l3_categories": [],
                    # 保留路径信息
                    "parent_l1_code": current_l1["code"],
                    "parent_l1_name": current_l1["name"],
                    "path_code": current_l1["code"],
                    "path_name": current_l1["name"]
                }
                l2_dict[current_l2["code"]] = l2_data
                l1_dict[current_l1["code"]]["l2_categories"].append(l2_data)
        
        # 处理三级分类
        if level3 and level3 != current_l3["name"]:
            l3_order += 1
            current_l3 = {
                "name": level3,
                "code": self.generate_code(level3, "l3", current_l2["code"])
            }
            
            if current_l3["code"] not in l3_dict:
                path_code = f"{current_l1['code']}.{current_l2['code']}"
                path_name = f"{current_l1['name']}.{current_l2['name']}"
                
                l3_data = {
                    "l3_code": current_l3["code"],
                    "l3_name": current_l3["name"],
                    "l3_order": l3_order,
                    "fields": [],
                    # 保留路径信息
                    "parent_l2_code": current_l2["code"],
                    "parent_l2_name": current_l2["name"],
                    "parent_l1_code": current_l1["code"],
                    "parent_l1_name": current_l1["name"],
                    "path_code": path_code,
                    "path_name": path_name
                }
                l3_dict[current_l3["code"]] = l3_data
                l2_dict[current_l2["code"]]["l3_categories"].append(l3_data)
        
        # 处理字段
        if field_name:
            field_count += 1
            field_code = self.generate_code(field_name, "field", current_l3["code"])
            
            path_code = f"{current_l1['code']}.{current_l2['code']}.{current_l3['code']}"
            path_name = f"{current_l1['name']}.{current_l2['name']}.{current_l3['name']}"
            full_path_code = f"{path_code}.{field_code}"
            full_path_name = f"{path_name}.{field_name}"
            
            field_data = {
                "field_code": field_code,
                "field_name": field_name,
                "field_order": field_count,
                "field_type": self._infer_field_type(field_name),
                "is_required": self._is_required_field(field_name, remark),
                "remark": remark,
                "data_source": self._extract_data_source(remark),
                "data_url": data_url,
                # 保留完整路径信息
                "parent_l3_code": current_l3["code"],
                "parent_l3_name": current_l3["name"],
                "parent_l2_code": current_l2["code"],
                "parent_l2_name": current_l2["name"],
                "parent_l1_code": current_l1["code"],
                "parent_l1_name": current_l1["name"],
                "path_code": path_code,
                "path_name": path_name,
                "full_path_code": full_path_code,
                "full_path_name": full_path_name
            }
            l3_dict[current_l3["code"]]["fields"].append(field_data)
    
    # 更新统计信息
    hierarchy_structure["metadata"]["total_l1"] = len(l1_dict)
    hierarchy_structure["metadata"]["total_l2"] = len(l2_dict)
    hierarchy_structure["metadata"]["total_l3"] = len(l3_dict)
    hierarchy_structure["metadata"]["total_fields"] = field_count
    
    # 保存JSON文件
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(hierarchy_structure, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 层级结构JSON文件已生成: {output_path}")
    print(f"📊 统计信息:")
    print(f"   - 一级分类: {hierarchy_structure['metadata']['total_l1']} 个")
    print(f"   - 二级分类: {hierarchy_structure['metadata']['total_l2']} 个") 
    print(f"   - 三级分类: {hierarchy_structure['metadata']['total_l3']} 个")
    print(f"   - 字段总数: {hierarchy_structure['metadata']['total_fields']} 个")
    
    return hierarchy_structure


# 便捷调用函数
def create_hierarchy_json(excel_file: str = "./一企一档数据项.xlsx", 
                         json_file: str = "./hierarchy_structure.json") -> Dict[str, Any]:
    """
    便捷函数：生成层级结构JSON文件
    
    Args:
        excel_file: Excel文件路径
        json_file: 输出JSON文件路径
    
    Returns:
        Dict[str, Any]: 层级结构数据
    """
    generator = FlatEnterpriseArchiveGenerator()
    return generator.generate_hierarchy_structure_json(excel_file, json_file)