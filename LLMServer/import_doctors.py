import os
import django
import pandas as pd

import aiserver

# 设置 Django 环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aiserver.settings")  # 修改为你的项目名
django.setup()

from doctors.models import Doctors  # ✅ 绝对导入

def import_doctors_from_csv(csv_file):
    # 读取 CSV
    df = pd.read_csv(csv_file)

    doctors = []
    for _, row in df.iterrows():
        doctor = Doctors(
            image=row.get("image", ""),
            name=row.get("name", ""),
            department=row.get("department", None),
            rank=row.get("rank", None),
            ifo=row.get("ifo", None),
            advantage=row.get("advantage", None),
        )
        doctors.append(doctor)

    # 批量写入数据库
    Doctors.objects.bulk_create(doctors, batch_size=1000)
    print(f"成功导入 {len(doctors)} 条医生信息！")

if __name__ == "__main__":
    csv_path = "datas/doctor3.csv"  # 修改为你的 csv 文件路径
    import_doctors_from_csv(csv_path)
