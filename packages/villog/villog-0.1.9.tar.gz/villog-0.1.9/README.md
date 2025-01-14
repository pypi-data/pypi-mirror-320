# Villog is a simple python utility tool for your everyday projects.

## Modules
### Logger
```
from villog import Logger

l: Logger = Logger(
    file_path = "test.log",
    encoding = "utf-8-sig",
    time_format = "%Y.%m.%d %H:%M:%S",
    separator = "\t",
    silent = False,
    enable_remove = False,
    strip_content = False
)

l.log(
    content = "test"
)
```

### Writexcel
```
from villog.writexcel import WorkSheet, WorkBook

sheet_1: WorkSheet = WorkSheet(
    name = "Sheet1",
    header = ["header_1", "header_2", "header_3"],
    data = [
        ["data_1", "data_2", "data_3"],
        ["data_4", "data_5", "data_6"]
    ]
)

sheet_2: WorkSheet = WorkSheet(
    name = "Sheet2",
    header = ["header_1", "header_2", "header_3"],
    data = [
        ["data_1", "data_2", "data_3"],
        ["data_4", "data_5", "data_6"]
    ]
)

book: WorkBook = WorkBook(
    name = "Book1",
    sheets = [sheet_1, sheet_2]
)

book.xlsx_create(
    file_path = "test.xlsx"
)
```

### MsSQL
tba

### pdf
tba

## Install
With **pip**:
```
pip install villog
```