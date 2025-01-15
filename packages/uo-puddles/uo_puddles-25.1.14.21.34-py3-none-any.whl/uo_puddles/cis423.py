#for cis 423 class use

pypi_version = '1.67'

from sklearn.base import BaseEstimator, TransformerMixin

from sklearn.pipeline import Pipeline
import pandas as pd
pd.set_option('mode.chained_assignment', None)  #https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy

import numpy as np
import warnings
from sklearn.model_selection import train_test_split
from sklearn.impute import KNNImputer  #chapter 6

from sklearn.experimental import enable_halving_search_cv
from sklearn.model_selection import HalvingGridSearchCV
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score

from sklearn.neighbors import KNeighborsClassifier

#Check if a function is referencing global variables - bad
import builtins
import types
#use: @up_no_globals(globals())  #globals is function that returns *current* globals as dict
#DANGER DANGER: this fails on forward refs. Assumes helper functions all defined before main function. If not will get spurious error.
def up_no_globals(gfn:dict):

  def wrap(f):
    new_globals = {'__builtins__': builtins} 
    # removing keys from globals() storing global values in old_globals
    for key, val in gfn.items():
      if  callable(val):
          new_globals[key] = val
    new_f = types.FunctionType(f.__code__, globals=new_globals, argdefs=f.__defaults__)
    new_f.__annotations__ = f.__annotations__ # for some reason annotations aren't copied over
    return new_f

  return wrap

##THIS FROM mlops.py library
class CustomMappingTransformer(BaseEstimator, TransformerMixin):

  def __init__(self, mapping_column, mapping_dict:dict):
    assert isinstance(mapping_dict, dict), f'{self.__class__.__name__} constructor expected dictionary but got {type(mapping_dict)} instead.'
    self.mapping_dict = mapping_dict
    self.mapping_column = mapping_column  #column to focus on

  def fit(self, X, y = None):
    print(f"\nWarning: {self.__class__.__name__}.fit does nothing.\n")
    return self

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
    assert self.mapping_column in X.columns.to_list(), f'{self.__class__.__name__}.transform unknown column "{self.mapping_column}"'  #column legit?
    warnings.filterwarnings('ignore', message='.*downcasting.*')  #happens in replace method

    #Set up for producing warnings. First have to rework nan values to allow set operations to work.
    #In particular, the conversion of a column to a Series, e.g., X[self.mapping_column], transforms nan values in strange ways that screw up set differencing.
    #Strategy is to convert empty values to a string then the string back to np.nan
    placeholder = "NaN"
    column_values = X[self.mapping_column].fillna(placeholder).tolist()  #convert all nan values to the string "NaN" in new list
    column_values = [np.nan if v == placeholder else v for v in column_values]  #now convert back to np.nan
    keys_values = self.mapping_dict.keys()

    column_set = set(column_values)  #without the conversion above, the set will fail to have np.nan values where they should be.
    keys_set = set(keys_values)      #this will have np.nan values where they should be so no conversion necessary.

    #now check to see if all keys are contained in column.
    keys_not_found = keys_set - column_set
    if keys_not_found:
      print(f"\nWarning: {self.__class__.__name__}[{self.mapping_column}] these mapping keys do not appear in the column: {keys_not_found}\n")

    #now check to see if some keys are absent
    keys_absent = column_set -  keys_set
    if keys_absent:
      print(f"\nWarning: {self.__class__.__name__}[{self.mapping_column}] these values in the column do not contain corresponding mapping keys: {keys_absent}\n")

    #do actual mapping
    X_ = X.copy()
    X_[self.mapping_column] = X_[self.mapping_column].replace(self.mapping_dict)
    return X_

  def fit_transform(self, X, y = None):
    self.fit(X,y)
    result = self.transform(X)
    return result
    

class CustomOHETransformer(BaseEstimator, TransformerMixin):
  def __init__(self, target_column, dummy_na=False, drop_first=False):  #False because worried about mismatched columns after splitting. Easier to add missing column.
    self.target_column = target_column
    self.dummy_na = dummy_na
    self.drop_first = drop_first
 
  def fit(self, X, y = None):
    print(f"Warning: {self.__class__.__name__}.fit does nothing.")
    return self

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
    assert self.target_column in X.columns.to_list(), f'{self.__class__.__name__}.transform unknown column {self.target_column}'
    X_ = X.copy()
    X_ = pd.get_dummies(X_, columns=[self.target_column],
                        dummy_na=self.dummy_na,
                        drop_first = self.drop_first,
                       dtype=int)
    return X_

  def fit_transform(self, X, y = None):
    #self.fit(X,y)
    result = self.transform(X)
    return result

