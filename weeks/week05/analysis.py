"""Synthesize prior measured results without training or changing the test split."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent / 'outputs'

def main():
    OUT.mkdir(exist_ok=True)
    statistical = json.loads((ROOT/'weeks/week03/outputs/results.json').read_text())
    modeling = json.loads((ROOT/'weeks/week04/outputs/results.json').read_text())
    assert statistical['sha256'] == modeling['dataset_sha256']
    selected = next(r for r in modeling['metrics'] if r['model']==modeling['selected_model'])
    synthesis = {'dataset_rows':891, 'survivors':342,
        'dataset_sha256':statistical['sha256'],
        'statistical_results':statistical['results'],
        'selected_model':modeling['selected_model'], 'test_metrics':selected,
        'test_n':modeling['test_n'], 'confusion_matrix':modeling['confusion_matrix'],
        'scope':'Historical educational analysis; no causal effect or deployment impact estimated.'}
    (OUT/'project_summary.json').write_text(json.dumps(synthesis,indent=2)+'\n')
    tn,fp= modeling['confusion_matrix'][0]
    fn,tp= modeling['confusion_matrix'][1]
    fig,ax=plt.subplots(figsize=(7.2,3.7))
    names=['Correct non-survival','False survival','Missed survival','Correct survival']
    bars=ax.barh(names,[tn,fp,fn,tp],color=['#31688e','#d49055','#d49055','#35a18a'])
    ax.bar_label(bars,padding=4);ax.set(xlim=(0,115),xlabel='Test passengers',
        title='What 82.1% accuracy means across 179 test passengers')
    ax.spines[['top','right']].set_visible(False)
    fig.tight_layout();fig.savefig(OUT/'01_error_summary.png',dpi=170);plt.close(fig)
    recommendations = [
        ['Preserve raw data and split manifests','Analyst','Every rerun passes snapshot and split checks','Immediate'],
        ['Audit subgroup errors before model use','Model reviewer','Report recall and false positives with denominators','Immediate'],
        ['Validate on newly acquired independent records','Research lead','Independent performance and uncertainty reported','Before any external use'],
        ['Collect family IDs and operational variables','Data steward','Coverage and linkage quality measured','Next data collection'],
        ['Evaluate any operational intervention separately','Domain specialist','Predefined outcome and comparison design','Future research']]
    pd.DataFrame(recommendations,columns=['action','proposed_owner','success_measure','timing']).to_csv(
        OUT/'recommendations.csv',index=False)
    print('Week 5 synthesis regenerated from Weeks 3 and 4 outputs.')

if __name__=='__main__':
    main()
