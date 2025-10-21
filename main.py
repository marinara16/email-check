import streamlit as st
import pandas as pd

st.set_page_config(page_title="Email List Comparison Tool", layout="wide")

st.title("📧 Email List Comparison Tool")
st.markdown("Upload two CSV files to compare email lists and identify which emails appear in only one file.")

# File uploaders
col1, col2 = st.columns(2)

with col1:
    st.subheader("File 1")
    file1 = st.file_uploader("Upload first CSV file", type=['csv'], key='file1')

with col2:
    st.subheader("File 2")
    file2 = st.file_uploader("Upload second CSV file", type=['csv'], key='file2')

def normalize_email(email):
    """Normalize email by converting to lowercase and stripping whitespace"""
    return str(email).strip().lower() if pd.notna(email) else ""

if file1 and file2:
    try:
        # Read CSV files
        df1 = pd.read_csv(file1)
        df2 = pd.read_csv(file2)
        
        # Strip whitespace from column names
        df1.columns = df1.columns.str.strip()
        df2.columns = df2.columns.str.strip()
        
        # Check for required columns
        required_cols = ['First Name', 'Last Name', 'Email']
        
        missing_cols_file1 = [col for col in required_cols if col not in df1.columns]
        missing_cols_file2 = [col for col in required_cols if col not in df2.columns]
        
        if missing_cols_file1 or missing_cols_file2:
            st.error("Missing required columns!")
            if missing_cols_file1:
                st.error(f"File 1 is missing: {', '.join(missing_cols_file1)}")
            if missing_cols_file2:
                st.error(f"File 2 is missing: {', '.join(missing_cols_file2)}")
            st.info("Required columns: First Name, Last Name, Email")
        else:
            # Create normalized email column
            df1['normalized_email'] = df1['Email'].apply(normalize_email)
            df2['normalized_email'] = df2['Email'].apply(normalize_email)
            
            # Remove rows with empty emails
            df1 = df1[df1['normalized_email'] != ""]
            df2 = df2[df2['normalized_email'] != ""]
            
            # Get unique emails from each file
            emails_file1 = set(df1['normalized_email'])
            emails_file2 = set(df2['normalized_email'])
            
            # Find emails unique to each file
            emails_only_file1 = emails_file1 - emails_file2
            emails_only_file2 = emails_file2 - emails_file1
            
            # Create dataframes for students with unique emails
            df_only_file1 = df1[df1['normalized_email'].isin(emails_only_file1)][['First Name', 'Last Name', 'Email']].copy()
            df_only_file2 = df2[df2['normalized_email'].isin(emails_only_file2)][['First Name', 'Last Name', 'Email']].copy()
            
            # Sort by first name for easier reading
            df_only_file1 = df_only_file1.sort_values(['First Name', 'Last Name']).reset_index(drop=True)
            df_only_file2 = df_only_file2.sort_values(['First Name', 'Last Name']).reset_index(drop=True)
            
            # Display results
            st.markdown("---")
            st.header("📊 Comparison Results")
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Emails in Both Files", len(emails_file1 & emails_file2))
            with col2:
                st.metric("Emails Only in File 1", len(emails_only_file1))
            with col3:
                st.metric("Emails Only in File 2", len(emails_only_file2))
            
            # Section 1: Only in File 1
            st.markdown("---")
            st.subheader("📄 Emails Only in File 1")
            if len(df_only_file1) > 0:
                st.dataframe(df_only_file1, use_container_width=True)
                
                # Create copyable text version
                text_output = "Emails Only in File 1:\n\n"
                for _, row in df_only_file1.iterrows():
                    text_output += f"{row['First Name']} {row['Last Name']} - {row['Email']}\n"
                
                st.text_area("Copy this text:", text_output, height=200, key='text1')
            else:
                st.success("No unique emails in File 1! All emails from File 1 are also in File 2. ✅")
            
            # Section 2: Only in File 2
            st.markdown("---")
            st.subheader("📄 Emails Only in File 2")
            if len(df_only_file2) > 0:
                st.dataframe(df_only_file2, use_container_width=True)
                
                # Create copyable text version
                text_output = "Emails Only in File 2:\n\n"
                for _, row in df_only_file2.iterrows():
                    text_output += f"{row['First Name']} {row['Last Name']} - {row['Email']}\n"
                
                st.text_area("Copy this text:", text_output, height=200, key='text2')
            else:
                st.success("No unique emails in File 2! All emails from File 2 are also in File 1. ✅")
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please make sure your CSV files are properly formatted with columns: First Name, Last Name, Email")

else:
    st.info("👆 Please upload both CSV files to begin comparison.")
    
    with st.expander("ℹ️ How to use this tool"):
        st.markdown("""
        1. Upload two CSV files using the file uploaders above
        2. Each file must have these exact columns: **First Name**, **Last Name**, **Email**
        3. The tool will compare email addresses (case-insensitive)
        4. You'll see two reports:
           - Emails only appearing in File 1 (with student names)
           - Emails only appearing in File 2 (with student names)
        5. Each section has a text area where you can easily copy the results
        6. Results are sorted alphabetically by first name for easier reading
        """)