#This class will rename one or more columns.
class CustomRenamingTransformer(BaseEstimator, TransformerMixin):
  #your __init__ method below

  def __init__(self, mapping_dict:dict):
    assert isinstance(mapping_dict, dict), f'{self.__class__.__name__} constructor expected dictionary but got {type(mapping_dict)} instead.' 
    self.mapping_dict = mapping_dict

  def fit(self, X, y = None):
    print(f"Warning: {self.__class__.__name__}.fit does nothing.")
    return self

  #write the transform method without asserts. Again, maybe copy and paste from MappingTransformer and fix up.   
  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'RenamingTransformer.transform expected Dataframe but got {type(X)} instead.'
    #your assert code below

    column_set = set(X.columns)
    not_found = set(self.mapping_dict.keys()) - column_set
    assert not not_found, f"Columns {not_found}, are not in the data table"

    X_ = X.copy()
    return X_.rename(columns=self.mapping_dict)

  def fit_transform(self, X, y = None):
    #self.fit(X,y)
    result = self.transform(X)
    return result

class CustomPearsonTransformer(BaseEstimator, TransformerMixin):
  def __init__(self, threshold):
    self.threshold = threshold
    self.correlated_columns = None

  #define methods below

  def fit(self, X, y = None):
    df_corr = X.corr(method='pearson')
    masked_df = df_corr.abs() > self.threshold
    upper_mask = np.triu(masked_df, k=1)
    self.correlated_columns = [c for i,c in enumerate(df_corr.columns) if upper_mask[:,i].any()]
    return self

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
    assert isinstance(self.correlated_columns, list), f'NotFittedError: This {self.__class__.__name__} instance is not fitted yet. Call "fit" with appropriate arguments before using this estimator.'

    X_ = X.drop(columns=self.correlated_columns)
    return X_

  def fit_transform(self, X, y = None):
    self.fit(X, y)
    result = self.transform(X)
    return result

class CustomDythonTransformer(BaseEstimator, TransformerMixin):
  def __init__(self, threshold):
    self.threshold = threshold
    self.drop_columns = None

  #define methods below

  def fit(self, X, y = None):
    assoc_matrix = nominal.associations(X, nominal_columns='auto', compute_only=True)
    corr_matrix = assoc_matrix['corr'].abs().round(2)
    masked_df = corr_matrix > self.threshold
    upper_mask = np.triu(masked_df, k=1)
    self.drop_columns = [c for i,c in enumerate(X.columns) if upper_mask[:,i].any()]
    return self

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
    assert isinstance(self.drop_columns, list), f'NotFittedError: This {self.__class__.__name__} instance is not fitted yet. Call "fit" with appropriate arguments before using this estimator.'

    X_ = X.drop(columns=self.drop_columns)
    return X_

  def fit_transform(self, X, y = None):
    self.fit(X, y)
    result = self.transform(X)
    return result
  
#chapter 4 asks for 2 new transformers

class CustomSigma3Transformer(BaseEstimator, TransformerMixin):
  def __init__(self, target_column):
    self.target_column = target_column
    self.high_wall = None
    self.low_wall = None

  def fit(self, X, y = None):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.fit expected Dataframe but got {type(X)} instead.'
    assert self.target_column in X.columns.to_list(), f'{self.__class__.__name__}.fit unrecognizable column {self.target_column}.'
    mean = X[self.target_column].mean()
    sigma = X[self.target_column].std()
    self.high_wall = float(mean + 3.0*sigma)
    self.low_wall = mean - 3.0*sigma
    return self

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
    assert isinstance(self.high_wall, float), f'{self.__class__.__name__}.transform appears no fit was called prior.'
    assert self.target_column in X.columns.to_list(), f'{self.__class__.__name__}.transform unrecognizable column {self.target_column}.'

    X_ = X.copy()
    X_[self.target_column] = X_[self.target_column].clip(lower=self.low_wall, upper=self.high_wall)
    return X_

  def fit_transform(self, X, y = None):
    self.fit(X,y)
    result = self.transform(X)
    return result

