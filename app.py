import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import openai

# Function to load CSV files
def load_csv(file):
    return pd.read_csv(file)

# Function to load Google Sheets
def load_google_sheet(credentials_file, sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# Streamlit app
st.title("AI Agent for Data Retrieval")

# Upload options
option = st.selectbox("Upload CSV or Connect Google Sheet", ["CSV", "Google Sheet"])

if option == "CSV":
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file:
        data = load_csv(uploaded_file)
        st.write("Data Preview", data.head())
elif option == "Google Sheet":
    credentials_file = st.text_input("Enter Google Sheets credentials JSON file path")
    sheet_name = st.text_input("Enter Google Sheet name")
    if credentials_file and sheet_name:
        data = load_google_sheet(credentials_file, sheet_name)
        st.write("Data Preview", data.head())

# Dynamic query input
selected_column = st.selectbox("Select the main column", data.columns)
query_template = st.text_input("Enter your query template", "Get me the email address of {company}")

# Function to perform web search
def search_web(query):
    api_key = "YOUR_SERPAPI_KEY"
    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key
    }
    response = requests.get("https://serpapi.com/search", params=params)
    return response.json()

# Perform searches and extract information
results = []
for entity in data[selected_column]:
    query = query_template.format(company=entity)
    search_results = search_web(query)
    results.append(search_results)

openai.api_key = "YOUR_OPENAI_API_KEY"

def extract_information(prompt, search_results):
    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt + "\n\n" + search_results,
        max_tokens=100
    )
    return response.choices[0].text.strip()

extracted_info = []
for search_result in results:
    info = extract_information(query_template, search_result['snippet'])
    extracted_info.append(info)

result_df = pd.DataFrame({
    selected_column: data[selected_column],
    "Extracted Information": extracted_info
})

st.write(result_df)
st.download_button("Download Results as CSV", result_df.to_csv(index=False).encode("utf-8"), "results.csv", "text/csv")

if st.button("Update Google Sheet"):
    sheet.update([result_df.columns.values.tolist()] + result_df.values.tolist())
