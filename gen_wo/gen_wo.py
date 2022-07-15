import warnings

warnings.filterwarnings("ignore")

from nbclient import execute
import nbformat
from nbparameterise import extract_parameters, parameter_values, replace_definitions

import pandas as pd
from pandas import ExcelWriter


def save_xls(list_dfs, xls_path):
    # Function to save a list of dataframes as sheets of an excel
    with ExcelWriter(xls_path) as writer:
        for n, df in enumerate(list_dfs):
            df.to_excel(writer, "sheet%s" % n, index=False)
    return None


# Define asset class names
asset_class_lt = ["SIG/ATC/OBU", "SIG/ATC/TRK", "SIG/ATS/CATS", "SIG/ATS/LATS"]

nb = nbformat.read("Generate_AC_WO_Data.ipynb", as_version=4)
orig_paramters = extract_parameters(nb)

for asset_class in asset_class_lt:
    print("Generating WOs for " + asset_class)

    # Update parameter and run the asset class wo gen. notebook
    params = parameter_values(orig_paramters, asset_class=asset_class)
    new_nb = replace_definitions(nb, params)
    execute(new_nb)

# Combine all asset class work order excels into single dataset
print("Combining all asset class work orders")
instll_date_df_lt = []
wo_df_lt = []
for asset_class in asset_class_lt:
    wo_file = "../dataset/dummy_wo-" + asset_class.replace("/", "_") + ".xlsx"
    instll_date_df_lt.append(
        pd.read_excel(wo_file, sheet_name="sheet0", engine="openpyxl")
    )
    wo_df_lt.append(pd.read_excel(wo_file, sheet_name="sheet1", engine="openpyxl"))
save_xls(
    [pd.concat(instll_date_df_lt), pd.concat(wo_df_lt)],
    "../dataset/dummy_wo-v1.xlsx",
)
