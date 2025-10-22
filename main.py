import streamlit as st
import pandas as pd

st.set_page_config(page_title="Email List Comparison Tool", layout="wide")

st.title("📧 Email List Comparison Tool")
st.markdown("Upload two CSV files to identify students enrolled in Google Classroom but missing from your attendance report.")

# File uploaders
col1, col2 = st.columns(2)

with col1:
    st.subheader("File 1: Attendance Report List")
    file1 = st.file_uploader("Upload Attendance Report CSV", type=['csv'], key='file1')

with col2:
    st.subheader("File 2: Google Classroom List")
    file2 = st.file_uploader("Upload Google Classroom CSV", type=['csv'], key='file2')

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
                st.error(f"Attendance Report is missing: {', '.join(missing_cols_file1)}")
            if missing_cols_file2:
                st.error(f"Google Classroom List is missing: {', '.join(missing_cols_file2)}")
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
            emails_in_both = emails_file1 & emails_file2
            
            # Create dataframe for students only in Google Classroom
            df_only_file2 = df2[df2['normalized_email'].isin(emails_only_file2)][['First Name', 'Last Name', 'Email']].copy()
            
            # Sort by first name for easier reading
            df_only_file2 = df_only_file2.sort_values(['First Name', 'Last Name']).reset_index(drop=True)
            
            # Display results
            st.markdown("---")
            st.header("📊 Comparison Results")
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Emails in Both Files", len(emails_in_both))
            with col2:
                st.metric("Only in Attendance Report", len(emails_only_file1))
            with col3:
                st.metric("Only in Google Classroom", len(emails_only_file2))
            
            # Section: Only in Google Classroom (File 2)
            st.markdown("---")
            st.subheader("📋 Students to Add to Attendance Report")
            st.caption("These students are enrolled in Google Classroom but missing from your attendance report.")
            
            if len(df_only_file2) > 0:
                st.dataframe(df_only_file2, use_container_width=True)
            else:
                st.success("Great! All Google Classroom students are in your attendance report. ✅")
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please make sure your CSV files are properly formatted with columns: First Name, Last Name, Email")

else:
    st.info("👆 Please upload both CSV files to begin comparison.")
    
    with st.expander("ℹ️ How to use this tool"):
        st.markdown("""
        1. Upload your **Attendance Report** CSV (File 1)
        2. Upload your **Google Classroom** CSV (File 2)
        3. Each file must have these exact columns: **First Name**, **Last Name**, **Email**
        4. The tool will show you students who are in Google Classroom but missing from your attendance report
        5. Results are sorted alphabetically by first name for easier reading
        """)
