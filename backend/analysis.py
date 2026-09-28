import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# =========================================================
# 1. LOAD DATA
# =========================================================

print("=" * 60)
print("CONSTRUCTION COST ANALYSIS")
print("=" * 60)

df = pd.read_csv("../data/construction_cost.csv")

print("\nFirst 5 rows:")
print(df.head())


# =========================================================
# 2. BASIC DATASET INFORMATION
# =========================================================

print("\nDataset Shape:")
print(df.shape)

print("\nColumn Names:")
print(df.columns.tolist())

print("\nDataset Information:")
df.info()

print("\nMissing Values:")
print(df.isnull().sum())

print("\nDuplicate Rows:")
print(df.duplicated().sum())


# =========================================================
# 3. REMOVE DUPLICATES
# =========================================================

df = df.drop_duplicates()

print("\nShape after removing duplicates:")
print(df.shape)


# =========================================================
# 4. DATA CLEANING
# =========================================================

numeric_columns = [
    'Duration',
    'Planned_Labour_Cost',
    'Actual_Labour_Cost',
    'Planned_Material_Cost',
    'Actual_Material_Cost',
    'Equipment_Cost',
    'Subcontracting_Cost'
]


# Convert numeric columns
for col in numeric_columns:

    df[col] = pd.to_numeric(
        df[col],
        errors='coerce'
    )


# Fill missing numeric values
for col in numeric_columns:

    df[col] = df[col].fillna(
        df[col].median()
    )


# Handle Project_Size separately
# because it may be numeric OR categorical

if df['Project_Size'].dtype == 'object':

    df['Project_Size'] = (
        df['Project_Size']
        .astype(str)
        .str.strip()
    )

else:

    df['Project_Size'] = pd.to_numeric(
        df['Project_Size'],
        errors='coerce'
    )

    df['Project_Size'] = df['Project_Size'].fillna(
        df['Project_Size'].median()
    )


print("\nData after cleaning:")
print(df.head())


# =========================================================
# 5. DESCRIPTIVE STATISTICS
# =========================================================

print("\nDescriptive Statistics:")
print(df.describe(include='all'))


print("\nLocation Distribution:")
print(df['Location'].value_counts())


# =========================================================
# 6. COST VARIANCE CALCULATIONS
# =========================================================

# Labour variance
df['Labour_Variance'] = (
    df['Actual_Labour_Cost']
    -
    df['Planned_Labour_Cost']
)


# Material variance
df['Material_Variance'] = (
    df['Actual_Material_Cost']
    -
    df['Planned_Material_Cost']
)


# Planned cost
# Only planned labour and material are available
df['Planned_Total_Cost'] = (
    df['Planned_Labour_Cost']
    +
    df['Planned_Material_Cost']
)


# Actual cost
df['Actual_Total_Cost'] = (
    df['Actual_Labour_Cost']
    +
    df['Actual_Material_Cost']
    +
    df['Equipment_Cost']
    +
    df['Subcontracting_Cost']
)


# Total cost variance
df['Total_Cost_Variance'] = (
    df['Actual_Total_Cost']
    -
    df['Planned_Total_Cost']
)


# Variance percentage
df['Variance_Percentage'] = np.where(
    df['Planned_Total_Cost'] != 0,
    (
        df['Total_Cost_Variance']
        /
        df['Planned_Total_Cost']
    ) * 100,
    0
)


print("\nCost Analysis:")

print(
    df[
        [
            'Project_ID',
            'Planned_Total_Cost',
            'Actual_Total_Cost',
            'Total_Cost_Variance',
            'Variance_Percentage'
        ]
    ].head(10)
)


# =========================================================
# 7. OVER-BUDGET ANALYSIS
# =========================================================

over_budget = df[
    df['Total_Cost_Variance'] > 0
]

under_budget = df[
    df['Total_Cost_Variance'] <= 0
]


print("\nProjects Over Budget:")
print(
    over_budget[
        [
            'Project_ID',
            'Location',
            'Duration',
            'Total_Cost_Variance',
            'Variance_Percentage'
        ]
    ]
)


over_budget_percentage = (
    len(over_budget)
    /
    len(df)
) * 100


print(
    f"\nPercentage of projects over budget: "
    f"{over_budget_percentage:.2f}%"
)


print(
    f"Number of projects over budget: "
    f"{len(over_budget)}"
)


