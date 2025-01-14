import pandas as pd


def read_crash(directory):
    dates = ['CRASH_DATE_AND_TIME', 'REPORT_DATE_AND_TIME', 'NOTIFIED_TIME', 'DISPATCHED_TIME', 'ARRIVED_TIME',
                 'CLEARED_TIME']
    crash = pd.read_csv(directory + r'\crash_event.csv', parse_dates=dates)
    return crash

def read_driver(directory):
    driver = pd.read_csv(directory + r'\driver.csv')
    return driver

def read_vehicle(directory):
    vehicle = pd.read_csv(directory + r'\vehicle.csv')
    return vehicle

def read_passenger(directory):
    passenger = pd.read_csv(directory + r'\passenger.csv')
    return passenger

def read_non_motorist(directory):
    non_motorist = pd.read_csv(directory + r'\non_motorist.csv')
    return non_motorist

def read_violation(directory):
    violation = pd.read_csv(directory + r'\violation.csv')
    return violation


def impaired_driver(x):
    return x[(x.BLOOD_ALCOHOL_CONTENT > 0) | (x.DRUG_TEST_RESULTS == 'Positive') | (x.SUSPECTED_DRUG_USE_CODE == 'Y') | ( x.SUSPECTED_ALCOHOL_USE_CODE == 'Y') | (x.ALCOHOL_TESTED_CODE == 'Test Refused') | (x.DRUG_TESTED_CODE == 'Test Refused')]

def alcohol_driver(x):
    df = x[(x.BLOOD_ALCOHOL_CONTENT > 0) | (x.SUSPECTED_ALCOHOL_USE_CODE == 'Y') | ( x.ALCOHOL_TESTED_CODE == 'Test Refused')]
    return df

def drug_driver(x):
    return x[(x.DRUG_TEST_RESULTS == 'Positive') | (x.SUSPECTED_DRUG_USE_CODE == 'Y') | ( x.DRUG_TESTED_CODE == 'Test Refused')]

def add_alcohol_col(x):
    df = x[(x.BLOOD_ALCOHOL_CONTENT > 0) | (x.SUSPECTED_ALCOHOL_USE_CODE == 'Y') | ( x.ALCOHOL_TESTED_CODE == 'Test Refused')]
    df['alcohol'] = 1 
    col_list = list(x.columns)
    merged = x.merge(df, on = col_list, how='left')
    merged.alcohol.fillna(0, inplace=True)
    return merged

def add_drug_col(x):
    df = x[(x.DRUG_TEST_RESULTS == 'Positive') | (x.SUSPECTED_DRUG_USE_CODE == 'Y') | ( x.DRUG_TESTED_CODE == 'Test Refused')]
    df['drug'] = 1 
    col_list = list(x.columns)
    merged = x.merge(df, on = col_list, how='left')
    merged.drug.fillna(0, inplace=True)
    return merged

def add_impair_col(x):
    df = x[(x.BLOOD_ALCOHOL_CONTENT > 0) | (x.DRUG_TEST_RESULTS == 'Positive') | (x.SUSPECTED_DRUG_USE_CODE == 'Y') | ( x.SUSPECTED_ALCOHOL_USE_CODE == 'Y') | (x.ALCOHOL_TESTED_CODE == 'Test Refused') | (x.DRUG_TESTED_CODE == 'Test Refused')]
    df['impair'] = 1 
    col_list = list(x.columns)
    merged = x.merge(df, on = col_list, how='left')
    merged.impair.fillna(0, inplace=True)
    return merged

