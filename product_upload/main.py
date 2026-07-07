import logging
import pandas as pd
from pathlib import Path
from functools import wraps
from typing import Callable, Any

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

BASE = Path(__file__).resolve().parent / "packages"
FOLDERS = list(range(1, 67))
SHEET_NAMES = {"drugs": "Drugs", "devices": "devices", "cosmetics": "cosmetics"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def normalize_cols(df: pd.DataFrame) -> dict[str, str]:
    """Return {lowercase_name: actual_column_name} for all columns in df."""
    return {c.lower().strip(): c for c in df.columns}


def col_lookup(df: pd.DataFrame, *candidates: str) -> str | None:
    """Find a column by trying multiple case-insensitive names."""
    lookup = normalize_cols(df)
    for cand in candidates:
        key = cand.lower().strip()
        if key in lookup:
            return lookup[key]
    return None


def is_empty(v) -> bool:
    """Check if a value is null, empty string, or placeholder."""
    if pd.isna(v):
        return True
    s = str(v).strip()
    return s in ("", "_", "-", "None", "nan", "0")


def ensure_str_column(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Convert a column to string if it's numeric (e.g. all-NaN float64)."""
    if df[col].dtype in ("float64", "int64"):
        df = df.copy()
        df[col] = df[col].astype(object)
    return df


def all_sheets(dfs: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    return dfs


def drugs_only(dfs: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    return {k: v for k, v in dfs.items() if k == SHEET_NAMES["drugs"]}


def devices_only(dfs: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    return {k: v for k, v in dfs.items() if k == SHEET_NAMES["devices"]}


def cosmetics_only(dfs: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    return {k: v for k, v in dfs.items() if k == SHEET_NAMES["cosmetics"]}


def load_one(folder: int) -> dict[str, pd.DataFrame] | None:
    path = BASE / str(folder) / "file.xlsx"
    try:
        sheets = pd.read_excel(path, sheet_name=None, engine="openpyxl")
    except Exception:
        log.warning("Skipping folder %s - file is corrupt or unreadable", folder)
        return None
    return {s: sheets[s] for s in sheets}


def save_one(folder: int, dfs: dict[str, pd.DataFrame]) -> None:
    path = BASE / str(folder) / "file.xlsx"
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for name, df in dfs.items():
            df.to_excel(writer, sheet_name=name, index=False)


def apply_to_all(
    operation: Callable[[pd.DataFrame], pd.DataFrame],
    sheet_selector: Callable = all_sheets,
    *,
    dry_run: bool = False,
):
    for folder in FOLDERS:
        dfs = load_one(folder)
        if dfs is None:
            continue
        target_sheets = sheet_selector(dfs)

        for name in target_sheets:
            dfs[name] = operation(dfs[name])

        if dry_run:
            print(f"--- Folder {folder} (dry run) ---")
            for name in target_sheets:
                print(f"  [{name}] {operation.__name__}")
        else:
            save_one(folder, dfs)

    print(f"{'[DRY RUN] ' if dry_run else ''}Applied '{operation.__name__}' to {len(FOLDERS)} folders.")


# ---------------------------------------------------------------------------
# Bulk operations that DON'T need column-name normalization
# (they take exact column names as parameters)
# ---------------------------------------------------------------------------

def rename_column(old: str, new: str, **kwargs):
    def op(df): return df.rename(columns={old: new}) if old in df.columns else df
    op.__name__ = f"rename {old!r} -> {new!r}"
    apply_to_all(op, **kwargs)


def update_column(col: str, value: Any, **kwargs):
    def op(df):
        if col in df.columns:
            df = df.copy()
            df[col] = value
        return df
    op.__name__ = f"set {col!r} = {value!r}"
    apply_to_all(op, **kwargs)


def update_column_where(col: str, value: Any, condition_col: str, condition_val: Any, **kwargs):
    def op(df):
        if col in df.columns and condition_col in df.columns:
            df = df.copy()
            df.loc[df[condition_col] == condition_val, col] = value
        return df
    op.__name__ = f"set {col!r} = {value!r} where {condition_col!r} == {condition_val!r}"
    apply_to_all(op, **kwargs)


def map_column(col: str, mapping: dict, **kwargs):
    def op(df):
        if col in df.columns:
            df = df.copy()
            df[col] = df[col].replace(mapping)
        return df
    op.__name__ = f"map {col!r}"
    apply_to_all(op, **kwargs)


def delete_column(col: str, **kwargs):
    def op(df): return df.drop(columns=[col]) if col in df.columns else df
    op.__name__ = f"delete {col!r}"
    apply_to_all(op, **kwargs)


def add_column(col: str, value: Any, **kwargs):
    def op(df):
        if col not in df.columns:
            df = df.copy()
            df[col] = value
        return df
    op.__name__ = f"add {col!r} = {value!r}"
    apply_to_all(op, **kwargs)


def apply_to_column(col: str, func: Callable, **kwargs):
    def op(df):
        if col in df.columns:
            df = df.copy()
            df[col] = df[col].apply(func)
        return df
    op.__name__ = f"apply func to {col!r}"
    apply_to_all(op, **kwargs)


def strip_all_strings(**kwargs):
    def op(df):
        df = df.copy()
        for c in df.columns:
            if df[c].dtype == object:
                df[c] = df[c].astype(str).str.strip()
        return df
    op.__name__ = "strip all strings"
    apply_to_all(op, **kwargs)


# ---------------------------------------------------------------------------
# Domain-specific bulk operations
# ---------------------------------------------------------------------------

def fill_drug_descriptions(*, dry_run: bool = False):
    """
    Fill empty Description / En * and Description / Ar * in the Drugs sheet
    across ALL folders. Uses product names to generate fake descriptions.
    Handles column-name variants (case differences) and dtype issues
    (float64 columns from all-NaN).
    """

    def op(df: pd.DataFrame) -> pd.DataFrame:
        col_en_name = col_lookup(df, "Name / En", "name")
        col_ar_name = col_lookup(df, "Name / Ar", "name / ar")

        # Resolve description columns exactly as they appear in each file
        lookup = normalize_cols(df)
        col_en_desc = lookup.get("description / en *")
        col_ar_desc = lookup.get("description / ar*")

        if col_en_desc is None and col_ar_desc is None:
            return df

        df = df.copy()

        # Fix dtype: columns that are all-NaN get read as float64
        if col_en_desc:
            df = ensure_str_column(df, col_en_desc)
        if col_ar_desc:
            df = ensure_str_column(df, col_ar_desc)

        for idx in df.index:
            if col_en_desc and is_empty(df.at[idx, col_en_desc]):
                raw_name = df.at[idx, col_en_name] if col_en_name else None
                base = str(raw_name).strip() if not is_empty(raw_name) else "Product"
                df.at[idx, col_en_desc] = f"{base} detailed description."

            if col_ar_desc and is_empty(df.at[idx, col_ar_desc]):
                raw_name = df.at[idx, col_ar_name] if col_ar_name else None
                base = str(raw_name).strip() if not is_empty(raw_name) else "المنتج"
                df.at[idx, col_ar_desc] = f"وصف تفصيلي لـ {base}"

        return df

    op.__name__ = "fill drug descriptions"
    apply_to_all(op, sheet_selector=drugs_only, dry_run=dry_run)