print(
    f"Number of projects under/on budget: "
    f"{len(under_budget)}"
)


# =========================================================
# 8. COST SUMMARY
# =========================================================

total_labour_variance = (
    df['Labour_Variance'].sum()
)

total_material_variance = (
    df['Material_Variance'].sum()
)

total_equipment_cost = (
    df['Equipment_Cost'].sum()
)

total_subcontracting_cost = (
    df['Subcontracting_Cost'].sum()
)


print("\nCost Summary")

print(
    "Total Labour Variance:",
    total_labour_variance
)

print(
    "Total Material Variance:",
    total_material_variance
)

print(
    "Total Equipment Cost:",
    total_equipment_cost
)

print(
    "Total Subcontracting Cost:",
    total_subcontracting_cost
)


# =========================================================
# 9. CREATE OUTPUT DIRECTORY
# =========================================================

os.makedirs(
    "backend",
    exist_ok=True
)

os.makedirs(
    "visualizations",
    exist_ok=True
)


# =========================================================
# 10. VISUALIZATION 1
#     PLANNED VS ACTUAL COST
# =========================================================

plt.figure(figsize=(10, 6))

costs = [
    df['Planned_Total_Cost'].sum(),
    df['Actual_Total_Cost'].sum()
]

plt.bar(
    [
        'Planned Cost',
        'Actual Cost'
    ],
    costs
)

plt.title(
    'Planned Cost vs Actual Cost'
)

plt.ylabel('Cost')

plt.tight_layout()

plt.savefig(
    'visualizations/planned_vs_actual.png',
    dpi=300
)

plt.show()


# =========================================================
# 11. VISUALIZATION 2
#     LABOUR VS MATERIAL VARIANCE
# =========================================================

categories = [
    'Labour',
    'Material'
]

variances = [
    total_labour_variance,
    total_material_variance
]


plt.figure(figsize=(10, 6))

plt.bar(
    categories,
    variances
)

plt.title(
    'Cost Variance by Category'
)

plt.xlabel(
    'Cost Category'
)

plt.ylabel(
    'Variance'
)

plt.tight_layout()

plt.savefig(
    'visualizations/cost_variance_category.png',
    dpi=300
)

plt.show()


# =========================================================
# 12. VISUALIZATION 3
#     DURATION VS COST VARIANCE
# =========================================================

plt.figure(figsize=(10, 6))

sns.scatterplot(
    data=df,
    x='Duration',
    y='Total_Cost_Variance',
    hue='Location',
    s=80
)

plt.axhline(
    0,
    linestyle='--'
)

plt.title(
    'Project Duration vs Cost Variance'
)

plt.xlabel(
    'Project Duration'
)

plt.ylabel(
    'Total Cost Variance'
)

plt.tight_layout()

plt.savefig(
    'visualizations/duration_vs_variance.png',
    dpi=300
)

plt.show()


# =========================================================
# 13. VISUALIZATION 4
#     LOCATION VS COST VARIANCE
# =========================================================

plt.figure(figsize=(10, 6))

sns.boxplot(
    data=df,
    x='Location',
    y='Total_Cost_Variance'
)

plt.title(
    'Cost Variance by Location'
)

plt.xlabel(
    'Location'
)

plt.ylabel(
    'Total Cost Variance'
)

plt.xticks(
    rotation=45
)

plt.tight_layout()

plt.savefig(
    'visualizations/location_vs_variance.png',
    dpi=300
)

plt.show()


# =========================================================
# 14. DURATION CORRELATION
# =========================================================

corr_value = df[
    'Duration'
].corr(
    df['Total_Cost_Variance']
)


print(
    f"\nDuration vs Cost Variance Correlation: "
    f"{corr_value:.3f}"
)


# =========================================================
# 15. LOCATION ANALYSIS
# =========================================================

location_analysis = (
    df.groupby('Location')
    [
        [
            'Total_Cost_Variance',
            'Variance_Percentage',
            'Duration'
        ]
    ]
    .mean()
    .sort_values(
        'Total_Cost_Variance',
        ascending=False
    )
)


print("\nLocation Analysis:")
print(location_analysis)


# =========================================================
# 16. PROJECT SIZE ANALYSIS
# =========================================================

size_analysis = (
    df.groupby('Project_Size')
    [
        [
            'Total_Cost_Variance',
            'Variance_Percentage',
            'Duration'
        ]
    ]
    .mean()
    .sort_values(
        'Total_Cost_Variance',
        ascending=False
    )
)