class CustomTukeyTransformer(BaseEstimator, TransformerMixin):
  def __init__(self, target_column, fence='outer'):
    assert fence in ['inner', 'outer']
    self.target_column = target_column
    self.fence = fence
    self.inner_low = None
    self.outer_low = None
    self.inner_high = None
    self.outer_high = None

  def fit(self, X, y = None):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.fit expected Dataframe but got {type(X)} instead.'
    assert self.target_column in X.columns.to_list(), f'{self.__class__.__name__}.fit unrecognizable column {self.target_column}.'
    q1 = X[self.target_column].quantile(0.25)
    q3 = X[self.target_column].quantile(0.75)
    iqr = q3-q1
    self.inner_low = q1-1.5*iqr
    self.outer_low = q1-3.0*iqr
    self.inner_high = q3+1.5*iqr
    self.outer_high = q3+3.0*iqr
    return self

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
    assert isinstance(self.inner_low, float), f'{self.__class__.__name__}.transform appears no fit was called prior.'
    assert self.target_column in X.columns.to_list(), f'{self.__class__.__name__}.transform unrecognizable column {self.target_column}.'

    X_ = X.copy()
    if self.fence=='inner':
      X_[self.target_column] = X_[self.target_column].clip(lower=self.inner_low, upper=self.inner_high)
    elif self.fence=='outer':
      X_[self.target_column] = X_[self.target_column].clip(lower=self.outer_low, upper=self.outer_high)
    else:
      assert False, f"fence has unrecognized value {self.fence}"
    return X_

  def fit_transform(self, X, y = None):
    self.fit(X,y)
    result = self.transform(X)
    return result

class CustomDropColumnsTransformer(BaseEstimator, TransformerMixin):
  def __init__(self, column_list, action='drop'):
    assert action in ['keep', 'drop'], f'DropColumnsTransformer action {action} not in ["keep", "drop"]'
    assert isinstance(column_list, list), f'DropColumnsTransformer expected list but saw {type(column_list)}'
    self.column_list = column_list
    self.action = action

  def fit(self, X, y = None):
    print(f"Warning: {self.__class__.__name__}.fit does nothing.")
    return X

  #fill in the rest below
  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
    remaining_set = set(self.column_list) - set(X.columns)

    X_ = X.copy()
    if self.action=='drop':
      if remaining_set:
        print(f"\nWarning: {self.__class__.__name__} does not contain these columns to drop: {remaining_set}.")
      X_ = X_.drop(columns=self.column_list, errors='ignore')
    else:
      assert not remaining_set, f'{self.__class__.__name__}.transform unknown columns to keep: {remaining_set}'
      X_ = X_[self.column_list]
    return X_

  def fit_transform(self, X, y = None):
    result = self.transform(X)
    return result

#from scratch
class CustomRobustTransformer(BaseEstimator, TransformerMixin):
  def __init__(self, target_column):
    #fill in rest below
    self.target_column = target_column
    self.iqr = None
    self.med = None


  def fit(self, X, y = None):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.fit expected Dataframe but got {type(X)} instead.'
    assert self.target_column in X.columns.to_list(), f'{self.__class__.__name__}.fit unrecognizable column {self.target_column}.'
    self.iqr = float(X[self.target_column].quantile(.75)) - float(X[self.target_column].quantile(.25))
    self.med = X[self.target_column].median()
    return self

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
    assert self.iqr, f'NotFittedError: This {self.__class__.__name__} instance is not fitted yet. Call "fit" with appropriate arguments before using this estimator.'
    assert self.target_column in X.columns.to_list(), f'{self.__class__.__name__}.transform unrecognizable column {self.target_column}.'

    X_ = X.copy()
    X_[self.target_column] -= self.med
    X_[self.target_column] /= self.iqr
    return X_

  def fit_transform(self, X, y):
    self.fit(X,y)
    result = self.transform(X)
    return result

#wrapping RobustScaler (not used)
class __CustomRobustTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, target_column):
        self.target_column = target_column
        self.scaler = RobustScaler()
        
    def fit(self, X, y=None):
        # Input validation
        assert isinstance(X, pd.DataFrame), (
            f'{self.__class__.__name__}.fit expected DataFrame but got {type(X)} instead.'
        )
        assert self.target_column in X.columns, (
            f'{self.__class__.__name__}.fit unrecognizable column {self.target_column}.'
        )
        
        # Fit the scaler on the target column
        self.scaler.fit(X[[self.target_column]])
        return self

    def transform(self, X):
        # Input validation
        assert isinstance(X, pd.DataFrame), (
            f'{self.__class__.__name__}.transform expected DataFrame but got {type(X)} instead.'
        )
        assert self.target_column in X.columns, (
            f'{self.__class__.__name__}.transform unrecognizable column {self.target_column}.'
        )
        # Check if scaler has been fitted
        assert hasattr(self.scaler, 'center_'),f'This {self.__class__.__name__} instance is not fitted yet. Call "fit" before using this estimator.'
      

        # Create a copy to avoid modifying the original
        X_ = X.copy()
        # Transform only the target column
        X_[self.target_column] = self.scaler.transform(X_[[self.target_column]])
        return X_

    def fit_transform(self, X, y=None):
        return self.fit(X).transform(X)

