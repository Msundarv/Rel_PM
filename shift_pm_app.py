import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from calendar import monthrange
import matplotlib.pyplot as plt
from io import BytesIO
from lifelines import WeibullFitter


def print_about():
    """
    Print the app background and assumptions
    """

    about_txt = """ 
    <p>This Streamlit app helps to analyse the effect of different preventive maintenance intervals on reliability metrics. 
    Consider many assets of the same type deployed at various times.  
    We can determine the failure distribution of the asset class 
    and use the same to determine the effect of various preventive maintenance intervals. 
    We are focusing on the first failure here while selecting the failure distribution 
    since our assumption is that the asset will be as good as new whenever there is a work order because of a failure. </p> 
    <p>Our current focus is on Weibull distribution. 
    Weibull distribution is widely used in reliability and life data analysis due to its versatility. 
    Depending on the values of the parameters, the Weibull distribution can be used to model a variety of life behaviors. 
    An important aspect of the Weibull distribution is how the values of the shape parameter, 
    and the scale parameter, affect such distribution characteristics as the shape of the pdf curve, and the failure rate.</p>
    <p> For more info about this Streamlit app, 
    Please visit <a href="https://github.com/Msundarv/Rel_PM#readme">this</a> page. 
    <br> Author: <a href="https://github.com/Msundarv">msundarv</a> </p>
    """

    about_expander = st.expander(label="About", expanded=False)
    with about_expander:
        st.markdown(about_txt, unsafe_allow_html=True)

    return None


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
    st_col1.markdown("<br>", unsafe_allow_html=True)
    st_col1.text("Shape: " + "{:.2f}".format(wbf.rho_))
    st_col1.text("Scale: " + "{:.2f}".format(wbf.lambda_))
    st_col2.image(fig_2_buf)
    st_col3.image(fig_1_buf)

    return wbf


def get_fpmh_by_intervals(wbf, intervals=range(1, 46)):
    """
    Calc. FPMH for different time interval using the given weibull fitter object
    """

    # Every month is considered to have 30 days
    monthly_hrs = 30 * 24

    # Get interval length in terms of hours
    interval_lengths = [i * monthly_hrs for i in intervals]

    # FPMH by interval
    fpmh_intervals = wbf.cumulative_hazard_at_times(interval_lengths)
    fpmh_intervals = (fpmh_intervals.values * 1e6) / interval_lengths
    fpmh_intervals = pd.DataFrame(fpmh_intervals, index=intervals, columns=["FPMH"])

    # Plot Interval FPMH
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 4))
    fpmh_intervals.plot.bar(
        ax=ax, xlabel="PM Interval (No. of months)", ylabel="Exp. FPMH"
    )
    ax.set_ylim(
        ((fpmh_intervals.min() * 0.8).values[0], (fpmh_intervals.max() * 1.2).values[0])
    )
    fig.suptitle("FPMH vs PM Interval Length")
    fig.tight_layout()
    fig_buf = BytesIO()
    fig.savefig(fig_buf, format="png")

    st_col1, st_col2, st_col3 = st.columns([1, 8, 1])
    st_col1.text("")
    st_col2.image(fig_buf)
    st_col3.text("")

    return None


# Config Streamlit
st.set_page_config(page_title="Rel PM", layout="wide")
st.title("Reliability Based Preventive Maintenance")
print_about()
st.markdown("---")

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
        wbf = fit_weibull(wo_df)
        st.markdown("---")

        # Calc. FPMH for different PM Intervals
        st.subheader("Plan Preventive Maintenance")
        get_fpmh_by_intervals(wbf, range(1, 24))
        st.markdown("---")

    except ValueError:
        st.error("Please upload a valid WO XLSX file")

else:
    st.text("Work order data not yet uploaded")
