import pandas as pd
import joblib
import sklearn
from .models import CustomerProfile, Product
def predict_preferred_category(customer_data): 
    #customer data dict of age, gender, household_size, has_children, monthly_income_sgd, employment_status, occupation, education
    loaded_model = joblib.load('onlinestore/mlmodel/b2c_customers_100.joblib')
    columns = {
        'age':'int64', 'household_size':'int64', 'has_children':'int64', 'monthly_income_sgd':'float64',
        'gender_Female':'bool', 'gender_Male':'bool', 'employment_status_Full-time':'bool',
        'employment_status_Part-time':'bool', 'employment_status_Retired':'bool',
        'employment_status_Self-employed':'bool', 'employment_status_Student':'bool',
        'occupation_Admin':'bool', 'occupation_Education':'bool', 'occupation_Sales':'bool',
        'occupation_Service':'bool', 'occupation_Skilled Trades':'bool', 'occupation_Tech':'bool',
        'education_Bachelor':'bool', 'education_Diploma':'bool', 'education_Doctorate':'bool',
        'education_Master':'bool', 'education_Secondary':'bool'
    }

    df = pd.DataFrame({col: pd.Series(dtype=dtype) for col, dtype in columns.items()})
    customer_df = pd.DataFrame([customer_data])
    customer_encoded = pd.get_dummies(customer_df, columns=['gender', 'employment_status', 'occupation', 'education'])    

    for col in df.columns:

        if col not in customer_encoded.columns:

            # Use False for bool columns, 0 for numeric
            if df[col].dtype == bool:
                df[col] = False
            else:
                df[col] = 0
        
        else:

            df[col] = customer_encoded[col]
    
    # Now input_encoded can be used for prediction
    prediction = loaded_model.predict(df)    

    return prediction

# use the loaded_rules to extract recommendations
#CleanRide Car Care Shield
def get_recommendations(items, metric='confidence', top_n=3):
    loaded_rules = joblib.load('onlinestore/mlmodel/b2c_products_500_transactions_50k.joblib')
    recommendations = set()
    for item in items:
        # Find rules where the item is in the antecedents
        matched_rules = loaded_rules[loaded_rules['antecedents'].apply(lambda x: item in x)]
        # Sort by the specified metric and get the top N
        top_rules = matched_rules.sort_values(by=metric, ascending=False).head(top_n)
        for _, row in top_rules.iterrows():
            recommendations.update(row['consequents'])
    # Remove items that are already in the input list
    recommendations.difference_update(items)
    product_recs = []
    for rec in list(recommendations)[:top_n]:
        try:
            prod = Product.objects.get(pk=rec)
            product_recs.append(
                {'product_sku': prod.sku_code, 
                 'product_name': prod.product_name,
                 'product_subcategory': prod.subcategory_id})
        except Product.DoesNotExist:
            pass
    return product_recs

def get_recommended_category(user):
    if not user.is_authenticated:
        return None
    try:
        profile = user.customer.customerprofile
        customer_data = {
            'age': profile.age,
            'gender': profile.gender,
            'household_size': profile.household_size,
            'has_children': profile.has_children,
            'monthly_income_sgd': profile.monthly_income,
            'employment_status': profile.employment_status,
            'occupation': profile.occupation,
            'education': profile.education
        }
        return predict_preferred_category(customer_data)[0]
    except (CustomerProfile.DoesNotExist, AttributeError):
        return None
