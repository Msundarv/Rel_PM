import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from calendar import monthrange
import matplotlib.pyplot as plt
from io import BytesIO
from lifelines import WeibullFitter


def load_data(file):
    """
    Load input work order data excel file
    """
    instll_date_df = pd.read_excel(file, sheet_name="sheet0", engine="openpyxl")
    wo_df = pd.read_excel(file, sheet_name="sheet1", engine="openpyxl")

    ip_data_expander = st.expander(label="Uploaded Input Data", expanded=True)
    with ip_data_expander:
        st_col1, st_col2 = st.columns(2)
        st_col2.text("Uploaded Installation Details")
        st_col2.dataframe(instll_date_df)
        st_col1.text("Uploaded Work Order Details")
        st_col1.dataframe(wo_df)

    return wo_df, instll_date_df


def attach_ttf(wo_df, instll_date_df):
    """
    Calc. ttf for work orders
    """
    res_dfs = []
    grouped_wo = wo_df.groupby(["asset_num"])
    for asset, asset_wo in grouped_wo:
        # Get the installation date from previous work order by default
        asset_wo = asset_wo.sort_values(by="wo_date", ascending=True)
        asset_wo["instll_date"] = asset_wo["wo_date"].shift(1)
        # Get the installation date for the first work order
        initial_instll_date = list(
            instll_date_df[instll_date_df["asset_num"] == asset]["instll_date"]
        )[0]
        asset_wo.loc[
            asset_wo["instll_date"].isna(), "instll_date"
        ] = initial_instll_date
        # Get ttf
        asset_wo["ttf"] = (
            (asset_wo["wo_date"] - asset_wo["instll_date"]).dt.total_seconds() / 60 / 60
        )
        res_dfs.append(asset_wo)

    res_df = pd.concat(res_dfs, ignore_index=True)

    # Keep only work orders with ttf > 1 day
    res_df = res_df[res_df["ttf"] > 24]

    return res_df


def get_hist_dates(start_date):
    """
    Create a range of dates from start date's month till current month
    """
    start_hist = datetime(
        start_date.year,
        start_date.month,
        monthrange(start_date.year, start_date.month)[1],
    )
    end_hist = datetime(
        datetime.now().year,
        datetime.now().month,
        monthrange(datetime.now().year, datetime.now().month)[1],
    )
    historical_dates = pd.date_range(start=start_hist, end=end_hist, freq="M")

    return historical_dates


# TODO: Function to get FPMH based on historical dates
def get_fpmh(wo_df):
    """
    Calc. historical FPMH from work order data
    """
    hist_dates = get_hist_dates(wo_df["instll_date"].min())
    # print(hist_dates)

    return None


def get_discretized_fpmh(ttf_lt, n_bins=50):
    """
    Calc. historical FPMH from ttf data
    """
    fcount, bins = np.histogram(ttf_lt, bins=n_bins)
    bin_end = bins[1:]
    fpmh = 1e6 * fcount.cumsum() / bin_end
    fpmh = pd.Series(fpmh, index=bin_end)
    return fpmh


def plot_hist_data(ttf_lt, hist_fpmh):
    """
    Plot historical ttf, fpmh data
    """
    fig = plt.figure()
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(12, 4))

    # Plot TTF
    ax1.hist(ttf_lt, bins=25)
    ax1.set_xlabel("Time (hrs)")
    ax1.set_ylabel("No. of failures")
    ax1.title.set_text("TTF Histogram")

    # Plot FPMH
    hist_fpmh.plot(ax=ax2)
    ax2.ticklabel_format(axis="y", scilimits=(1, 3))
    ax2.set_xlabel("Time (hrs)")
    ax2.set_ylabel("FPMH")
    ax2.title.set_text("Failure Rate")

    fig.tight_layout()

    fig_buf = BytesIO()
    fig.savefig(fig_buf, format="png")
    st_col1, st_col2, st_col3 = st.columns([1, 6, 1])
    st_col1.text("")
    st_col2.image(fig_buf)
    st_col3.text("")

    return None


def fit_weibull(wo_df):
    """
    Fit Weibull distribution to the work order data
    """
    wo_df["indicator"] = 1

    wbf = WeibullFitter()
    wbf.fit(wo_df["ttf"], wo_df["indicator"])
    # wbf.print_summary()
    # print(wbf.lambda_, wbf.rho_)

    # Plot cdf function
    fig = plt.figure(figsize=(6, 4))
    wbf.plot_cumulative_density()
    fig.suptitle("Cumulative Density Function")
    fig_1_buf = BytesIO()
    fig.savefig(fig_1_buf, format="png")

    # Plot pdf function
    fig = plt.figure(figsize=(6, 4))
    wbf.plot_density()
    fig.suptitle("Density Function")
    fig_2_buf = BytesIO()
    fig.savefig(fig_2_buf, format="png")

    st_col1, st_col2, st_col3 = st.columns([1, 3, 3])
    st_col1.text("Shape: " + "{:.2f}".format(wbf.rho_))
    st_col1.text("Scale: " + "{:.2f}".format(wbf.lambda_))
    st_col2.image(fig_2_buf)
    st_col3.image(fig_1_buf)

    return wbf


# Config Streamlit
st.set_page_config(page_title="Shift PM", layout="wide")
st.title("Reliability Based Preventive Maintenance")
st.subheader("Upload Work Order Data")

uploaded_file = st.file_uploader("Choose a WO XLSX file", type="xlsx")
if uploaded_file:

    try:
        # Load work order data
        wo_df, instll_date_df = load_data(uploaded_file)
        st.markdown("---")

        # Get ttf data
        wo_df = attach_ttf(wo_df, instll_date_df)
        ttf_lt = list(wo_df["ttf"])
        # st.dataframe(wo_df)

        # Get FPMH data
        # hist_fpmh = get_fpmh(wo_df)
        hist_fpmh = get_discretized_fpmh(ttf_lt)
        # st.dataframe(hist_fpmh)

        # Plot hist. metrics
        st.subheader("Historical Reliability Metrics")
        plot_hist_data(ttf_lt, hist_fpmh)
        st.markdown("---")

        # Fit Weibull Distribution
        st.subheader("Fitted Weibull Distribution")
        fit_weibull(wo_df)
        st.markdown("---")

    except ValueError:
        st.error("Please upload a valid WO XLSX file")

else:
    st.text("Work order data not yet uploaded")
