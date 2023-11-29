from rules.high_loud import init_highloud, init_highlong
from rules.metrical_amp import init_metrical_amp
from rules.metrical_dur import init_metrical_dur
from rules.decrease_amp import init_decrease_amp
from rules.decrease_dur import init_decrease_dur

from rules.final_ritardando import init_final_ritardando
from rules.melodic_charge import init_melodic_charge

allRules = {
    'high loud': init_highloud,
    'high long': init_highlong,

    'metrical amp': init_metrical_amp,
    'metrical dur': init_metrical_dur,
    'decrease amp': init_decrease_amp,
    'decrease dur': init_decrease_dur,

    'final ritardando': init_final_ritardando,
    'melodic charge': init_melodic_charge,
}