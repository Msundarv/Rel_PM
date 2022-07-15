# Reliability Based Preventive Maintenance

<p> Rel_PM is a data app developed using Streamlit that helps to analyse the effect of different preventive maintenance intervals on reliability metrics. Consider many assets of the same type deployed at various times. We can determine the failure distribution of the asset class and use the same to determine the effect of various preventive maintenance intervals. We are focusing on the first failure here while selecting the failure distribution since we assume that the asset will become as good as new whenever there is a work order. Thus the current implementation uses <a href="https://www.weibull.com/hotwire/issue14/relbasics14.htm">Weibull distribution</a>.</p>

<p>The present asset hierarchy assumption is that a system consists of multiple subsystems, and every subsystem has many asset classes. For example, an asset class name 'SIG/ATC/OBU' will denote 'SIG' as the system name and 'ATC' as the subsystem name for the asset class 'OBU'. All our analyses are at asset class level.</p>

Link to the app: https://share.streamlit.io/msundarv/rel_pm/main/shift_pm_app.py

To run the app locally:
```
streamlit run shift_pm_app.py
```

## Prerequisites

Requires Python 3.x.

List of libraries required is [here](https://github.com/Msundarv/Rel_PM/blob/main/requirements.txt).

## Input Data

Before trying the app, you need to have the work order data. You can either use [this](https://github.com/Msundarv/Rel_PM/blob/main/Generate_WO_Data.ipynb) notebook to generate some dummy work order data or use the generated [dummy work order data](https://github.com/Msundarv/Rel_PM/blob/main/dummy_wo.xlsx) from the same notebook.

## Authors

- [Sundar V](http://msundarv.com/)