print("\nProject Size Analysis:")
print(size_analysis)


# =========================================================
# 17. TOP PROJECT OVERRUNS
# =========================================================

top_overruns = (
    df.sort_values(
        'Total_Cost_Variance',
        ascending=False
    )
    .head(10)
)


print("\nTop 10 Project Cost Overruns:")

print(
    top_overruns[
        [
            'Project_ID',
            'Location',
            'Project_Size',
            'Duration',
            'Total_Cost_Variance',
            'Variance_Percentage'
        ]
    ]
)


# =========================================================
# 18. LINEAR REGRESSION
# =========================================================

print("\n")
print("=" * 60)
print("LINEAR REGRESSION")
print("=" * 60)


model_data = df.copy()


# Convert categorical columns
categorical_columns = []


if model_data['Project_Size'].dtype == 'object':

    categorical_columns.append(
        'Project_Size'
    )


if model_data['Location'].dtype == 'object':

    categorical_columns.append(
        'Location'
    )


if categorical_columns:

    model_data = pd.get_dummies(
        model_data,
        columns=categorical_columns,
        drop_first=True
    )


# ---------------------------------------------------------
# IMPORTANT:
# Use only variables that are available for prediction.
#
# Do NOT include:
# Actual_Total_Cost
# Labour_Variance
# Material_Variance
# Total_Cost_Variance
# Variance_Percentage
#
# because they are derived from the target/outcome.
# ---------------------------------------------------------

X = model_data.drop(
    columns=[
        'Project_ID',
        'Total_Cost_Variance',
        'Labour_Variance',
        'Material_Variance',
        'Variance_Percentage',
        'Planned_Total_Cost',
        'Actual_Total_Cost'
    ],
    errors='ignore'
)


y = model_data[
    'Total_Cost_Variance'
]


# Make sure X contains numeric values
X = X.apply(
    pd.to_numeric,
    errors='coerce'
)


# Fill any missing values
X = X.fillna(
    X.median(numeric_only=True)
)


# Train-test split
X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,

    test_size=0.2,

    random_state=42
)


# Train model
model = LinearRegression()

model.fit(
    X_train,
    y_train
)


# Predictions
y_pred = model.predict(
    X_test
)


# Evaluation
mae = mean_absolute_error(
    y_test,
    y_pred
)


rmse = np.sqrt(
    mean_squared_error(
        y_test,
        y_pred
    )
)


r2 = r2_score(
    y_test,
    y_pred
)


print("\nLinear Regression Results")
print("-------------------------")

print(
    f"MAE : {mae:.2f}"
)

print(
    f"RMSE: {rmse:.2f}"
)

print(
    f"R²  : {r2:.4f}"
)


# =========================================================
# 19. REGRESSION COEFFICIENTS
# =========================================================

coefficients = pd.DataFrame({

    'Feature': X.columns,

    'Coefficient': model.coef_

})


coefficients = coefficients.sort_values(
    'Coefficient',
    ascending=False
)


print("\nRegression Coefficients:")

print(coefficients)


# =========================================================
# 20. SAVE CLEANED DATA
# =========================================================

df.to_json(
    "dashboard_data.json",
    orient="records",
    indent=4
)


print(
    "\nCleaned dataset saved successfully."
)


# =========================================================
# 21. SAVE DASHBOARD DATA
# =========================================================

df.to_json(

    "backend/dashboard_data.json",

    orient="records",

    indent=4

)


print(
    "Dashboard data saved to "
    "backend/dashboard_data.json"
)


# =========================================================
# 22. SAVE MODEL RESULTS FOR FRONTEND
# =========================================================

model_results = {

    "mae": float(mae),

    "rmse": float(rmse),

    "r2": float(r2),

    "correlation_duration_variance":
        float(corr_value),

    "over_budget_percentage":
        float(over_budget_percentage),

    "total_projects":
        int(len(df)),

    "projects_over_budget":
        int(len(over_budget))

}


import json


with open(
    "backend/model_results.json",
    "w"
) as file:

    json.dump(
        model_results,
        file,
        indent=4
    )


print(
    "Model results saved to "
    "backend/model_results.json"
)


# =========================================================
# 23. FINISHED
# =========================================================

print("\n")
print("=" * 60)
print("ANALYSIS COMPLETED SUCCESSFULLY")
print("=" * 60)