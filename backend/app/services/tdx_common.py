"""TDX 各資料集共用的小工具（避免公車／捷運／停車場各自重複實作）。"""

# 台北市 + 新北市：大台北生活圈的公車、停車場都要合併這兩個 City 一起查
CITIES = ["Taipei", "NewTaipei"]


def zh_text(field: dict | None) -> str:
    """TDX 的多語欄位取繁中值；欄位缺漏或大小寫不一致時回空字串，不讓整支 API 掛掉。"""
    if not field:
        return ""
    return field.get("Zh_tw") or field.get("Zh_TW") or ""
