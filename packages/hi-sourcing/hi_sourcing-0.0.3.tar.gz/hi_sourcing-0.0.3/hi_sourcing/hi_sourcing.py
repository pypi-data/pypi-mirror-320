# ************************************************************************************
# ***                C O N F I D E N T I A L  --  H I - S O U R C I N G          ***
# ************************************************************************************
# *                                                                                  *
# *                Project Name : Hi-Sourcing Utilities                              *
# *                                                                                  *
# *                File Name : hi_sourcing.py                                        *
# *                                                                                  *
# *                Programmer : Jinwen Liu                                           *
# *                                                                                  *
# *                Start Date : January 9, 2025                                      *
# *                                                                                  *
# *                Last Update : January 9, 2025                                     *
# *                                                                                  *
# *                Version : 0.0.3                                                   *
# *                                                                                  *
# *-------------------------------------------------------------------------------*
# * Class Description:                                                              *
# *   HiSourcing -- Main class for performing similarity-based data sourcing       *
# *   Uses FAISS (Facebook AI Similarity Search) to find similar entries in a      *
# *   database based on a query dataset. Supports filtering by labels and custom   *
# *   column removal.                                                              *
# *                                                                                *
# * Functions:                                                                     *
# *   Public:                                                                      *
# *   - __init__ -- Initialize with query/database DataFrames and label column    *
# *   - remove_columns_from_df -- Removes specified columns from DataFrames       *
# *   - set_fillna_method -- Sets method for handling NaN values                  *
# *   - fillna -- Fills NaN values using specified method                         *
# *   - run -- Performs similarity search using FAISS after filtering by label    *
# *   - sourcing -- Returns the sourcing results as a DataFrame                   *
# *   - validate -- Compares label counts before and after sourcing              *
# *   Private:                                                                     *
# *   - _get_credentials -- Internal method for credential verification           *
# *       - Prompts user for credentials and returns the input credential        *
# *       - Used for access control in the run method                            *
# *                                                                                *
# * Parameters:                                                                    *
# *   query_df -- DataFrame containing the query data, which is features with labels                                *
# *   db_df -- DataFrame containing the database to search within                 *
# *   label -- Column name for label-based filtering                              *
# *   remove_columns -- List of columns to remove before similarity search        *
# *   fillna_method -- Method to handle missing values                            *
# *   k -- Number of nearest neighbors to retrieve                                *
# *   credentials -- Optional credentials for access control                       *
# *                                                                                *
# *******************************************************************************/

import pandas as pd
import numpy as np
import faiss
import tkinter as tk
from tkinter import simpledialog


class HiSourcing:
    def __init__(self,
                 query_df: pd.DataFrame,
                 db_df: pd.DataFrame,
                 label: str,
                 remove_columns: list[str] = [],
                 fillna_method: str = 'zero',
                 k: int = 1000,
                 credentials: str = None
    ):
        self.raw_query_df = query_df
        self.raw_db_df = db_df
        
        self.label = label
        self.remove_columns = remove_columns

        self.fillna_method = fillna_method
        self.k = k
        self.D = None
        self.I = None
        self.credentials = credentials
        # self.run()

    
    def remove_columns_from_df(self, df):
        return df.drop(self.remove_columns, axis=1)

    def set_fillna_method(self, method):
        self.fillna_method = method

    def fillna(self, df):
        if self.fillna_method == 'zero':
            return df.fillna(0)
        elif self.fillna_method == 'mean':
            return df.fillna(df.mean())
        elif self.fillna_method == 'median':
            return df.fillna(df.median())
        elif self.fillna_method == 'mode':
            return df.fillna(df.mode())
        elif self.fillna_method == 'max':
            return df.fillna(df.max())
        elif self.fillna_method == 'min':
            return df.fillna(df.min())
        else:
            print("Invalid fillna_method. Please choose from ['zero', 'mean', 'median', 'mode', 'max', 'min'].")
            return
    
    def _get_credentials(self):
        """
        Internal method for credential verification.

        Prompts user for credentials and returns the input credential.
        Used for access control in the run method.
        """
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        credential = simpledialog.askstring("Credential Required", "Please enter your credentials:", show='*')
        return credential

    def run(self):
        input_credential = self._get_credentials()
        if input_credential != 'hijinwen':
            print("Access denied: Invalid credentials")
            return
            
        try:
            # keep rows with only label=1
            self.query_df = self.raw_query_df[self.raw_query_df[self.label]==1]
            # remove label columns
            self.query_df = self.remove_columns_from_df(self.query_df)

            # remove label columns
            self.db_df = self.remove_columns_from_df(self.raw_db_df)
            
            # faiss does not take nan
            self.query_df = self.fillna(self.query_df)
            self.db_df = self.fillna(self.db_df)
            
            # faiss
            index = faiss.IndexFlatL2(self.query_df.shape[1])
            index.add(self.db_df)
            
            self.D, self.I = index.search(self.query_df, self.k)

            self.indices = [index for sublist in self.I for index in sublist]
            
            # return prediction df has no label
            self.return_df = self.db_df.iloc[self.indices]
            self.return_df = self.return_df.drop_duplicates()
        except:
            print("Error running sourcing")
        
    def sourcing(self):
        return self.return_df

    def validate(self):
        try:
            # labels in db_db
            self.label_before_sourcing = self.raw_db_df[self.raw_db_df[self.label]==1].shape[0]
            
            # return prediction df has no label
            self.df_after_sourcing = self.raw_db_df.iloc[self.indices]
            self.df_after_sourcing = self.df_after_sourcing.drop_duplicates()
            self.label_after_sourcing = self.df_after_sourcing[self.df_after_sourcing[self.label]==1].shape[0] 

            print ("Label before sourcing: " + str(self.label_before_sourcing))
            print ("Label after sourcing: " + str(self.label_after_sourcing))

            print ("number of rows before sourcing: " + str(self.raw_db_df.shape[0]))
            print ("number of rows after sourcing: " + str(self.df_after_sourcing.shape[0]))
        except:
            print("Error Validating")
