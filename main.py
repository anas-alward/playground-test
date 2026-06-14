import os
import uuid

import pandas as pd


def generate_seller_sku():
    return f"SKU-{uuid.uuid4().hex[:12].upper()}"


def main():
    packages_dir = "/home/anas/Dev/playground/pandas/product_upload/packages"

    subdirs = sorted(
        [
            d
            for d in os.listdir(packages_dir)
            if os.path.isdir(os.path.join(packages_dir, d))
        ]
    )

    for subdir in subdirs:
        file_path = os.path.join(packages_dir, subdir, "file.xlsx")

        if os.path.exists(file_path):
            print(f"Processing {file_path}...")

            try:
                # Read all sheets
                sheets = pd.read_excel(
                    file_path,
                    sheet_name=None,
                )

                for sheet_name, df in sheets.items():
                    sheets[sheet_name] = df.loc[:, ~df.columns.str.contains(r"^Unnamed")]

                                # Add Seller SKU column to drugs sheet
                    
                # Write workbook back
                with pd.ExcelWriter(
                    file_path,
                    engine="openpyxl",
                ) as writer:
                    for sheet_name, df in sheets.items():
                        df.to_excel(
                            writer,
                            sheet_name=sheet_name,
                            index=False,
                        )

                print("  Done")

            except Exception as e:
                print(f"  Error processing {file_path}: {e}")


if __name__ == "__main__":
    main()
