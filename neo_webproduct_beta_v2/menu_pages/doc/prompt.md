## API 编写

### /api/v1/documents

在 \services\mongodb*service\main.py 中添加一个 API：
1、API 参数：字符串 enterprise_code 企业代码 ； 字符串 full_path_code 字段路径 ；字典 dict_fileds ，其包括 4 个键值对：
value ： value 值（不能为空）,
value_pic_url: http://get_pic*{enterprise*code}*{full*path_code }/pic（此默认值，可为空）
value_doc_url：http://get_pic*{enterprise*code}*{full*path_code }/doc （此默认值，可为空）
value_video_url: http://get_pic*{enterprise*code}*{full_path_code }/video （此默认值，可为空）

2、接收参数后，API 的逻辑为通过 enterprise_code 和 full_path_code 找到 mongodb 的子文档，然后将值 dict_fields 中的值分别**插入或更新**到文档中的 value 、value_pic_url、value_doc_url、value_video_url 的字段。

3、请编写高效、稳定的 API，并充分复用包中的已有功能，如\services\mongodb_service\mongodb_manager.py。 由于其他逻辑可复用，**只要编写 API 对应的数据模型和 API 路由函数**。

### /api/v1/enterprises/search

在 \services\mongodb_service\main.py 中添加一个 API：

1、API 参数：字符串 enterprise_text 企业代码
2、接收参数后，API 的逻辑为通过 enterprise_text 模糊查找 mongodb 的子文档，对 enterprise_code 与 enterprise_name 进行模糊匹配。然后返回检索的文档中的 enterprise_code、enterprise_name
3、请编写高效、稳定的 API，并充分复用包中的已有功能，如\services\mongodb_service\mongodb_manager.py。 由于其他逻辑可复用，**只要编写 API 对应的数据模型和 API 路由函数**。

### query_fields

在 \services\mongodb_service\main.py 中添加一个 API: /api/v1/enterprises/query_fields：
1、API 参数：字符串 enterprise_code 企业代码 ； 字符串 path_code_param 层级路径代码 ； 列表 fields_param 字段列表

2、接收参数后，使用 enterprise_code 查询对应的企业。如果 fields_param 为空，API 的逻辑为：使用 path_code_param 匹配文档 fields 数组中的 path_code 字段， 匹配出所有文档，然后获取以下字段的值： value、value_pic_url、value_doc_url、value_video_url、data_url、encoding、format、license、rights、update_frequency、value_dict 。然后返回数据

3、接收参数后，使用 enterprise_code 查询对应的企业。如果 fields_param 不为空，API 的逻辑为:用 path_code_param 匹配文档 fields 数组中的 path_code 字段，并且要求匹配字段 field_code in fields_param 的文档，然后获取以下字段的值：value、value_pic_url、value_doc_url、value_video_url、data_url、encoding、format、license、rights、update_frequency、value_dict。然后返回数据

4、请编写高效、稳定的 API，并充分复用包中的已有功能，如\services\mongodb_service\mongodb_manager.py。 由于其他逻辑可复用，**只要编写 API 对应的数据模型和 API 路由函数**，数据模型编写在\services\mongodb_service\schemas.py 中

## UI 编写

编写 \menu_pages\enterprise_archive\read_archive_tab.py read_archive_content 函数代码，

伪代码如下，请按照布局及注释说明进行实现，不要私自添加其他布局和组件。

```py
# 不要使用ui.card组件
from .hierarchy_selector_component import HierarchySelector
from common.exception_handler import log_info, log_error, safe_protect

with ui.column():
    with column():
        # search_input 和 search_select的宽度比例为1：4
        with row():
            # 搜索输入：search_input
            # 按下回车键，调用\services\mongodb_service\main.py 中的API:/api/v1/enterprises/search

            search_input = ui.input().on("keydown.enter")

            # 下拉列表：search_select
            # 使用API返回值，可查看\services\mongodb_service\schemas.py明确返回的数据模型；
            # 列表中展示API返回数据 enterprise_code+enterprise_name ，实际要使用的是enterprise_code
            search_select = ui.select()

        # hierarchy_selector组件展示
        hierarchy_selector = HierarchySelector(multiple=True)
        hierarchy_selector.render_row()
```