class CustomTargetTransformer(BaseEstimator, TransformerMixin):
    """
    A target encoder that applies smoothing and returns np.nan for unseen categories.

    Parameters:
    -----------
    cols : list or None, default=None
        List of columns to encode. If None, all string/object columns will be encoded.
    smoothing : float, default=10.0
        Smoothing factor. Higher values give more weight to the global mean.
    """

    def __init__(self, cols=None, smoothing=10.0):
        self.cols = cols
        self.smoothing = smoothing

    def fit(self, X, y):
        """
        Fit the target encoder using training data.

        Parameters:
        -----------
        X : array-like of shape (n_samples, n_features)
            Training data features.
        y : array-like of shape (n_samples,)
            Target values.
        """
        assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.fit expected Dataframe but got {type(X)} instead.'

        #Convert y to Series so can use groupby, etc.
        y_ = pd.Series(y, index=X.index)


        # Determine which columns to encode
        if self.cols is None:
            self.cols_ = X.select_dtypes(include=['object', 'string', 'category']).columns
        else:
            self.cols_ = self.cols

        #Check for bogus columns
        residue = set(self.cols_) - set(X.columns)
        assert not residue, f'{self.__class__.__name__}.fit unknown columns "{residue}"'

        # Debug prints
        #print("\nDEBUG INFO:")
        #print("Cherbourg samples:", sum(X['Joined'] == 'Cherbourg'))
        #print("Cherbourg labels:", y_[X['Joined'] == 'Cherbourg'].tolist())
        
        # Calculate global mean
        self.global_mean_ = y_.mean()

        # Initialize encoding dictionary
        self.encoding_dict_ = {}

        # For each column
        for col in self.cols_:
            # Debug the groupby operation specifically
            #print("\nGroupby before means calculation:")
            #print(y_.groupby(X[col]).groups)
            
            # Get counts and means
            counts = X[col].value_counts().to_dict()    #dictionary of unique values in the column col and their counts
            means = y_.groupby(X[col]).mean().to_dict() #dictionary of unique values in the column col and their means

            #print("\nCounts:", counts)
            #print("Means:", means)

            # Calculate smoothed means
            smoothed_means = {}
            for category in counts.keys():
                n = counts[category]
                category_mean = means[category]
                # Apply smoothing formula: (n * cat_mean + m * global_mean) / (n + m)
                smoothed_mean = (n * category_mean + self.smoothing * self.global_mean_) / (n + self.smoothing)
                smoothed_means[category] = smoothed_mean

            # Store smoothed means for this column
            self.encoding_dict_[col] = smoothed_means

        return self

    def transform(self, X):
        """
        Transform the data using the fitted target encoder.
        Unseen categories will be encoded as np.nan.

        Parameters:
        -----------
        X : array-like of shape (n_samples, n_features)
            Input data to transform.
        """

        assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
        try:
          self.encoding_dict_  #if defined then fit was called
        except:
          assert False, f'{self.__class__.__name__}.transform not fitted'

        X_ = X.copy()

        # Apply encoding to each column
        for col in self.cols_:
            # Map values to encodings, naturally producing np.nan for unseen categories, i.e.,
            # when map tries to look up a value in the dictionary and doesn't find the key, it automatically returns np.nan. That is what we want.
            X_[col] = X_[col].map(self.encoding_dict_[col])

        return X_

    def fit_transform(self, X, y):
        """
        Fit the target encoder and transform the input data.

        Parameters:
        -----------
        X : array-like of shape (n_samples, n_features)
            Training data features.
        y : array-like of shape (n_samples,)
            Target values.
        """
        return self.fit(X, y).transform(X)


from sklearn.impute import KNNImputer
class CustomKNNTransformer(BaseEstimator, TransformerMixin):
  def __init__(self,n_neighbors=5, weights="uniform"):
    #your code
    self.n_neighbors = n_neighbors
    self.weights=weights
    self.imputer = KNNImputer(n_neighbors=self.n_neighbors, weights=self.weights, add_indicator=False)

  def fit(self, X, y = None):
    self.imputer.fit(X)
    return self

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
    assert hasattr(self.imputer, 'n_features_in_'), f'NotFittedError: This {self.__class__.__name__} instance is not fitted yet. Call "fit" with appropriate arguments before using this estimator.'

    X_ = X.copy()
    columns = X_.columns

    #Note that feature_names_in_ assumes all string names and will screw up if an int column name (for instance)
    if not columns.equals(pd.Index(self.imputer.feature_names_in_)):
      print(f'Column names mismatch warning: This {self.__class__.__name__} fitted with {pd.Index(self.imputer.feature_names_in_)} but transformed with {columns}')
    matrix = self.imputer.transform(X_)
    result_df = pd.DataFrame(matrix,columns=columns)
    return result_df

  def fit_transform(self, X, y = None):
    self.fit(X)
    result = self.transform(X)
    return result
    
