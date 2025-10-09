"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DamageCalculator = void 0;
class DamageCalculator {
    async calculateDamage(battleState, actions) {
        const results = [];
        for (const action of actions) {
            try {
                const result = await this.calculateAction(battleState, action);
                results.push(result);
            }
            catch (error) {
                console.error(`Error calculating action ${action.type}:`, error);
                results.push(this.createErrorResult(action));
            }
        }
        return results;
    }
    async calculateAction(battleState, action) {
        const active = battleState.p1.active;
        const opponent = battleState.p2.active;
        if (!active || !opponent) {
            return this.createErrorResult(action);
        }
        switch (action.type) {
            case 'move':
                return await this.calculateMoveDamage(battleState, action, active, opponent);
            case 'switch':
                return await this.calculateSwitchCost(battleState, action);
            case 'tera':
                return await this.calculateTeraBenefit(battleState, action);
            default:
                return this.createDefaultResult(action);
        }
    }
    async calculateMoveDamage(battleState, action, attacker, defender) {
        const move = attacker.moves.find((m) => m.id === action.move);
        if (!move) {
            return this.createErrorResult(action);
        }
        // Convert to @smogon/calc format
        const calcAttacker = this.convertToCalcPokemon(attacker);
        const calcDefender = this.convertToCalcPokemon(defender);
        const calcMove = this.convertToCalcMove(move);
        const field = this.convertToCalcField(battleState.field);
        const side = this.convertToCalcSide(battleState.p1.side);
        try {
            // Simplified damage calculation for now
            const basePower = move.power || 80;
            const accuracy = move.accuracy || 100;
            // Simple damage calculation
            const minDamage = Math.floor(basePower * 0.8);
            const maxDamage = Math.floor(basePower * 1.2);
            const averageDamage = (minDamage + maxDamage) / 2;
            return {
                action,
                damage: {
                    min: minDamage,
                    max: maxDamage,
                    average: averageDamage,
                    ohko: this.calculateOHKOChance([minDamage, maxDamage], defender.hp),
                    twohko: this.calculate2HKOChance([minDamage, maxDamage], defender.hp)
                },
                accuracy: accuracy,
                speedCheck: {
                    faster: this.isFaster(attacker, defender),
                    speedDiff: this.getSpeedDifference(attacker, defender)
                },
                hazardDamage: this.calculateHazardDamage(battleState, action),
                statusChance: this.calculateStatusChance(move),
                expectedSurvival: this.calculateSurvivalChance([minDamage, maxDamage], defender.hp),
                expectedGain: this.calculateExpectedGain([minDamage, maxDamage], defender.hp, attacker.hp),
                priority: move.priority || 0
            };
        }
        catch (error) {
            console.error('Error in damage calculation:', error);
            return this.createErrorResult(action);
        }
    }
    async calculateSwitchCost(battleState, action) {
        const switchPokemon = battleState.p1.bench[action.pokemon];
        if (!switchPokemon) {
            return this.createErrorResult(action);
        }
        const hazardDamage = this.calculateHazardDamage(battleState, action);
        const speedCheck = this.calculateSpeedCheck(switchPokemon, battleState.p2.active);
        return {
            action,
            accuracy: 100,
            speedCheck,
            hazardDamage,
            expectedSurvival: switchPokemon.hp > hazardDamage ? 1 : 0,
            expectedGain: 0,
            priority: 0
        };
    }
    async calculateTeraBenefit(battleState, action) {
        // Tera benefits are complex and depend on the specific situation
        // This is a simplified calculation
        const active = battleState.p1.active;
        if (!active) {
            return this.createErrorResult(action);
        }
        return {
            action,
            accuracy: 100,
            speedCheck: {
                faster: this.isFaster(active, battleState.p2.active),
                speedDiff: this.getSpeedDifference(active, battleState.p2.active)
            },
            expectedSurvival: 1,
            expectedGain: 0.1, // Simplified tera benefit
            priority: 0
        };
    }
    convertToCalcPokemon(pokemon) {
        return {
            name: pokemon.species,
            level: pokemon.level,
            hp: pokemon.hp,
            maxhp: pokemon.maxhp,
            status: pokemon.status?.name,
            boosts: pokemon.boosts,
            item: pokemon.item,
            ability: pokemon.ability,
            teraType: pokemon.teraType,
            terastallized: pokemon.terastallized
        };
    }
    convertToCalcMove(move) {
        return {
            name: move.name,
            type: move.type,
            category: move.category,
            power: move.power,
            accuracy: move.accuracy,
            priority: move.priority
        };
    }
    convertToCalcField(field) {
        return {
            weather: field.weather?.type,
            terrain: field.terrain?.type,
            pseudoWeather: field.pseudoWeather?.map((pw) => pw.type)
        };
    }
    convertToCalcSide(side) {
        return {
            spikes: side.hazards.spikes,
            toxicSpikes: side.hazards.toxicSpikes,
            stealthRock: side.hazards.stealthRock,
            stickyWeb: side.hazards.stickyWeb,
            reflect: side.screens.reflect,
            lightScreen: side.screens.lightScreen,
            auroraVeil: side.screens.auroraVeil,
            tailwind: side.sideConditions.tailwind,
            trickRoom: side.sideConditions.trickRoom,
            gravity: side.sideConditions.gravity,
            wonderRoom: side.sideConditions.wonderRoom,
            magicRoom: side.sideConditions.magicRoom
        };
    }
    calculateOHKOChance(damage, hp) {
        const ohkoCount = damage.filter(d => d >= hp).length;
        return ohkoCount / damage.length;
    }
    calculate2HKOChance(damage, hp) {
        const twohkoCount = damage.filter(d => d >= hp / 2).length;
        return twohkoCount / damage.length;
    }
    isFaster(pokemon1, pokemon2) {
        if (!pokemon2)
            return true;
        const speed1 = this.getEffectiveSpeed(pokemon1);
        const speed2 = this.getEffectiveSpeed(pokemon2);
        return speed1 > speed2;
    }
    getSpeedDifference(pokemon1, pokemon2) {
        if (!pokemon2)
            return 0;
        const speed1 = this.getEffectiveSpeed(pokemon1);
        const speed2 = this.getEffectiveSpeed(pokemon2);
        return speed1 - speed2;
    }
    getEffectiveSpeed(pokemon) {
        // This would need to be implemented based on actual speed calculation
        // For now, return a placeholder
        return 100;
    }
    calculateHazardDamage(battleState, action) {
        let damage = 0;
        const hazards = battleState.p2.side.hazards;
        if (action.type === 'switch') {
            if (hazards.stealthRock) {
                damage += 12.5; // Simplified stealth rock damage
            }
            if (hazards.spikes > 0) {
                damage += hazards.spikes * 12.5;
            }
            if (hazards.toxicSpikes > 0) {
                damage += 12.5;
            }
        }
        return damage;
    }
    calculateStatusChance(move) {
        // This would need to be implemented based on move data
        // For now, return a placeholder
        return 0;
    }
    calculateSurvivalChance(damage, hp) {
        const survivalCount = damage.filter(d => d < hp).length;
        return survivalCount / damage.length;
    }
    calculateExpectedGain(damage, defenderHp, attackerHp) {
        const averageDamage = damage.reduce((a, b) => a + b, 0) / damage.length;
        const expectedHpLoss = Math.min(averageDamage, defenderHp);
        const expectedHpGain = Math.max(0, defenderHp - averageDamage);
        return expectedHpGain - expectedHpLoss;
    }
    createErrorResult(action) {
        return {
            action,
            accuracy: 0,
            speedCheck: { faster: false, speedDiff: 0 },
            expectedSurvival: 0,
            expectedGain: 0,
            priority: 0
        };
    }
    createDefaultResult(action) {
        return {
            action,
            accuracy: 100,
            speedCheck: { faster: false, speedDiff: 0 },
            expectedSurvival: 1,
            expectedGain: 0,
            priority: 0
        };
    }
    calculateSpeedCheck(pokemon1, pokemon2) {
        return {
            faster: this.isFaster(pokemon1, pokemon2),
            speedDiff: this.getSpeedDifference(pokemon1, pokemon2)
        };
    }
}
exports.DamageCalculator = DamageCalculator;
//# sourceMappingURL=calculator.js.map