export declare class ShowdownClient {
    private ws;
    private battleState;
    private serverUrl;
    private username;
    private password;
    private isConnected;
    private isInBattle;
    constructor(serverUrl: string | undefined, username: string, password: string, calcServiceUrl?: string, policyServiceUrl?: string);
    connect(): Promise<void>;
    disconnect(): Promise<void>;
    private authenticate;
    private handleMessage;
    private handleChallengeString;
    private handleUserUpdate;
    private handleBattleStart;
    private handleBattleInit;
    private handleBattleRequest;
    private handleTurn;
    private handleBattleEnd;
    private makeBattleDecision;
    private sendAction;
    private sendFallbackAction;
    private send;
    challengeUser(username: string, format?: string): Promise<void>;
    acceptChallenge(): Promise<void>;
    rejectChallenge(): Promise<void>;
    getBattleState(): any;
    getBattleStateJSON(): string;
}
//# sourceMappingURL=showdown-client.d.ts.map