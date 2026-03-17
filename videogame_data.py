import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF

# --- DATA PREP (Your Logic & Comments) ---
df = pd.read_csv("vgsales.csv")

# df.Year = df["Year"].astype("Int64")
df['Year'] = df['Year'].astype("Int64")
fill_year = df["Year"].median()

# fillna for Year with median, not mean because data has high variation in values
df['Year'] = df['Year'].fillna(fill_year)

# remove Nan values from publisher
df = df[df["Publisher"].notnull()]

# --- MATH AUDIT (Your Finding) ---
df["Total_Sum"] = df["Other_Sales"] + df["NA_Sales"] + df["JP_Sales"] + df["EU_Sales"]
match_count = len(df[df["Global_Sales"] == df["Total_Sum"]])

# --- GRAPHS (Your Ideas) ---

# 1. Market Share Pie Chart (Keeping this as requested)
plt.figure(figsize=(7, 7))
regions = {
    'North America': df['NA_Sales'].sum(),
    'Europe': df['EU_Sales'].sum(),
    'Japan': df['JP_Sales'].sum(),
    'Other': df['Other_Sales'].sum()
}
pd.Series(regions).plot(kind='pie', autopct='%1.1f%%', colors=['#ff9999','#66b3ff','#99ff99','#ffcc99'])
plt.title("Global Market Share by Region")
plt.ylabel("")
plt.savefig("market_pie.png")
plt.close()

# 2. Genre Sales (The Bar Chart you wanted)
plt.figure(figsize=(10, 6))
df.groupby("Genre")["Global_Sales"].sum().sort_values().plot(kind='barh', color='teal')
plt.title("Genre with High Global Sales")
plt.tight_layout()
plt.savefig("genre_bar.png")
plt.close()

# --- THE PDF GENERATOR ---
class MyPortfolio(FPDF):
    def header(self):
        self.set_font("Arial", "B", 15)
        self.cell(0, 10, "Data Analysis Portfolio: Video Game Sales", ln=True, align='C')
        self.ln(5)

pdf = MyPortfolio()
pdf.set_auto_page_break(auto=True, margin=15)

# PAGE 1: Your Intro and Math Audit
pdf.add_page()
pdf.set_font("Arial", "B", 12)
pdf.cell(0, 10, "Technical Observation: Data Integrity Check", ln=True)
pdf.set_font("Arial", size=10)

# Including your specific findings in the text
audit_text = (
    f"Finding: Global Sales vs Total Sum does not match in all rows.\n"
    f"Total rows: {len(df)}\n"
    f"Number of rows that match exactly: {match_count}\n"
    f"Difference: {len(df) - match_count}\n\n"
    f"Analysis: Even with discrepancies, regional trends remain clear."
)
pdf.multi_cell(0, 7, audit_text)
pdf.ln(5)
pdf.image("market_pie.png", x=50, w=110)

# PAGE 2: Your Genre Analysis
pdf.add_page()
pdf.set_font("Arial", "B", 12)
pdf.cell(0, 10, "Genre and Market Trends", ln=True)
pdf.image("genre_bar.png", x=10, w=190)
pdf.ln(10)

# Adding your comments about mean/outliers
pdf.set_font("Arial", "I", 10)
pdf.multi_cell(0, 7, "Note: Average (mean) is not to be trusted when data has outliers. "
                     "For this reason, median was used for year imputation and "
                     "segmentation was used for platform analysis.")

# PAGE 3: The Pivot Table (Filtered for readability)
pdf.add_page()
pdf.set_font("Arial", "B", 12)
pdf.cell(0, 10, "Platform vs Genre: Average Global Sales", ln=True)
pdf.ln(5)

# Pivot Table Logic
top_p = df.groupby('Platform')['Global_Sales'].sum().nlargest(5).index
top_g = df.groupby('Genre')['Global_Sales'].sum().nlargest(5).index
pivot = df[df['Platform'].isin(top_p) & df['Genre'].isin(top_g)].pivot_table(
    values='Global_Sales', index='Genre', columns='Platform', aggfunc='mean').fillna(0)

# Drawing the Grid
pdf.set_font("Arial", "B", 9)
pdf.cell(30, 10, "Genre", 1)
for col in pivot.columns:
    pdf.cell(30, 10, str(col), 1, 0, 'C')
pdf.ln()

pdf.set_font("Arial", size=9)
for genre, row in pivot.iterrows():
    pdf.cell(30, 10, str(genre), 1)
    for val in row:
        pdf.cell(30, 10, f"{val:.2f}", 1, 0, 'C')
    pdf.ln()

pdf.output("My_Final_Portfolio.pdf")
print("Portfolio Ready for GitHub!")
