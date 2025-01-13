from re import Pattern


def regex_match_dict(
    pattern: Pattern[str],
    text: str,
) -> dict[str, str] | None:
    match_result = pattern.match(text)
    if match_result:
        return match_result.groupdict()
    else:
        return None


# clickhouse insert
def insert_to_clickhouse(clickhouse, table: str, data: list, column: list):
    try:
        clickhouse.insert(table, data, column_names=column)
        return f"Insert adb clickhouse. table: {table}"
    except Exception as e:
        raise f"Failed insert to clickhouse -> {e}, table: {table}, column: {column}, data: {data}"
