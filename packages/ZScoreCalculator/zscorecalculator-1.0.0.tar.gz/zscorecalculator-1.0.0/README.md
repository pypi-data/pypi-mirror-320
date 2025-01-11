# Z Score Calculator
A package for calculating z scores to determine functional effects and target engagement.

## Installation
```pip install ZScoreCalculator```

## Protein Functionl Effects
Calculate Z scores for protein abundance. 

A quick example. Data should be melted so abundance is a column.
```
from z_score_calculator import *

z_scores = get_z_scores(data, groupbycols=["Genes"])

# Get the median z scores for each protein and compound
z_scores = get_median_zscore(z_scores
                             zcolname="Z Score",                  # column to calculate z scores
                             groupbycols=["Genes", "Compound"],
                             mediancolname="Median Z Score",      # name for the new median column
)
```

## Target Engagement
Calculate Z scores for peptide abundance. And Z scores of Z scores to separate any confounding functional effects.

A quick example. Data should be melted so that abundance and Precursor.Id are columns.
```
from z_score_calculator import *

z_scores = get_z_scores(data) # by default, will group by "Genes" and "Precursor.Id" columns

# Calculate the z scores of the z scores to separate functional effects
z_scores = get_z_scores(data,
                        colname="Z Score",                  # column to calculate z scores
                        groupbycols=["Genes", "Compound"],  # groupby compound so eliminate functional effects
                        zcolname="Z of Z Score",            # name for the new z score column
)

# Get the median z scores for each peptide and compound
# Often the get_median_zscore function can take too long due to the factorially scaling groupby function
# The get_medain_zscore_df creates a whole new data frame and uses a loop instead of groupby
median_zscore_df = get_median_zscore_df(z_scores,
                                        zcolname="Z Scores" # column to calculate z scores
                                        groupbycols=["Genes", "Precursor.Id", "Compound"]
)
```
