# Encrypt & Decrypt SpreadSheets

Python code สำหรับเข้ารหัสและถอดรหัสข้อมูลใน Google sheets มีวิธีใช้งานดังนี้
- ระบุ key ที่จะใช้เข้ารหัส
- ระบุ path และชื่อไฟล์ที่ต้องการให้เก็บ key โดยมีสกุลไฟล์เป็น .json
- ระบุว่าเลือกที่จะ encrypt หรือ decrypt ข้อมูล
- แนบ path ที่เก็บ service account ของเรา
- แนบลิงค์ Google sheets ที่ต้องการเข้ารหัส
- ระบุชื่อ sheets ที่ต้องการเข้ารหัส
- ระบุชื่อ columns โดยสามารถใส่ได้หลาย columns โดยต้องอยู่ในรูปแบบ ColumnName1,ColumnName2,Columnname3 (เขียนชื่อคั่นด้วยลูกน้ำติดกันโดยไม่ต้องเว้นวรรค)

Argument  | Description
:--:|------------------
-k, --key | ระบุ key ที่จะใช้เข้ารหัส
-p, --path_key | ระบุ path และชื่อไฟล์ที่ต้องการให้เก็บ key โดยมีสกุลไฟล์เป็น .json
-en, --encrypt | กำหนดเป็น True ถ้าต้องการ encrypt
-de, --decrypt | กำหนดเป็น True ถ้าต้องการ decrypt
-sv, --service_account | ใส่ path ที่เก็บ service account 
-gsp, --gpread_url | แนบลิงค์ Google sheets ที่ต้องการเข้ารหัส
-shn, --sheet_name | ระบุชื่อ sheets ที่ต้องการเข้ารหัส


## Example
รันโปรแกรมใน CMD

```
python cryptsheets.py ^
-k K@iPumpM@rk ^
-p <your key's path> ^
--encrypt ^
-sv <your service account> ^
-gsp <your Google sheets link> ^
```

