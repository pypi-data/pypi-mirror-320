import pytest
import os
from ToolBox import DataFrameWrapper, InterpolateWrapper
from classifications import classifications
import helpers
import math
import numpy as np 

## DATAFRAME TESTS

def test_different_datasets():
    # Initialize and process datasets
    bank_data = DataFrameWrapper.DataFrameWrapperStr("bank.csv", "bank_out.csv")
    bank_data.load_and_read_file()
    bank_data.get_info()

    ibm_data = DataFrameWrapper.DataFrameWrapperStr("IBM.csv", "IBM_out.csv")
    ibm_data.load_and_read_file()
    ibm_data.get_info()

    ecom_data = DataFrameWrapper.DataFrameWrapperStr("ecom.csv", "ecom_out.csv")
    ecom_data.load_and_read_file()
    ecom_data.get_info()

    # Check if the expected files were created
    assert os.path.isfile("bank.csv_info.txt"), "bank.csv_info.txt was not created."
    assert os.path.isfile("IBM.csv_info.txt"), "IBM.csv_info.txt was not created."
    assert os.path.isfile("ecom.csv_info.txt"), "ecom.csv_info.txt was not created."

@pytest.fixture
def dfw():
    dfw= DataFrameWrapper.DataFrameWrapperInt("r.csv", "o.csv")
    dfw.load_and_read_file()
    return dfw 
def test_common_stats(dfw):
    mean = dfw.mean("Discount")
    sd = dfw.standard_deviation("Discount")
    median = dfw.median("Discount")
    correlation = dfw.correlation("Discount", "Profit")
    frequency_count =  dfw.frequency_count("Discount")
    
    assert frequency_count == { 0.8: 3, 0: 65, 0.6: 1, 0.15: 2, 0.7: 6, 0.5: 1, 0.4: 1, 0.2: 20, 0.1: 1 }
    assert pytest.approx(mean, rel=1e-2)== 0.125
    assert pytest.approx(sd, rel = 1e-2) == 0.222985
    assert median == 0
    assert pytest.approx(correlation, rel =  1e-2) == -0.327707

def test_get_col_index(dfw):
    columnName1 = "Discount"; # index = 4
    columnName2 = "Profit"; # index = 6
    discountIndex = dfw.get_col_index(columnName1);
    profitIndex = dfw.get_col_index(columnName2);

    assert discountIndex == 4;
    assert profitIndex == 6;
def test_get_col_by_index(dfw):
    with pytest.raises(IndexError, match="Invalid range: column index is out of bounds"):
        dfw.columns_by_index(10)  # Assuming 10 is an invalid index

    # assert dfw.columns_by_index(10) == 
def test_get_columns_by_entry(dfw):
    with pytest.raises(IndexError, match="Invalid range: column or row index is out of bounds"):
        dfw.columns_by_entry(10, 1)  # Assuming 10 is an invalid index


def test_get_columns_by_slice(dfw):
    slice = dfw.columns_by_slice(4, 1, 4)
    assert len(slice) == 4
    assert slice[0] == 0.80
    with pytest.raises(IndexError, match="Invalid slice range: start or stop index is out of bounds"):
        dfw.columns_by_slice(4, 1, 102)  # Assuming 10 is an invalid index

def test_custom_visitor(dfw):
    mean_profit = dfw.mean("Profit")
    profits = dfw.columns_by_name("Profit")

    categories = ["Below Mean", "Above Mean"]

    # Define classification conditions as lambda functions //TODO: modify as c++ doesn;t like python lambda functions
    def below_mean(value):
       return value < mean_profit
    def above_mean(value):
       return value >= mean_profit


    conditions = [
           below_mean,
           above_mean
    ]

    test_classifications = dfw.classify("Profit", categories, conditions)
    assert test_classifications == classifications

## INTERPOLATION TESTS

# Test function
f = lambda i: 1 / math.atan(1 + (i * i))

# Parameters
t = 2           # Interpolation point
n = 8           # Number of points
lb = -4         # Lower bound
ub = 4          # Upper bound
tolerance = 0.5

x_casual = helpers.casual_vec(n, lb, ub)
x_equid = helpers.fill_x_equid(n, lb, ub)
x_cheby = helpers.fill_x_Cheby(n, lb, ub)

@pytest.fixture
def lin():
    linear_interpolator = InterpolateWrapper.LinearInterpolator()
    return linear_interpolator 
@pytest.fixture
def lagrange():
    lagrange_interpolator = InterpolateWrapper.LagrangeInterpolator()
    return lagrange_interpolator 
@pytest.fixture
def spline():
    spline_interpolator = InterpolateWrapper.SplineInterpolator()
    return spline_interpolator 
def test_linear_interpolator(lin):
    # Define the test function
    f = lambda i: 1 / np.arctan(1 + (i * i))

    y = [f(x) for x in x_casual]

    # Build the interpolating polynomial
    lin.build(x_casual, y, len(y), lb, ub)  # Adjust method signature as necessary

    # Interpolate the value at point t
    result = lin(t)

    # Print debug information
    print(f"Function value on {t}: {f(t)} --- Interpolated value on {t}: {result} --- ERROR ON {t}: {abs(result - f(t))}")

    # Evaluate the maximum error
    max_error = lin.error(f, lb, ub)  # Replace `error` with your actual method name
    print(f"Max Error: {max_error}")

    # Assert that the interpolated value is within the tolerance
    assert np.isclose(f(t), result, atol=tolerance), f"Interpolated value {result} deviates too much from {f(t)}"
def test_lagrange_interpolator(lagrange):
    # Define the test function
    f = lambda i: 1 / np.arctan(1 + (i * i))

    y = [f(x) for x in x_equid]

    # Build the interpolating polynomial
    lagrange.build(x_casual, y, len(y), lb, ub)  # Adjust method signature as necessary

    # Interpolate the value at point t
    result = lagrange(t)

    # Print debug information
    print(f"Function value on {t}: {f(t)} --- Interpolated value on {t}: {result} --- ERROR ON {t}: {abs(result - f(t))}")

    # Evaluate the maximum error
    max_error = lagrange.error(f, lb, ub)  # Replace `error` with your actual method name
    print(f"Max Error: {max_error}")

    # Assert that the interpolated value is within the tolerance
    assert np.isclose(f(t), result, atol=tolerance), f"Interpolated value {result} deviates too much from {f(t)}"
def test_spline_interpolator(spline):
    # Define the test function
    f = lambda i: 1 / np.arctan(1 + (i * i))

    y = [f(x) for x in x_equid]

    # Build the interpolating polynomial
    spline.build(x_equid, y, len(y), lb, ub)  # Adjust method signature as necessary

    # Interpolate the value at point t
    result = spline(t)

    # Print debug information
    print(f"Function value on {t}: {f(t)} --- Interpolated value on {t}: {result} --- ERROR ON {t}: {abs(result - f(t))}")

    # Evaluate the maximum error
    max_error = spline.error(f, lb, ub)  # Replace `error` with your actual method name
    print(f"Max Error: {max_error}")

    # Assert that the interpolated value is within the tolerance
    assert np.isclose(f(t), result, atol=tolerance), f"Interpolated value {result} deviates too much from {f(t)}"
 




