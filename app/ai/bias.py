import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def detect_bias(employee_data: pd.DataFrame):
    """
    employee_data columns:
    ['employee_id','manager_id','jira_tickets','slack_activity',
     'extra_activities','bmi','annual_roles','customer_appreciations']
    """

    # Normalize numeric fields
    scaler = MinMaxScaler()
    numeric_cols = ['jira_tickets','slack_activity','extra_activities','customer_appreciations']
    employee_data[numeric_cols] = scaler.fit_transform(employee_data[numeric_cols])

    # Compare employees within same manager
    results = []
    for manager_id, group in employee_data.groupby("manager_id"):
        mean_scores = group[numeric_cols].mean()
        for _, row in group.iterrows():
            deviation = abs(row[numeric_cols] - mean_scores).mean()
            if deviation > 0.4:  # arbitrary threshold
                results.append({
                    "employee_id": row["employee_id"],
                    "manager_id": manager_id,
                    "bias_flag": True,
                    "deviation_score": deviation
                })

    return results
