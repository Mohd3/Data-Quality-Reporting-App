import pandas as pd
import numpy as np
import re
import streamlit as st
import warnings
from datetime import date

warnings.filterwarnings('ignore')

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

def Outliers(col):
    Q1 = col.quantile(0.25)
    Q3 = col.quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    outliers = col[(col < lower_bound) | (col > upper_bound)]
    return outliers    
 

def Quality(df):
    num_records = len(df)

    null_value_counts = df.isnull().sum()
    available_columns = set(df.columns)
   
    completeness_score = (1 - (df.isnull().sum() / num_records)) * 100
    total_completeness_score = completeness_score.sum() / len(completeness_score)
    dups = df.duplicated().sum()
    uniqueness_score = (1 - dups / num_records) * 100

    #if not invalid_df.empty:
        #st.write("Total Validity Score: {:.2f}%".format(validity_score))
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
 
    st.write("_______________________________________________")
    st.subheader('Data Completeness Scores')
    completeness_df = pd.DataFrame(completeness_data)
    completeness_df = completeness_df.style.apply(color_coding, axis=1)

    st.dataframe(completeness_df)
    st.write("Total Completeness Score: {:.2f}%".format(total_completeness_score))
    st.write("_______________________________________________")

    # Calculate and display the number of outliers for each numerical column
    numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    outlier_counts = {col: Outliers(df[col]) for col in numerical_cols}

    st.subheader('Outliers')
    outlier_data = {'Column': [], 'Outlier Count': [], 'Outlier Percentage': []}
    for col, outliers in outlier_counts.items():
        outlier_data['Column'].append(col)
        outlier_data['Outlier Count'].append(len(outliers))
        outlier_percentage = (len(outliers) / len(df[col])) * 100
        outlier_data['Outlier Percentage'].append("{:.2f}%".format(outlier_percentage))

    outlier_df = pd.DataFrame(outlier_data)
    st.dataframe(outlier_df)

    st.write("_______________________________________________")

    today = pd.Timestamp(date.today())  # Convert today to a pandas Timestamp object

    

def main():
    st.title('Data Quality Reporting Tool')
    st.subheader('Upload your dataset and get data quality scores.')

    uploaded_file = st.file_uploader('Upload a CSV or Excel file', type=['csv', 'xlsx'])
    st.write("_______________________________________________")

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

        # Show the first 5 rows
        st.subheader('First 5 Rows')
        st.dataframe(df.head())

        # Show the number of columns and rows
        st.subheader('Dataset Information')
        st.write("Data Types:")
        st.write(df.dtypes)
        st.write("Number of Columns: {}".format(df.shape[1]))
        st.write("Number of Rows: {}".format(df.shape[0]))
        st.write("Unique Values:")
        st.write(df.nunique())


        # Show statistical summary
        st.subheader('Statistical Summary')
        st.dataframe(df.describe())

   

        Quality(df)

if __name__ == '__main__':
    main()