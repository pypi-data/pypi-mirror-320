import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def get_split_data(df, column_name):
    df = df.copy()
    df[column_name] = df[column_name].fillna('')
    def custom_split(text):
        if not isinstance(text, str):
            return ['']
        text = text.replace('A/C', 'TEMP_AC')
        parts = text.split('/')
        parts = [part.replace('TEMP_AC', 'A/C') for part in parts]
        return parts
    df['split_parts'] = df[column_name].apply(custom_split)
    df['SLASH_SPLIT'] = df[column_name].apply(
        lambda x: 1 if isinstance(x, str) and '/' in x and 'A/C' not in x else 0
    )
    try:
        df_exploded = df.explode('split_parts', ignore_index=True)
    except ValueError as e:
        print(f"Error during explode: {e}")
        return df
    df_exploded[column_name] = df_exploded['split_parts']
    df_exploded = df_exploded.drop(columns=['split_parts'])
    return df_exploded

def get_cosine_similarity(df1, df2, column_name):
    if column_name not in df1.columns or column_name not in df2.columns:
        raise ValueError(f"Column '{column_name}' must exist in both dataframes.")
    combined_series = pd.concat([df1[column_name], df2[column_name]])
    vectorizer = TfidfVectorizer().fit(combined_series)
    tfidf_df1 = vectorizer.transform(df1[column_name])
    tfidf_df2 = vectorizer.transform(df2[column_name])
    
    similarities = cosine_similarity(tfidf_df2, tfidf_df1)
    
    results = []
    for i, row in enumerate(similarities):
        max_index = row.argmax()
        max_similarity = row[max_index]
        
        matching_vendor = df1.iloc[max_index][column_name]

        results.append({
            "Vendor (df2)": df2.iloc[i][column_name],
            "Matching Vendor (df1)": matching_vendor,
            "Cosine Similarity": round(max_similarity, 2)
        })
    return pd.DataFrame(results)

def get_top_5_matches(df1, df2, column_name):
    if column_name not in df1.columns or column_name not in df2.columns:
        raise ValueError(f"Column '{column_name}' not found in both dataframes")
    vectorizer = TfidfVectorizer().fit(pd.concat([df1[column_name], df2[column_name]]))
    tfidf_matrix_1 = vectorizer.transform(df1[column_name])
    tfidf_matrix_2 = vectorizer.transform(df2[column_name])
    cosine_sim = cosine_similarity(tfidf_matrix_1, tfidf_matrix_2)
    result_columns = [column_name]
    for i in range(1, 6):
        result_columns.append(f'match_name_{i}')
        result_columns.append(f'cosine_result_{i}')
    result_data = []
    for idx, row in enumerate(cosine_sim):
        top_indices = row.argsort()[-5:][::-1]
        top_matches = [(df2.iloc[i][column_name], row[i]) for i in top_indices]
        result_row = [df1.iloc[idx][column_name]]
        for match, score in top_matches:
            result_row.append(match)
            result_row.append(score)
        result_data.append(result_row)
    result_df = pd.DataFrame(result_data, columns=result_columns)
    return result_df