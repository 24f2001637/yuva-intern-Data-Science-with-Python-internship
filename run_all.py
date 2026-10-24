"""Execute completed weeks in order using this Python interpreter."""
from pathlib import Path
import subprocess
import sys
ROOT = Path(__file__).resolve().parent
for week in ('week01','week02','week03','week04','week05'):
    print(f'Running {week}', flush=True)
    subprocess.run([sys.executable, str(ROOT/'weeks'/week/'analysis.py')],
                   cwd=ROOT, check=True)
print('All five supplied weeks completed. See each weeks/weekXX/outputs directory.')
