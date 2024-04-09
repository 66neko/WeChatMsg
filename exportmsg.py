import csv
import os,json

from app.DataBase import hard_link_db
from app.util.image import get_image_ex, get_image
from app.util.exporter.exporter import ExporterBase, escape_js_and_html
from app.person import Me
from app.config import INFO_FILE_PATH

def load_data(flag=True):
        if os.path.exists(INFO_FILE_PATH):
            with open(INFO_FILE_PATH, 'r', encoding='utf-8') as f:
                dic = json.loads(f.read())
                wxid = dic.get('wxid')
                if wxid:
                    me = Me()
                    me.wxid = dic.get('wxid')
                    me.name = dic.get('name')
                    me.nickName = dic.get('name')
                    me.remark = dic.get('name')
                    me.mobile = dic.get('mobile')
                    me.wx_dir = dic.get('wx_dir')
                    me.token = dic.get('token')
        else:
            pass

def traverse_csv_file(csv_file_path):
    with open(csv_file_path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        data = list(reader)
        for row in data:
            if len(row) >= 3 and row[2] == '3':
                #如果消息类型是图片
                str_content = row[7]
                #str_content = escape_js_and_html(str_content)
                BytesExtra = bytes()
                print("#################\n",str_content,"#####################\n")
                image_path = hard_link_db.get_image_original(str_content, BytesExtra)
                print(image_path)
                if image_path is None:
                    image_path = hard_link_db.get_image_thumb(str_content, BytesExtra)
                    print("缩略图获取 = ",image_path)
                base_path = os.path.join("./data/", 'img')
                image_path = get_image_ex(image_path, base_path=base_path)
                print("output= ", image_path)
                if len(row) >= 13:
                    row[12] = image_path
                else:
                    row.append(image_path)
                pass
    # 将修改后的内容写回到 CSV 文件中
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(data)


def split_csv_by_column(csv_file):
    # 读取 CSV 文件
    with open(csv_file, 'r',encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)  # 读取标题行
        col_num = 10  # 第11列对应的索引号（0-based）

        # 创建一个字典，用于保存每个不同值的行
        rows_by_value = {}

        # 根据第五列的值将行分组
        for row in reader:
            value = row[col_num]  # 获取第五列的值
            if value not in rows_by_value:
                rows_by_value[value] = []
            rows_by_value[value].append(row)

    # 创建目录保存分割后的文件
    output_dir = os.path.splitext(csv_file)[0] + "_split"
    os.makedirs(output_dir, exist_ok=True)

    # 根据不同的值创建文件并写入行
    for value, rows in rows_by_value.items():
        output_file = os.path.join(output_dir, f"{value}.csv")
        with open(output_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(header)  # 写入标题行
            writer.writerows(rows)  # 写入相应值的行

    print("CSV 文件已分割完毕！")


if __name__ == "__main__":
    csv_file_path = "data/messages.csv"  # 替换为你的 CSV 文件路径
    traverse_csv_file(csv_file_path)
    split_csv_by_column(csv_file_path)
