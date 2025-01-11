
import pandas as pd
from tqdm import tqdm
import numpy as np
from typing import List


def calculate_series_z_score(abundance_series: pd.Series) -> pd.Series:
    """
    Calculate modified Z-scores for a series based on median and MAD.

    This function computes Z-scores by centering data around the median
    and normalizing using the median absolute deviation (MAD). It is
    useful for identifying outliers in distributions that may not be
    normal, as it is more robust against outliers than standard Z-scores.

    Args:
        abundance_series (pd.Series): Series of values for Z-score calc.

    Returns:
        pd.Series: Series of Z-scores for each element in input series.
    """
    overall_median = abundance_series.median()

    # Get median absolute deviation
    MAD = (abs(abundance_series - overall_median)).median()

    # Compute Z Score
    if MAD != 0:
        z_scores = (abundance_series - overall_median) / MAD
        z_scores = z_scores.where(~abundance_series.isna(), np.nan)
    else:
        z_scores = pd.Series([0] * len(abundance_series), \
                             index=abundance_series.index)
    z_scores = z_scores.where(~abundance_series.isna(), np.nan)
    return z_scores

def get_z_scores(df: pd.DataFrame, 
                 colname: str="Abundance",
                 groupbycols: list[str]=["Genes", "Precursor.Id"],
                 zcolname: str="Z Score") -> pd.DataFrame:
    """
    Calculate Z-scores within groups in a DataFrame and add as a new column.

    This function groups the DataFrame by specified columns, calculates
    modified Z-scores for each group based on a specified column, and
    adds the scores as a new column.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        colname (str): Name of the column to calculate Z-scores on.
        groupbycols (list[str]): Columns to group by when calculating.
        zcolname (str): Name of the column to store calculated Z-scores.

    Returns:
        pd.DataFrame: The original DataFrame with Z-scores added.
    """
    
    df[zcolname] = df.groupby(groupbycols, observed=False)[colname] \
        .transform(calculate_series_z_score)

    return df

def get_median_zscore(df: pd.DataFrame,
    zcolname: str="Z Score",
    groupbycols: List[str]=['Genes', 'Precursor.Id','Compound'],
    mediancolname: str="Median"
    ) -> pd.DataFrame:
    """
    Compute and add a median Z-score column to the DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame containing the data.
        zcolname (str): Name of the column with Z-scores to calculate medians.
        groupbycols (List[str]): Columns to group by, in hierarchical order.
        mediancolname (str): Name of the new column for the median Z-scores.

    Returns:
        pd.DataFrame: The input DataFrame with an added median Z-score column.
    """

    df[mediancolname] = (
        df.groupby(groupbycols, observed=False)[zcolname].transform('median')
    )

    return df 



def get_median_zscore_df(
    df: pd.DataFrame,
    zcolname: str = "Z Score",
    groupbycols: List[str] = ['Genes', 'Precursor.Id', 'Compound']
    ) -> pd.DataFrame:
    """ 
    Compute median Z-scores within subgroups and return a new DataFrame.

    This function calculates the median Z-score within groups of a DataFrame,
    grouped by the specified columns. It then returns a DataFrame with unique
    combinations of grouping columns and their corresponding median Z-scores.
    
    It looks like a dumb way to do things, but if there are several genes,
    precursor.Ids, Compounds, this is actually more memory efficient than
    groupby.

    Args:
        df (pd.DataFrame): The input DataFrame containing the data.
        zcolname (str): Name of the column with Z-scores to calculate medians.
        groupbycols (list[str]): Columns to group by, in hierarchical order.

    Returns:
        pd.DataFrame: A new DataFrame with unique groups and median Z-scores.
    """
    gene_colname = groupbycols[0]
    df_list = []
    for gene in tqdm(df[gene_colname],
                      desc="Computing median z scores",
                      unit="gene"):
        subdf = df.loc[df[gene_colname]==gene]
        subdf["Median"] =  subdf.groupby(groupbycols[1:], observed=False) \
            [zcolname].transform('median')
        unique_combos = subdf[groupbycols + ["Median"]].drop_duplicates()
        df_list.append(unique_combos)
    return pd.concat(df_list)
          