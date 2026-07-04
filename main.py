import os
import pandas as pd


def main():
    packages_dir = "/home/anas/Dev/playground/pandas/product_upload/packages"

    subdirs = sorted(
        d
        for d in os.listdir(packages_dir)
        if os.path.isdir(os.path.join(packages_dir, d))
    )

    for subdir in subdirs:
        file_path = os.path.join(packages_dir, subdir, "file.xlsx")

        if not os.path.exists(file_path):
            continue

        try:
            sheets = pd.read_excel(file_path, sheet_name=None, engine="openpyxl")
            changed = False

            if "cosmetics" in sheets:
                df = sheets["cosmetics"]

                if "Ingredients" not in df.columns and "Ingredients (INCI) *" in df.columns:
                    if "Seller SKU" in df.columns:
                        seller_idx = df.columns.get_loc("Seller SKU")
                        df.insert(seller_idx, "Ingredients", df["Ingredients (INCI) *"])
                    else:
                        df["Ingredients"] = df["Ingredients (INCI) *"]

                    sheets["cosmetics"] = df
                    changed = True

            if changed:
                with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
                    for sheet_name, s_df in sheets.items():
                        s_df.to_excel(writer, sheet_name=sheet_name, index=False)

                print(f"  {subdir}: Added Ingredients to cosmetics")

        except Exception as e:
            print(f"  {subdir}: Error: {e}")

    print("\nDone.")


if __name__ == "__main__":
    main()
