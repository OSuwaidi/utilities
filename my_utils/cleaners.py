import re
from unicodedata import normalize


def replace_values(name: str, mapping: dict[str, str]) -> str:
    """Replace string values in the column name.

    Parameters
    ----------
    name
        Column name.
    mapping
        Maps old values in the column name to the new values.
    """

    for old_value, new_value in mapping.items():
        # If the old value or the new value is not alphanumeric, add underscores to the
        # beginning and end so the new value will be parsed correctly for convert_case()
        new_val = rf"{new_value}" if old_value.isalnum() and new_value.isalnum() else rf"_{new_value}_"
        name = re.sub(rf"{old_value}", new_val, name, flags=re.IGNORECASE)

    return name


def _remove_accents(name: str) -> str:
    """Return the normal form for a Unicode string name using canonical decomposition."""
    return normalize("NFD", name).encode("ascii", "ignore").decode("ascii")


def _split_strip_string(string: str) -> list[str]:
    """Split the string into separate words and strip punctuation."""
    string = re.sub(r"[!()*+,\-./:;<=>?[\]^_{|}~]", " ", string)
    string = re.sub(r"[\'\"`]", "", string)

    return re.sub(r"([A-Z][a-z]+)", r" \1", re.sub(r"([A-Z]+|[0-9]+|\W+)", r" \1", string)).split()


def convert_case(name: str, case: str) -> str:
    """Convert case style of a column name.

    Args:
        name (str): Column name.
        case (str): Preferred case type, e.g. snake or camel.

    Returns:
        Any: name with case converted.
    """

    words = _split_strip_string(str(name))

    if case == "snake":
        name = "_".join(words).lower()
    elif case == "kebab":
        name = "-".join(words).lower()
    elif case == "camel":
        name = words[0].lower() + "".join(w.capitalize() for w in words[1:])
    elif case == "pascal":
        name = "".join(w.capitalize() for w in words)
    elif case == "const":
        name = "_".join(words).upper()

    return name


def rename_duplicates(names: list, case: str) -> list:
    """Rename duplicated column names to append a number at the end."""
    if case in {"snake", "const"}:
        sep = "_"
    elif case in {"camel", "pascal"}:
        sep = ""
    else:
        sep = "-"

    counts: dict[str, int] = {}

    for i, col in enumerate(names):
        cur_count = counts.get(col, 0)
        if cur_count > 0:
            names[i] = f"{col}{sep}{cur_count}"
        counts[col] = cur_count + 1

    return names


def clean_columns(
    arr: list[str, ...] | tuple[str, ...],
    case: str = "snake",
    replace: dict[str, str] | None = None,
    remove_accents: bool = True,
) -> list[str, ...] | tuple[str, ...]:
    """Clean column names from a given list.

    Args:
        arr (list[str, ...] or tuple[str, ...], required): The array of string(s) to be cleaned
        case (str, optional): The desired case style of the column name. Defaults to "snake".

                - 'snake': 'column_name'
                - 'kebab': 'column-name'
                - 'camel': 'columnName'
                - 'pascal': 'ColumnName'
                - 'const': 'COLUMN_NAME'

        replace (Dict[str, str], optional): Values (parts) to replace from the column names. Defaults to None.

                - {'old_value': 'new_value'}

        remove_accents (bool, optional): If True, strip accents from the column names. Defaults to True.
    """

    if replace:
        arr = [replace_values(ele, replace) for ele in arr]

    if remove_accents:
        arr = [_remove_accents(ele) for ele in arr]

    arr = [convert_case(ele, case) for ele in arr]

    return rename_duplicates(arr, case)
