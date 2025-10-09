interface LadderConfig {
    format: string;
    maxGames: number;
    username: string;
    password: string;
    serverUrl: string;
    teamPath: string;
    logPath: string;
}
declare class LadderClient {
    private client;
    private config;
    private gameCount;
    private wins;
    private losses;
    constructor(config: LadderConfig);
    start(): Promise<void>;
    private loadTeam;
    private submitTeam;
    private convertTeamToShowdown;
    private ladderLoop;
    private requestBattle;
    private waitForBattle;
    private playBattle;
    private getLegalActions;
    private getOptimalAction;
    private getCalcResults;
    private getPolicyRecommendation;
    private applySafetyLayer;
    private getFallbackAction;
    private sendAction;
    private logTelemetry;
    private showStats;
    private showFinalStats;
    private sleep;
}
export { LadderClient };
//# sourceMappingURL=ladder.d.ts.map