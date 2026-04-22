from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

binary_cols = ['schoolsup', 'famsup', 'paid', 'activities', 'nursery', 'higher', 'internet', 'romantic']
for col in binary_cols:
    df[col] = df[col].map({'yes': 1, 'no': 0})     # Binary mapping of yes and no to 1 and 0

df['support_index'] = df['schoolsup'] + df['famsup'] + df['higher']
df['risk_behavior'] = df['Dalc'] + df['Walc'] + df['goout']
df['engagement'] = df['studytime'] - (df['absences'] / 10)          # Feature Engineering (Domain Knowledge)

df_encoded = pd.get_dummies(df, drop_first=True)    # One-hot encoding of categorical variables, dropping the first category to avoid multicollinearity

X = df_encoded.drop(columns=['G1', 'G2', 'Risk'], errors='ignore')
y = df_encoded['Risk']          # Define Features (X) and Target (y) for the EARLY MODEL

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

scaler = StandardScaler()

X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)
X_test_scaled = pd.DataFrame(scaler.transform(X_test), columns=X_test.columns)

print(f"Training Data Shape: {X_train_scaled.shape}")
print(f"Testing Data Shape: {X_test_scaled.shape}")
print(f"Train At-Risk %: {y_train.mean():.2%}")
print(f"Test At-Risk %: {y_test.mean():.2%}")