import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Student Email Comparison Tool", layout="wide")

st.title("📧 Student Email Comparison Tool")
st.markdown("Upload two CSV files to compare student emails and identify discrepancies.")

# File uploaders
col1, col2 = st.columns(2)

with col1:
    st.subheader("File 1")
    file1 = st.file_uploader("Upload first CSV file", type=['csv'], key='file1')

with col2:
    st.subheader("File 2")
    file2 = st.file_uploader("Upload second CSV file", type=['csv'], key='file2')

def normalize_name(first, last):
    """Normalize names by converting to lowercase and stripping whitespace"""
    first_clean = str(first).strip().lower() if pd.notna(first) else ""
    last_clean = str(last).strip().lower() if pd.notna(last) else ""
    return f"{first_clean}|{last_clean}"

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
            # Create normalized name key and email
            df1['name_key'] = df1.apply(lambda row: normalize_name(row['First Name'], row['Last Name']), axis=1)
            df2['name_key'] = df2.apply(lambda row: normalize_name(row['First Name'], row['Last Name']), axis=1)
            
            df1['normalized_email'] = df1['Email'].apply(normalize_email)
            df2['normalized_email'] = df2['Email'].apply(normalize_email)
            
            # Remove any empty name keys
            df1 = df1[df1['name_key'] != "|"]
            df2 = df2[df2['name_key'] != "|"]
            
            # Find students in both files
            students_in_both = set(df1['name_key']) & set(df2['name_key'])
            students_only_file1 = set(df1['name_key']) - set(df2['name_key'])
            students_only_file2 = set(df2['name_key']) - set(df1['name_key'])
            
            # Find students with different emails
            different_emails = []
            for name_key in students_in_both:
                student1 = df1[df1['name_key'] == name_key].iloc[0]
                student2 = df2[df2['name_key'] == name_key].iloc[0]
                
                if student1['normalized_email'] != student2['normalized_email']:
                    different_emails.append({
                        'First Name': student1['First Name'],
                        'Last Name': student1['Last Name'],
                        'Email (File 1)': student1['Email'],
                        'Email (File 2)': student2['Email']
                    })
            
            # Create dataframes for display
            df_different = pd.DataFrame(different_emails)
            
            only_file1_data = []
            for name_key in students_only_file1:
                student = df1[df1['name_key'] == name_key].iloc[0]
                only_file1_data.append({
                    'First Name': student['First Name'],
                    'Last Name': student['Last Name'],
                    'Email': student['Email']
                })
            df_only_file1 = pd.DataFrame(only_file1_data)
            
            only_file2_data = []
            for name_key in students_only_file2:
                student = df2[df2['name_key'] == name_key].iloc[0]
                only_file2_data.append({
                    'First Name': student['First Name'],
                    'Last Name': student['Last Name'],
                    'Email': student['Email']
                })
            df_only_file2 = pd.DataFrame(only_file2_data)
            
            # Display results
            st.markdown("---")
            st.header("📊 Comparison Results")
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Students with Different Emails", len(df_different))
            with col2:
                st.metric("Students Only in File 1", len(df_only_file1))
            with col3:
                st.metric("Students Only in File 2", len(df_only_file2))
            
            # Section 1: Different Emails
            st.markdown("---")
            st.subheader("🔄 Students with Different Emails")
            if len(df_different) > 0:
                st.dataframe(df_different, use_container_width=True)
                
                # Create copyable text version
                text_output = "Students with Different Emails:\n\n"
                for _, row in df_different.iterrows():
                    text_output += f"{row['First Name']} {row['Last Name']}\n"
                    text_output += f"  File 1: {row['Email (File 1)']}\n"
                    text_output += f"  File 2: {row['Email (File 2)']}\n\n"
                
                st.text_area("Copy this text:", text_output, height=200)
            else:
                st.success("No students found with different emails! ✅")
            
            # Section 2: Only in File 1
            st.markdown("---")
            st.subheader("📄 Students Only in File 1")
            if len(df_only_file1) > 0:
                st.dataframe(df_only_file1, use_container_width=True)
                
                text_output = "Students Only in File 1:\n\n"
                for _, row in df_only_file1.iterrows():
                    text_output += f"{row['First Name']} {row['Last Name']} - {row['Email']}\n"
                
                st.text_area("Copy this text:", text_output, height=150, key='text1')
            else:
                st.info("No students found only in File 1.")
            
            # Section 3: Only in File 2
            st.markdown("---")
            st.subheader("📄 Students Only in File 2")
            if len(df_only_file2) > 0:
                st.dataframe(df_only_file2, use_container_width=True)
                
                text_output = "Students Only in File 2:\n\n"
                for _, row in df_only_file2.iterrows():
                    text_output += f"{row['First Name']} {row['Last Name']} - {row['Email']}\n"
                
                st.text_area("Copy this text:", text_output, height=150, key='text2')
            else:
                st.info("No students found only in File 2.")
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please make sure your CSV files are properly formatted with columns: First Name, Last Name, Email")

else:
    st.info("👆 Please upload both CSV files to begin comparison.")
    
    with st.expander("ℹ️ How to use this tool"):
        st.markdown("""
        1. Upload two CSV files using the file uploaders above
        2. Each file must have these exact columns: **First Name**, **Last Name**, **Email**
        3. The tool will compare students based on their first and last names (case-insensitive)
        4. You'll see three reports:
           - Students with different emails in both files
           - Students only appearing in File 1
           - Students only appearing in File 2
        5. Each section has a text area where you can easily copy the results
        """)
