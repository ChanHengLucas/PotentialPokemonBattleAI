import { BattleState, LegalAction, CalcResult } from './schemas/battle-state';
export declare class DamageCalculator {
    calculateDamage(battleState: BattleState, actions: LegalAction[]): Promise<CalcResult[]>;
    private calculateAction;
    private calculateMoveDamage;
    private calculateSwitchCost;
    private calculateTeraBenefit;
    private convertToCalcPokemon;
    private convertToCalcMove;
    private convertToCalcField;
    private convertToCalcSide;
    private calculateOHKOChance;
    private calculate2HKOChance;
    private isFaster;
    private getSpeedDifference;
    private getEffectiveSpeed;
    private calculateHazardDamage;
    private calculateStatusChance;
    private calculateSurvivalChance;
    private calculateExpectedGain;
    private createErrorResult;
    private createDefaultResult;
    private calculateSpeedCheck;
}
//# sourceMappingURL=calculator.d.ts.map