##BELOW ORIGINAL 423 library
#drop by removing or keeping
class DropColumnsTransformer(BaseEstimator, TransformerMixin):
  def __init__(self, column_list, action='drop'):
    assert action in ['keep', 'drop'], f'DropColumnsTransformer action {action} not in ["keep", "drop"]'
    assert isinstance(column_list, list), f'DropColumnsTransformer expected list but saw {type(column_list)}'
    self.column_list = column_list
    self.action = action

  #fill in rest below
  def fit(self, X, y = None):
    print(f"Warning: {self.__class__.__name__}.fit does nothing.")
    return X

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
    remaining_set = set(self.column_list) - set(X.columns)

    X_ = X.copy()
    if self.action=='drop':
      if remaining_set:
        print(f"\nWarning: {self.__class__.__name__} does not contain these columns to drop: {remaining_set}.")
      X_ = X_.drop(columns=self.column_list, errors='ignore')
    else:
      assert not remaining_set, f'{self.__class__.__name__}.transform unknown columns to keep: {remaining_set}'
      X_ = X_[self.column_list]
    return X_

  def fit_transform(self, X, y = None):
    result = self.transform(X)
    return result
  
#This class maps values in a column, numeric or categorical.
#Importantly, it does not change NaNs, leaving that for the imputer step.
#This class maps values in a column, numeric or categorical.
class MappingTransformer(BaseEstimator, TransformerMixin):

  def __init__(self, mapping_column, mapping_dict:dict):
    assert isinstance(mapping_dict, dict), f'{self.__class__.__name__} constructor expected dictionary but got {type(mapping_dict)} instead.'
    self.mapping_dict = mapping_dict
    self.mapping_column = mapping_column  #column to focus on

  def fit(self, X, y = None):
    print(f"\nWarning: {self.__class__.__name__}.fit does nothing.\n")
    return X

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
    assert self.mapping_column in X.columns.to_list(), f'{self.__class__.__name__}.transform unknown column "{self.mapping_column}"'  #column legit?

    #now check to see if all keys are contained in column
    column_set = set(X[self.mapping_column].unique())
    keys_not_found = set(self.mapping_dict.keys()) - column_set
    if keys_not_found:
      print(f"\nWarning: {self.__class__.__name__}[{self.mapping_column}] does not contain these keys as values {keys_not_found}\n")

    #now check to see if some keys are absent
    keys_absent = column_set -  set(self.mapping_dict.keys())
    if keys_absent:
      print(f"\nWarning: {self.__class__.__name__}[{self.mapping_column}] does not contain keys for these values {keys_absent}\n")

    X_ = X.copy()
    X_[self.mapping_column] = X_[self.mapping_column].replace(self.mapping_dict)
    return X_

  def fit_transform(self, X, y = None):
    result = self.transform(X)
    return result
    

class OHETransformer(BaseEstimator, TransformerMixin):
  def __init__(self, target_column, dummy_na=False, drop_first=False):  #False because worried about mismatched columns after splitting. Easier to add missing column.
    self.target_column = target_column
    self.dummy_na = dummy_na
    self.drop_first = drop_first
 
  def fit(self, X, y = None):
    print(f"Warning: {self.__class__.__name__}.fit does nothing.")
    return X

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
    assert self.target_column in X.columns.to_list(), f'{self.__class__.__name__}.transform unknown column {self.target_column}'
    X_ = X.copy()
    X_ = pd.get_dummies(X_, columns=[self.target_column],
                        dummy_na=self.dummy_na,
                        drop_first = self.drop_first)
    return X_

  def fit_transform(self, X, y = None):
    result = self.transform(X)
    return result
  
#This class will rename one or more columns.
class RenamingTransformer(BaseEstimator, TransformerMixin):
  #your __init__ method below

  def __init__(self, mapping_dict:dict):
    assert isinstance(mapping_dict, dict), f'{self.__class__.__name__} constructor expected dictionary but got {type(mapping_dict)} instead.' 
    self.mapping_dict = mapping_dict

  #write the transform method without asserts. Again, maybe copy and paste from MappingTransformer and fix up.   
  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'RenamingTransformer.transform expected Dataframe but got {type(X)} instead.'
    #your assert code below

    column_set = set(X.columns)
    not_found = set(self.mapping_dict.keys()) - column_set
    assert not not_found, f"Columns {not_found}, are not in the data table"

    X_ = X.copy()
    return X_.rename(columns=self.mapping_dict)
  
#chapter 4 asks for 2 new transformers

