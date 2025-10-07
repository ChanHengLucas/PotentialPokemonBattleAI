function clamp(val, min = 0, max = 1) {
    return Math.max(min, Math.min(max, val));
}
export function evaluateActionsSimple(req) {
    const { battleState, actions } = req;
    const myActive = battleState.sides.me.active;
    const oppActive = battleState.sides.opponent.active;
    const speedRelation = myActive.stats.spe > oppActive.stats.spe
        ? 'outspeed'
        : myActive.stats.spe === oppActive.stats.spe
            ? 'speed_tie'
            : 'underspeed';
    return actions.map((action) => {
        if (action.type === 'MOVE') {
            const move = myActive.moves.find((m) => m.id === action.moveId);
            const baseAcc = move ? move.accuracy : 1.0;
            const basePower = move ? move.basePower : 0;
            // Very naive placeholder: scale damage by base power and ATK/SPA vs DEF/SPD
            const isPhysical = move?.category === 'Physical';
            const atkStat = isPhysical ? myActive.stats.atk : myActive.stats.spa;
            const defStat = isPhysical ? oppActive.stats.def : oppActive.stats.spd;
            const raw = basePower * (atkStat / Math.max(1, defStat));
            const maxDmg = Math.min(100, raw / 2); // arbitrary scaling to percent
            const minDmg = maxDmg * 0.85;
            const ohkoProb = maxDmg >= oppActive.hp.percent ? baseAcc : 0;
            const twohkoProb = maxDmg * 2 >= oppActive.hp.percent ? baseAcc : 0;
            const expectedDamagePercent = clamp((minDmg + maxDmg) / 2 / 100) * 100 * baseAcc;
            return {
                action,
                accuracy: clamp(baseAcc),
                minDamagePercent: clamp(minDmg / 100) * 100,
                maxDamagePercent: clamp(maxDmg / 100) * 100,
                ohkoProb: clamp(ohkoProb),
                twohkoProb: clamp(twohkoProb),
                speedControl: speedRelation,
                hazardOnSwitchPercent: 0,
                expectedDamagePercent: clamp(expectedDamagePercent / 100) * 100,
                survivalProb: 1 - clamp(expectedDamagePercent / Math.max(1, myActive.hp.percent)),
                expectedNetGain: (expectedDamagePercent - 0) / 100,
            };
        }
        if (action.type === 'SWITCH') {
            const entryHazard = estimateHazardDamagePercent(battleState.sides.me.hazards, myActive.types);
            return {
                action,
                accuracy: 1,
                minDamagePercent: 0,
                maxDamagePercent: 0,
                ohkoProb: 0,
                twohkoProb: 0,
                speedControl: speedRelation,
                hazardOnSwitchPercent: entryHazard,
                expectedDamagePercent: 0,
                survivalProb: 1,
                expectedNetGain: -entryHazard / 100,
            };
        }
        // TERASTALLIZE - placeholder neutral effect
        return {
            action,
            accuracy: 1,
            minDamagePercent: 0,
            maxDamagePercent: 0,
            ohkoProb: 0,
            twohkoProb: 0,
            speedControl: speedRelation,
            hazardOnSwitchPercent: 0,
            expectedDamagePercent: 0,
            survivalProb: 1,
            expectedNetGain: 0,
        };
    });
}
function estimateHazardDamagePercent(hazards, types) {
    let percent = 0;
    if (hazards.stealthRock) {
        // Simplified: base 12.5% SR, ignore type modifiers for now
        percent += 12.5;
    }
    if (hazards.spikes) {
        percent += [0, 12.5, 16.67, 25][hazards.spikes] ?? 0;
    }
    return percent;
}
