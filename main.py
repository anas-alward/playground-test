import os
import pandas as pd


def main():
    # Iterate through folders in packages
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
                # Read the excel file
                df = pd.read_excel(file_path)

                # Create barcode column from ID column
                id_col = next(
                    (col for col in df.columns if str(col).strip().lower() == "id"),
                    None,
                )

                if id_col:
                    df["barcode"] = df[id_col]
                    print("  Created barcode column from ID")
                else:
                    print("  ID column not found, barcode column not created")

                # Write back to the same path
                df.to_excel(file_path, sheet_name="Drugs", index=False)

                print(f"  Successfully updated {file_path}")

            except Exception as e:
                print(f"  Error processing {file_path}: {e}")


if __name__ == "__main__":
    main()
