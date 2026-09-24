"""Plot actual same-coordinate checkpoint controls, with no interpolation claim."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
data=json.loads((OUT/'failure_mechanisms/gate_jump_controls.json').read_text())
fig,axs=plt.subplots(2,2,figsize=(10,7),sharex=True,sharey='row',layout='constrained')
for ax,r in zip(axs.flat,data['rows']):
    col=8 if r['kappa']<.5 else 10
    for control,color in zip(r['controls'],['#276FBF','#CC6B32']):
        ax.plot([x['p'] for x in control['noise']],[x['observables'][col] for x in control['noise']],'o-',color=color,label=f"{control['cnots']} actual CNOTs")
    ax.set(title=f"kappa={r['kappa']}, h={r['h']}",xlabel='target depolarization p',ylabel='m0 squared' if col==8 else 'm(pi/2) squared');ax.legend()
fig.suptitle('Same Hamiltonian, same reference/seed, different saved growth checkpoint\nExploratory control; parameters and gates both change, no reoptimization')
folder=OUT/'failure_mechanisms/figures';folder.mkdir(exist_ok=True)
fig.savefig(folder/'gate_jump_noise_controls.png',dpi=170);plt.close(fig)
print('Gate-jump control plot saved')
