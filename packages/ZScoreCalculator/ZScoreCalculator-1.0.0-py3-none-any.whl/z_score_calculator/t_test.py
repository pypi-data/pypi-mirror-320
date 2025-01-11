import pandas as pd
import numpy as np
from scipy.stats import ttest_ind
from statsmodels.stats.multitest import multipletests

def ttest_zscores(df: pd.DataFrame,
                   zcolname: str="Z Score",
                   groupbycols: list=["Genes", "Precursor.Id", "Compound"],
                   ) -> pd.DataFrame:
    """
    Perform t-tests on Z scores grouped by specified columns.

    This function groups the input DataFrame by the specified columns and
    performs independent t-tests (Welch's t-test) for the Z scores of each
    group against the Z scores of all other groups combined. The results,
    including the t-statistic and p-value for each group, are returned in
    a new DataFrame.

    Parameters:
    ----------
    df : pd.DataFrame
        The input DataFrame containing the data.
    zcolname : str, optional
        The name of the column containing Z scores. Default is "Z Score".
    groupbycols : list, optional
        A list of column names to group the DataFrame by. Default is
        ["Genes", "Precursor.Id", "Compound"].

    Returns:
    -------
    pd.DataFrame
        A DataFrame containing the group keys, t-statistics, and p-values
        for each group. The columns include:
        - Each of the grouping columns specified in `groupbycols`.
        - `t_stat`: The t-statistic for the t-test.
        - `p_value`: The p-value for the t-test.
    """
        
    results = []
    groups = df.groupby(groupbycols, observed=False)

    for group_tuple, group in groups:
        # Z scores for this group
        specific_z_scores = group[zcolname]

        # Z scores for all other groups
        overall_z_scores = df[~df.index.isin(group.index)][zcolname]

        # Perform t-test if both groups have sufficient data
        if len(specific_z_scores) > 1 and len(overall_z_scores) > 1:
            t_stat, p_value = ttest_ind(
                specific_z_scores, overall_z_scores, equal_var=False
            )
        else:
            t_stat, p_value = np.nan, np.nan  # Not enough data for the test

        # Collect group information and results
        result_row = dict(zip(groupbycols, group_tuple))
        result_row.update({'t_stat': t_stat, 'p_value': p_value})
        results.append(result_row)

    return pd.DataFrame(results)

def correct_pvalues(df: pd.DataFrame, pcolname: str="p_value") -> pd.DataFrame:
    """
    Apply multiple testing correction to p-values in a DataFrame.

    This function adjusts p-values for multiple comparisons using the
    Benjamini-Hochberg method (False Discovery Rate). The corrected p-values
    are added as a new column to the DataFrame.

    Parameters:
    ----------
    df : pd.DataFrame
        The input DataFrame containing p-values.
    pcolname : str, optional
        The name of the column containing the p-values. Default is "p_value".

    Returns:
    -------
    pd.DataFrame
        The input DataFrame with an additional column:
        - `corrected_p_value`: The p-values corrected for multiple testing.
    """
    p_values = df[pcolname]
    _, corrected_p_values, _, _ = multipletests(p_values, method='fdr_bh')
    df['corrected_p_value'] = corrected_p_values
    return df