class Sigma3Transformer(BaseEstimator, TransformerMixin):
  def __init__(self, target_column):  
    self.target_column = target_column
    
  def fit(self, X, y = None):
    print(f"Warning: {self.__class__.__name__}.fit does nothing.")
    return self

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
    X_ = X.copy()
    mean = X_[self.target_column].mean()
    sigma = X_[self.target_column].std()
    high_wall = mean + 3*sigma
    low_wall = mean - 3*sigma
    #print(f'{self.__class__.__name__} mean, sigma, low_wall, high_wall: {round(mean, 2)}, {round(sigma, 2)}, {round(low_wall, 2)}, {round(high_wall, 2)}')
    X_[self.target_column] = X_[self.target_column].clip(lower=low_wall, upper=high_wall)
    return X_

  def fit_transform(self, X, y = None):
    result = self.transform(X)
    return result

class TukeyTransformer(BaseEstimator, TransformerMixin):
  def __init__(self, target_column, fence='outer'):
    assert fence in ['inner', 'outer']
    self.target_column = target_column
    self.fence = fence
    
  def fit(self, X, y = None):
    print(f"Warning: {self.__class__.__name__}.fit does nothing.")
    return self

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
    if len(set(X[self.target_column]))<20:
      print(f'{self.__class__.__name__} warning: {self.target_column} has less than 20 unique values. Consider it as categorical?')
      
    X_ = X.copy()
    q1 = X_[self.target_column].quantile(0.25)
    q3 = X_[self.target_column].quantile(0.75)
    iqr = q3-q1
    inner_low = q1-1.5*iqr
    outer_low = q1-3*iqr
    inner_high = q3+1.5*iqr
    outer_high = q3+3*iqr
    #print(f'{self.__class__.__name__} inner_low, inner_high, outer_low, outer_high: {round(inner_low, 2)}, {round(outer_low, 2)}, {round(inner_high, 2)}, {round(outer_high, 2)}')
    if self.fence=='inner':
      X_[self.target_column] = X_[self.target_column].clip(lower=inner_low, upper=inner_high)
    elif self.fence=='outer':
      X_[self.target_column] = X_[self.target_column].clip(lower=outer_low, upper=outer_high)
    else:
      assert False, f"fence has unrecognized value {self.fence}"
      
    if len(set(X_[self.target_column]))<5:
      print(f'{self.__class__.__name__} warning: {self.target_column} has less than 5 unique values after clipping.')
      
    return X_

  def fit_transform(self, X, y = None):
    result = self.transform(X)
    return result

#chapter 5 asks for 1 new transformer

class MinMaxTransformer(BaseEstimator, TransformerMixin):
  def __init__(self):
    pass
    
  #fill in rest below
  def fit(self, X, y = None):
    print(f'Warning: {self.__class__.__name__}.fit does nothing.')
    return X

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
    X_ = X.copy()
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler()
    new_df = pd.DataFrame(scaler.fit_transform(X_), columns=X_.columns)
    return new_df

  def fit_transform(self, X, y = None):
    result = self.transform(X)
    return result
  
MinMaxTransformerWrapped = MinMaxTransformer  #for fall 22 bug

class MinMaxTransformerScratch(BaseEstimator, TransformerMixin):
  def __init__(self):
    self.column_stats = dict()

  #fill in rest below
  def fit(self, X, y = None):
    assert isinstance(X, pd.core.frame.DataFrame), f'MinMaxTransformer.fit expected Dataframe but got {type(X)} instead.'
    if y: print(f'Warning: {self.__class__.__name__}.fit did not expect a value for y but got {type(y)} instead.')
    self.column_stats = {c:(X[c].min(),X[c].max()) for c in X.columns.to_list()}
    return X

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
    assert self.column_stats, f'{self.__class__.__name__}.transform expected fit method to be called prior.'
    X_ = X.copy()
    fit_columns = set(self.column_stats.keys())
    transform_columns = set(X_.columns.to_list())
    not_fit = transform_columns - fit_columns
    not_transformed = fit_columns - transform_columns
    if not_fit: print(f'Warning: {self.__class__.__name__}.transform has more columns than fit: {not_fit}.')
    if not_transformed: print(f'Warning: {self.__class__.__name__}.transform has fewer columns than fit: {not_transformed}.')

    for c in fit_columns:
      if c not in transform_columns: continue
      cmin,cmax = self.column_stats[c]
      denom = cmax-cmin
      if not denom:
        print(f'Warning: column {c} has same min and max. No change made.')
      else:
        new_col = [(v-cmin)/denom for v in X_[c].to_list()]  #note NaNs remain NaNs - nice
        X_[c] = new_col
    
    return X_

  def fit_transform(self, X, y = None):
    self.fit(X,y)
    result = self.transform(X)
    return result

