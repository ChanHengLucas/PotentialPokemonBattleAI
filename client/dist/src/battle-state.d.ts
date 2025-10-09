import { BattleState, Action, LegalAction } from '../data/schemas/battle-state';
export declare class BattleStateManager {
    private state;
    private websocket;
    private calcServiceUrl;
    private policyServiceUrl;
    constructor(websocket: any, calcServiceUrl?: string, policyServiceUrl?: string);
    private initializeEmptyState;
    getState(): BattleState;
    toJSON(): string;
    getLegalActions(): Promise<LegalAction[]>;
    getOptimalAction(): Promise<Action | null>;
    private getCalcResults;
    private getPolicyRecommendation;
    private convertToAction;
    updateFromShowdownMessage(message: any): void;
    private handleInitMessage;
    private handlePlayerMessage;
    private handlePokeMessage;
    private handleSwitchMessage;
    private handleMoveMessage;
    private handleTurnMessage;
    private handleWinMessage;
    private handleFieldMessage;
    private handleSideMessage;
    private parsePokemonData;
    private addLogEntry;
    updateOpponentModel(): void;
    applySafetyLayer(action: Action, legalActions: LegalAction[]): Action;
    private getFallbackAction;
    private calculateHazardDamage;
    private shouldPreserveRoleHolder;
}
//# sourceMappingURL=battle-state.d.ts.map