import unittest
import pandas as pd
from pandas.testing import assert_series_equal
from numpy import nan
from z_score_calculator.calculator import *


class TestCalculateSeriesZScore(unittest.TestCase):

    def test_standard_case(self):
        """Test with a typical series of numbers."""
        series = pd.Series([1, 2, 3, 4, 5, 6, 7])
        z_scores = calculate_series_z_score(series)
        self.assertAlmostEqual(z_scores.mean(), 0, delta=0.1)
        self.assertAlmostEqual(z_scores.median(), 0, delta=0.1)

    def test_constant_series(self):
        """Test with a series where all values are the same (MAD=0)."""
        series = pd.Series([5, 5, 5, 5, 5])
        z_scores = calculate_series_z_score(series)
        self.assertTrue((z_scores == 0).all(), "All Z-scores should be zero.")

    def test_single_value_series(self):
        """Test with a series that has only one value."""
        series = pd.Series([10])
        z_scores = calculate_series_z_score(series)
        self.assertTrue((z_scores == 0).all(), "Z-score should be zero for single value.")

    def test_empty_series(self):
        """Test with an empty series."""
        series = pd.Series([], dtype=float)
        z_scores = calculate_series_z_score(series)
        self.assertTrue(z_scores.empty, "Z-score for empty series should be empty.")

    def test_with_nan_values(self):
        """Test with a series containing NaN values."""
        series = pd.Series([1, 2, nan, 4, 5])
        z_scores = calculate_series_z_score(series)
        self.assertTrue(z_scores.hasnans, "Z-scores should contain NaNs.")
        self.assertTrue(pd.isna(z_scores[2]), "NaN values should be preserved.")

    def test_outliers(self):
        """Test that outliers have high Z-scores."""
        series = pd.Series([1, 2, 3, 4, 100])
        z_scores = calculate_series_z_score(series)
        self.assertGreater(z_scores.iloc[-1], 3, "Outlier should have high Z-score.")
        self.assertAlmostEqual(z_scores.median(), 0, delta=0.1)

class TestGetZScores(unittest.TestCase):

    def setUp(self):
        """Set up a sample DataFrame for testing."""
        self.df = pd.DataFrame({
            "Genes": ["gene1", "gene1", "gene2", "gene2", "gene3"],
            "Precursor.Id": ["A", "A", "B", "B", "C"],
            "Abundance": [1, 2, 3, 4, 5]
        })

    def test_z_scores_basic_functionality(self):
        """Test basic functionality with default parameters."""
        result_df = get_z_scores(self.df)
        self.assertIn("Z Score", result_df.columns, "Z Score column should be added.")
        self.assertEqual(len(result_df), len(self.df), "Result should have same number of rows.")

    def test_custom_column_names(self):
        """Test with custom column names for colname and zcolname."""
        custom_df = self.df.rename(columns={"Abundance": "Intensity"})
        result_df = get_z_scores(custom_df, colname="Intensity", zcolname="Z Intensity")
        self.assertIn("Z Intensity", result_df.columns, "Custom Z-score column name should be added.")
        self.assertNotIn("Z Score", result_df.columns, "Default Z Score column should not be added.")

    def test_empty_dataframe(self):
        """Test with an empty DataFrame."""
        empty_df = pd.DataFrame(columns=["Genes", "Precursor.Id", "Abundance"])
        result_df = get_z_scores(empty_df)
        self.assertTrue(result_df.empty, "Result should be empty for an empty input DataFrame.")
        self.assertIn("Z Score", result_df.columns, "Z Score column should still be added.")

    def test_nan_handling(self):
        """Test that NaN values in the original column do not break calculation."""
        nan_df = self.df.copy()
        nan_df.loc[1, "Abundance"] = float("nan")
        result_df = get_z_scores(nan_df)
        self.assertTrue(result_df["Z Score"].isna().iloc[1], "Z Score should be NaN where original value is NaN.")
        self.assertFalse(result_df["Z Score"].isna().all(), "Not all Z Scores should be NaN.")
        expected = pd.Series([0, float("nan"), -1, 1, 0])
        expected.name = "Z Score"
        assert_series_equal(result_df["Z Score"], expected, check_exact=True)

    def test_groupby_functionality(self):
        """Test that Z-scores are calculated within groups correctly."""
        group_df = pd.DataFrame({
            "Genes": ["gene1", "gene1", "gene2", "gene2", "gene2"],
            "Precursor.Id": ["A", "A", "B", "B", "B"],
            "Abundance": [10, 20, 10, 20, 30]
        })
        result_df = get_z_scores(group_df)
        
        # Extract Z-scores for each group to verify they are calculated independently
        gene1_z_scores = result_df[result_df["Genes"] == "gene1"]["Z Score"]
        gene2_z_scores = result_df[result_df["Genes"] == "gene2"]["Z Score"]
        
        # Check that Z-scores within groups have mean close to 0
        self.assertAlmostEqual(gene1_z_scores.mean(), 0, delta=0.1, msg="Gene1 Z-scores should have mean ~0")
        self.assertAlmostEqual(gene2_z_scores.mean(), 0, delta=0.1, msg="Gene2 Z-scores should have mean ~0")
        self.assertEqual(len(gene1_z_scores), 2, "Gene1 should have 2 Z-scores")
        self.assertEqual(len(gene2_z_scores), 3, "Gene2 should have 3 Z-scores")

if __name__ == "__main__":
    unittest.main()