##added in chapter 6

class KNNTransformer(BaseEstimator, TransformerMixin):
  def __init__(self,n_neighbors=5, weights="uniform"):
    #your code
    self.n_neighbors = n_neighbors
    self.weights=weights 

  def fit(self, X, y = None):
    print(f'Warning: KNNTransformer.fit does nothing.')
    return X

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'KNNTransformer.transform expected Dataframe but got {type(X)} instead.'
    X_ = X.copy()
    from sklearn.impute import KNNImputer
    imputer = KNNImputer(n_neighbors=self.n_neighbors, weights=self.weights, add_indicator=False)  #if True will screw up column match
    columns = X_.columns
    matrix = imputer.fit_transform(X_)
    result_df = pd.DataFrame(matrix,columns=columns)
    return result_df

  def fit_transform(self, X, y = None):
    result = self.transform(X)
    return result

class IterativeTransformer(BaseEstimator, TransformerMixin):
  def __init__(self, estimator, max_iter=10, random_state=1234):
    self.estimator = estimator
    self.max_iter=max_iter 
    self.random_state=random_state

  #your code
  def fit(self, X, y = None):
    print(f'Warning: {self.__class__.__name__}.fit does nothing.')
    return X

  def transform(self, X):
    assert isinstance(X, pd.core.frame.DataFrame), f'{self.__class__.__name__}.transform expected Dataframe but got {type(X)} instead.'
    X_ = X.copy()
    imputer = IterativeImputer(estimator=self.estimator, max_iter=self.max_iter, random_state=self.random_state)
    columns = X_.columns
    matrix = imputer.fit_transform(X_)
    result_df = pd.DataFrame(matrix,columns=columns)
    return result_df

  def fit_transform(self, X, y = None):
    result = self.transform(X)
    return result

#chapter 7 add

from sklearn.metrics import f1_score#, balanced_accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegressionCV
from sklearn.neighbors import KNeighborsClassifier


from sklearn.metrics import f1_score  #typical metric used to measure goodness of a model

def find_random_state(features_df, labels, transformer, n=200):
  model = KNeighborsClassifier(n_neighbors=5)

  Var = []  #collect test_f1/train_f1
  for i in range(1, n):
    train_X, test_X, train_y, test_y = train_test_split(features_df, labels, test_size=0.2, shuffle=True,
                                                    random_state=i, stratify=labels)

    #apply pipeline
    transform_train_X = transformer.fit_transform(train_X, train_y)
    transform_test_X = transformer.transform(test_X)

    model.fit(transform_train_X, train_y)  #train model
    train_pred = model.predict(transform_train_X)  #predict against training set
    test_pred = model.predict(transform_test_X)    #predict against test set
    train_f1 = f1_score(train_y, train_pred)  #how well did we do with prediction on training data?
    
    if train_f1 < .1:
        continue  # Skip if train_f1 is too low or zero
        
    test_f1 = f1_score(test_y, test_pred)     #how well did we do with prediction on test data?
    f1_ratio = test_f1/train_f1        #take the ratio - closer to 1 the better
    Var.append(f1_ratio)

  mean = np.mean(Var)
  rs_value = np.abs(Var - mean).argmin()  # Returns index of value closest to mean

  return rs_value, Var


import matplotlib.pyplot as plt

def heat_map(zipped, label_list=(0,1)):
  zlist = list(zipped)
  case_list = []
  for i in range(len(label_list)):
    inner_list = []
    for j in range(len(label_list)):
      inner_list.append(zlist.count((label_list[i], label_list[j])))
    case_list.append(inner_list)


  fig, ax = plt.subplots(figsize=(5, 5))
  ax.imshow(case_list)
  ax.grid(False)
  title = ''
  for i,c in enumerate(label_list):
    title += f'{i}={c} '
  ax.set_title(title)
  ax.set_xlabel('Predicted outputs', fontsize=16, color='black')
  ax.set_ylabel('Actual outputs', fontsize=16, color='black')
  ax.xaxis.set(ticks=range(len(label_list)))
  ax.yaxis.set(ticks=range(len(label_list)))
  
  for i in range(len(label_list)):
      for j in range(len(label_list)):
          ax.text(j, i, case_list[i][j], ha='center', va='center', color='white', fontsize=32)
  plt.show()
  return None

#ch9

