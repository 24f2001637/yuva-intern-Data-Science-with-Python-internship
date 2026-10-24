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
        for week,count in [('week01',5),('week02',6),('week03',4),('week04',4),('week05',1)]:
            folder = ROOT/'weeks'/week
            self.assertEqual(len(list((folder/'outputs').glob('*.png'))), count)
            self.assertEqual(len(list(folder.glob('*.docx'))), 1)
            for file in (folder/'outputs').glob('*.png'):
                self.assertGreater(file.stat().st_size, 1000)

    def test_model_split_and_saved_predictions(self):
        from sklearn.metrics import confusion_matrix, accuracy_score, roc_auc_score
        out=ROOT/'weeks/week04/outputs'
        split=pd.read_csv(out/'split.csv')
        predictions=pd.read_csv(out/'test_predictions.csv')
        raw=pd.read_csv(ROOT/'data/raw/titanic.csv')
        result=json.loads((out/'results.json').read_text())
        self.assertEqual(set(split.row_id),set(range(891)))
        self.assertFalse(split.row_id.duplicated().any())
        train=set(split.loc[split.split=='train','row_id'])
        test=set(split.loc[split.split=='test','row_id'])
        self.assertFalse(train & test)
        self.assertEqual((len(train),len(test)),(712,179))
        self.assertEqual(set(predictions.row_id),test)
        self.assertFalse(predictions.row_id.duplicated().any())
        self.assertEqual(predictions.actual.tolist(),raw.loc[predictions.row_id,'survived'].tolist())
        p=predictions[result['selected_model']]
        self.assertTrue(p.between(0,1).all())
        pred=(p>=result['threshold']).astype(int)
        self.assertEqual(confusion_matrix(predictions.actual,pred).tolist(),result['confusion_matrix'])
        metric=next(r for r in result['metrics'] if r['model']==result['selected_model'])
        self.assertAlmostEqual(accuracy_score(predictions.actual,pred),metric['accuracy'])
        self.assertAlmostEqual(roc_auc_score(predictions.actual,p),metric['roc_auc'])
        self.assertNotIn('alive',result['features'])
        self.assertNotIn('survived',result['features'])

    def test_synthesis_preserves_model_evidence(self):
        model=json.loads((ROOT/'weeks/week04/outputs/results.json').read_text())
        summary=json.loads((ROOT/'weeks/week05/outputs/project_summary.json').read_text())
        self.assertEqual(summary['dataset_sha256'],model['dataset_sha256'])
        self.assertEqual(summary['confusion_matrix'],model['confusion_matrix'])
        self.assertEqual(summary['test_n'],model['test_n'])

if __name__ == '__main__':
    unittest.main()
