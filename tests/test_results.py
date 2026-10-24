"""Regression checks for denominators, inference and deliverable completeness.

Run after run_all.py. These checks guard against accidental deduplication,
imputed-age inference and changes to the declared statistical results.
"""
from pathlib import Path
import json
import unittest
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]

class AnalysisResults(unittest.TestCase):
    def test_passengers_and_observed_ages_preserved(self):
        data = pd.read_csv(ROOT/'data/processed/titanic_eda.csv')
        self.assertEqual(len(data), 891)
        self.assertEqual(int(data.survived.sum()), 342)
        self.assertEqual(int(data.age_observed.notna().sum()), 714)
        self.assertEqual(int(data.age_missing.sum()), 177)
        self.assertEqual(int(data.age.isna().sum()), 0)

    def test_statistics_match_documented_snapshot(self):
        result = json.loads((ROOT/'weeks/week03/outputs/results.json').read_text())
        tests = {row['test']: row for row in result['results']}
        self.assertEqual(tests['Mean age']['n'], 714)
        self.assertEqual(tests['Class']['n'], 891)
        self.assertAlmostEqual(tests['Sex']['statistic'], 263.0505740707, places=7)
        self.assertAlmostEqual(tests['Mean age']['p_holm'], .0411896516259, places=10)
        self.assertAlmostEqual(result['age']['difference'], -2.28248959011, places=9)
        self.assertLess(result['age']['ci'][1], 0)
        self.assertGreater(result['imputed_age_p'], .05)
        self.assertLess(result['port']['p'], .001)

    def test_required_figures_and_reports_exist(self):
        for week,count in [('week01',5),('week02',6),('week03',4)]:
            folder = ROOT/'weeks'/week
            self.assertEqual(len(list((folder/'outputs').glob('*.png'))), count)
            self.assertEqual(len(list(folder.glob('*.docx'))), 1)
            for file in (folder/'outputs').glob('*.png'):
                self.assertGreater(file.stat().st_size, 1000)

if __name__ == '__main__':
    unittest.main()