titanic_transformer = Pipeline(steps=[
    ('drop', CustomDropColumnsTransformer(['Age', 'Gender', 'Class', 'Joined', 'Married',  'Fare'], 'keep')),
    ('map_gender', CustomMappingTransformer('Gender', {'Male': 0, 'Female': 1})),
    ('map_class', CustomMappingTransformer('Class', {'Crew': 0, 'C3': 1, 'C2': 2, 'C1': 3})),
    ('target_joined', CustomTargetTransformer(cols=['Joined'], smoothing=10)),
    ('tukey_age', CustomTukeyTransformer(target_column='Age', fence='outer')),
    ('tukey_fare', CustomTukeyTransformer(target_column='Fare', fence='outer')),
    ('scale_age', CustomRobustTransformer('Age')),
    ('scale_fare', CustomRobustTransformer('Fare')),
    ('impute', CustomKNNTransformer(n_neighbors=5)),
    ], verbose=True)

customer_transformer = Pipeline(steps=[
    ('map_os', CustomMappingTransformer('OS', {'Android': 0, 'iOS': 1})),
    ('target_isp', CustomTargetTransformer(cols=['ISP'])),
    ('map_level', CustomMappingTransformer('Experience Level', {'low': 0, 'medium': 1, 'high':2})),
    ('map_gender', CustomMappingTransformer('Gender', {'Male': 0, 'Female': 1})),
    ('tukey_age', CustomTukeyTransformer('Age', 'inner')),  #from chapter 4
    ('tukey_time spent', CustomTukeyTransformer('Time Spent', 'inner')),  #from chapter 4
    ('scale_age', CustomRobustTransformer(target_column='Age')), #from 5
    ('scale_time spent', CustomRobustTransformer(target_column='Time Spent')), #from 5
    ('impute', KNNImputer(n_neighbors=5, weights="uniform", add_indicator=False)),
    ], verbose=True)

def dataset_setup(full_table, label_column_name, the_transformer, rs, ts=.2):
  feature_table = full_table.drop(columns=label_column_name)
  labels = full_table[label_column_name].to_list()
  X_train, X_test, y_train, y_test  = train_test_split(feature_table, labels, test_size=ts, shuffle=True,
                                                    random_state=rs, stratify=labels)
  X_train_transformed = the_transformer.fit_transform(X_train)
  X_test_transformed = the_transformer.fit_transform(X_test)
  x_trained_numpy = X_train_transformed.to_numpy()
  x_test_numpy = X_test_transformed.to_numpy()
  y_train_numpy = np.array(y_train)
  y_test_numpy = np.array(y_test)
  return x_trained_numpy, x_test_numpy, y_train_numpy,  y_test_numpy

def titanic_setup(titanic_table, transformer=titanic_transformer, rs=40, ts=.2):
  return dataset_setup(titanic_table, 'Survived', transformer, rs=rs, ts=ts)

def customer_setup(customer_table, transformer=customer_transformer, rs=76, ts=.2):
  return dataset_setup(customer_table, 'Rating', transformer, rs=rs, ts=ts)

def threshold_results(thresh_list, actuals, predicted):
  result_df = pd.DataFrame(columns=['threshold', 'precision', 'recall', 'f1', 'accuracy'])
  for t in thresh_list:
    yhat = [1 if v >=t else 0 for v in predicted]
    #note: where TP=0, the Precision and Recall both become 0
    precision = precision_score(actuals, yhat, zero_division=0)
    recall = recall_score(actuals, yhat, zero_division=0)
    f1 = f1_score(actuals, yhat)
    accuracy = accuracy_score(actuals, yhat)
    result_df.loc[len(result_df)] = {'threshold':t, 'precision':precision, 'recall':recall, 'f1':f1, 'accuracy':accuracy}

  result_df = result_df.round(2)

  #Next bit fancies up table for printing. See https://betterdatascience.com/style-pandas-dataframes/
  #Note that fancy_df is not really a dataframe. More like a printable object.
  headers = {
    "selector": "th:not(.index_name)",
    "props": "background-color: #800000; color: white; text-align: center"
  }
  properties = {"border": "1px solid black", "width": "65px", "text-align": "center"}

  fancy_df = result_df.style.format(precision=2).set_properties(**properties).set_table_styles([headers])
  return (result_df, fancy_df)

def halving_search(model, grid, x_train, y_train, factor=3, scoring='roc_auc'):
  #your code below
  halving_cv = HalvingGridSearchCV(
    model, grid,  #our model and the parameter combos we want to try
    scoring=scoring,  #could alternatively choose f1, accuracy or others
    n_jobs=-1,
    min_resources="exhaust",
    factor=factor,  #a typical place to start so triple samples and take top 3rd of combos on each iteration
    cv=5, random_state=1234,
    refit=True  #remembers the best combo and gives us back that model already trained and ready for testing
)

  grid_result = halving_cv.fit(x_train, y_train)
  return grid_result
