# Reliability Based Preventive Maintenance

<p> Rel_PM is a data app developed using Streamlit that helps to analyse the effect of different preventive maintenance intervals on reliability metrics. Consider many assets of the same type deployed at various times.We can determine the failure distribution of the asset class and use the same to determine the effect of various preventive maintenance intervals. We are focusing on the first failure here while selecting the failure distribution since our assumption is that the asset will be as good as new whenever there is a work order because of a failure. </p> 

<p> Our current focus is on Weibull distribution. Weibull distribution is widely used in reliability and life data analysis due to its versatility. Depending on the values of the parameters, the Weibull distribution can be used to model a variety of life behaviors. An important aspect of the Weibull distribution is how the values of the shape parameter, and the scale parameter, affect such distribution characteristics as the shape of the pdf curve, and the failure rate.</p>

Link to the app: https://share.streamlit.io/msundarv/rel_pm/main/shift_pm_app.py

## Prerequisites

Requires Python 3.x.

List of libraries required is [here](https://github.com/Msundarv/Rel_PM/blob/main/requirements.txt).

## Input Data

Before trying the app, you need to have the work order data. You can either use [this](https://github.com/Msundarv/Rel_PM/blob/main/Generate_WO_Data.ipynb) notebook to generate some dummy work order data or use the generated [dummy work order data](https://github.com/Msundarv/Rel_PM/blob/main/dummy_wo.xlsx) from the same notebook.

## Authors

- [Sundar V](http://msundarv.com/)


