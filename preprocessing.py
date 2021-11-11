"""
Functions to process the produced dataset for use in predictive modeling algorithms
Processing includes:
    - Replace na/null values
    - NLP pipeline using nltk, spaCy
        - lowercasing
        - lemmitization
        - tokenization
        - stop word removal
"""

import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
# nltk.download('wordnet')
from nltk import wordnet

def fill_na_columns(df):
    fill_dict = {}
    for col in df.columns:
        if 'has' in col or 'score' in col:
            fill_dict[col] = 0
        else:
            fill_dict[col] = ''
    
    df = df.fillna(value = fill_dict)
    return df

def lowercase_columns(df):
    for col in df.columns:
        if isinstance(df[col][0], str):
            df[col] = df[col].str.lower()
    return df

def remove_stopwords(df, cols):
    stop = stopwords.words('english')
    for col in cols:
        df[col] = df[col].apply(lambda x: ' '.join([word for word in x.split() if word not in (stop)]))
    return df

w_tokenizer = nltk.tokenize.WhitespaceTokenizer()
lemmatizer = nltk.stem.WordNetLemmatizer()

def lemmatize_text(text):
    return [lemmatizer.lemmatize(w) for w in w_tokenizer.tokenize(text)]

def lemmatize_columns(df, cols):
    for col in cols:
        df[col] = df[col].apply(lemmatize_text)
    return df


