import pandas as pd
import re
import streamlit as st
import warnings
from datetime import date

warnings.filterwarnings('ignore')

# Validation functions
def phone_num(phone_number):
    pattern1 = r'05\d{1}-\d{7}$'
    return bool(re.match(pattern1, str(phone_number)))

def tele_num(telephone_number):
    pattern2 = r'\d{1,2}-\d{7}$'
    return bool(re.match(pattern2, str(telephone_number)))

def email(email_id):
    pattern3 = r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'
    return bool(re.match(pattern3, str(email_id)))

def eid(EID):
    pattern4 = r'\d{3}-\d{4}-\d{7}-\d{1}$'
    return bool(re.match(pattern4, str(EID)))

# Color coding function
def color_coding(row):
    completeness_score = float(row['Completeness Score'].rstrip('%'))
    if completeness_score == 0:
        return ['background-color: #ff573d'] * len(row)  # Red
    elif completeness_score >= 96:
        return ['background-color: #aaffaa'] * len(row)  # Light green
    elif completeness_score <= 50:
        return ['background-color: #ffb15e'] * len(row)  # Orange
    return [''] * len(row)

# def summ(df):
#     summary = df.describe(include='all')
#     return summary    

def Quality(df):
    num_records = len(df)

    validation_rules = {
        'Mobile No.': phone_num,
        'Telephone': tele_num,
        'Email ID': email,
        'EID': eid
    }

    invalid_record_counts = {col: 0 for col in validation_rules.keys()}
    null_value_counts = df.isnull().sum()

    available_columns = set(df.columns)

    for column in validation_rules.keys():
        if column in available_columns:
            invalid_records = df[column].dropna().apply(lambda x: not validation_rules[column](str(x)))
            invalid_record_counts[column] = invalid_records.sum()

    total_invalid_records = sum(invalid_record_counts.values())
    validity_score = ((num_records - total_invalid_records) / num_records) * 100
    completeness_score = (1 - (df.isnull().sum() / num_records)) * 100
    total_completeness_score = completeness_score.sum() / len(completeness_score)
    dups = df.duplicated().sum()
    uniqueness_score = (1 - dups / num_records) * 100

    st.write("Invalid Record Count (Without Null Values): ")
    invalid_data = {'Column': [], 'Invalid Records': [], 'Percentage': []}
    for col, count in invalid_record_counts.items():
        if col in available_columns:
            percentage = (count / num_records) * 100

            invalid_data['Column'].append(col)
            invalid_data['Invalid Records'].append(count)
            invalid_data['Percentage'].append("{:.2f}%".format(percentage))

    invalid_df = pd.DataFrame(invalid_data)
    st.dataframe(invalid_df)

    if not invalid_df.empty:
        st.write("Total Validity Score: {:.2f}%".format(validity_score))
    st.write("_______________________________________________")
    st.write("Total Uniqueness Score: {:.2f}%".format(uniqueness_score), "  (", dups, "Duplicate Records)")

    completeness_data = {'Column': [], 'Null Values': [], 'Null Percentage': [], 'Completeness Score': []}
    for col in df.columns:
        null_count = null_value_counts[col]
        null_percentage = (null_count / num_records) * 100
        completeness_score = (1 - (df[col].isnull().sum() / num_records)) * 100

        completeness_data['Column'].append(col)
        completeness_data['Completeness Score'].append("{:.2f}%".format(completeness_score))
        completeness_data['Null Values'].append(null_count)
        completeness_data['Null Percentage'].append("{:.2f}%".format(null_percentage))

    completeness_df = pd.DataFrame(completeness_data)
    completeness_df = completeness_df.style.apply(color_coding, axis=1)

    st.write("_______________________________________________")

    st.dataframe(completeness_df)
    st.write("Total Completeness Score: {:.2f}%".format(total_completeness_score))
    st.write("_______________________________________________")

    today = pd.Timestamp(date.today())  # Convert today to a pandas Timestamp object

    if "Ejari Expiry Date" in df.columns:
        # Filter expired Ejari
        expired_Ejari_df = df[pd.to_datetime(df["Ejari Expiry Date"], errors='coerce') < today]

        if not expired_Ejari_df.empty:
            st.write("Expired Ejari:")
            st.dataframe(expired_Ejari_df)
            ex_ajari_count =  len(expired_Ejari_df['EC Code'])
            ex_ajari_percent = len(expired_Ejari_df['EC Code']) / len(df['EC Code'])
            st.write("Expired Ejari Count: ",ex_ajari_count)
            st.write("Expired Ejari percentage: {:.2f}%".format(ex_ajari_percent))

        else:
            st.write("No Expired Contracts Found.")

    if "Passport Expiry" in df.columns:
        # Filter expired passports
        expired_passports = df[pd.to_datetime(df["Passport Expiry"], errors='coerce') < today]

        if not expired_passports.empty:
            st.write("Expired Passports:")
            st.dataframe(expired_passports)
            ex_pass_count =  len(expired_passports['C Code'])
            ex_pass_percent = len(expired_passports['C Code']) / len(df['C Code'])
            st.write("Expired Passports Count: ",ex_pass_count)
            st.write("Expired Passports percentage: {:.2f}%".format(ex_pass_percent))
        else:
            st.write("No Expired Passports Found.")
    st.write("_______________________________________________")
    if "EID Expiry" in df.columns:
        # Filter expired EIDs
        expired_EID = df[pd.to_datetime(df["EID Expiry"], errors='coerce') < today]

        if not expired_EID.empty:
            st.write("Expired EIDs:")
            st.dataframe(expired_EID)
            ex_EID_count =  len(expired_EID['C Code'])
            ex_EID_percent = len(expired_EID['C Code']) / len(df['C Code'])
            st.write("Expired EID Count: ",ex_EID_count)
            st.write("Expired EID percentage: {:.2f}%".format(ex_EID_percent))
        else:
            st.write("No Expired EIDs Found.") 

    if "Trade License Expiry Date" in df.columns:
        # Filter expired Trade Licenses
        expired_trd = df[pd.to_datetime(df["Trade License Expiry Date"], errors='coerce') < today]

        if not expired_trd.empty:
            st.write("Expired Trade Licenses:")
            st.dataframe(expired_trd)
            ex_trd_count =  len(expired_trd['Accountnum'])
            ex_trd_percent = len(expired_trd['Accountnum']) / len(df['Accountnum'])
            st.write("Expired trd Count: ",ex_trd_count)
            st.write("Expired trd percentage: {:.2f}%".format(ex_trd_percent))
        else:
            st.write("No Expired Trade Licenses Found.")                

    st.write("_______________________________________________")

def main():
    st.title('Data Quality Reporting Tool')
    st.write('Upload your dataset and get data quality scores.')

    uploaded_file = st.file_uploader('Upload a CSV or Excel file', type=['csv', 'xlsx'])

    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)
            else:
                st.error("Invalid file format. Please provide a CSV or Excel file.")
                return
        except Exception as e:
            st.error("An error occurred while reading the dataset: {}".format(str(e)))
            return

        st.subheader('Data Quality Scores')
        Quality(df)

if __name__ == '__main__':
    main()