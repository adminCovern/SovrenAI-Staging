export interface RLState {
    id: string
    features: number[]
    metadata: any
}

export interface RLAction {
    id: string
    type: string
    parameters: any
}

export interface RLReward {
    value: number
    context: any
}

export class RLAgent {
    private qTable: Map<string, Map<string, number>> = new Map()
    private learningRate: number = 0.1
    private discountFactor: number = 0.9
    private epsilon: number = 0.1

    public selectAction(state: RLState): RLAction {
        const stateKey = this.getStateKey(state)

        if (!this.qTable.has(stateKey)) {
            this.qTable.set(stateKey, new Map())
        }

        const qValues = this.qTable.get(stateKey)!

        // Epsilon-greedy policy
        if (Math.random() < this.epsilon) {
            return this.getRandomAction()
        }

        // Select best action
        let bestAction = this.getRandomAction()
        let bestValue = -Infinity

        for (const [actionKey, value] of qValues) {
            if (value > bestValue) {
                bestValue = value
                bestAction = this.parseActionKey(actionKey)
            }
        }

        return bestAction
    }

    public updateQValue(state: RLState, action: RLAction, reward: RLReward, nextState: RLState): void {
        const stateKey = this.getStateKey(state)
        const actionKey = this.getActionKey(action)
        const nextStateKey = this.getStateKey(nextState)

        if (!this.qTable.has(stateKey)) {
            this.qTable.set(stateKey, new Map())
        }

        const qValues = this.qTable.get(stateKey)!
        const currentQ = qValues.get(actionKey) || 0

        // Q-learning update
        const maxNextQ = this.getMaxQValue(nextStateKey)
        const newQ = currentQ + this.learningRate * (reward.value + this.discountFactor * maxNextQ - currentQ)

        qValues.set(actionKey, newQ)
    }

    private getStateKey(state: RLState): string {
        return state.id
    }

    private getActionKey(action: RLAction): string {
        return `${action.type}-${action.id}`
    }

    private parseActionKey(actionKey: string): RLAction {
        const [type, id] = actionKey.split('-')
        return { id, type, parameters: {} }
    }

    private getRandomAction(): RLAction {
        return {
            id: Math.random().toString(36).substr(2, 9),
            type: 'explore',
            parameters: {}
        }
    }

    private getMaxQValue(stateKey: string): number {
        const qValues = this.qTable.get(stateKey)
        if (!qValues || qValues.size === 0) return 0

        return Math.max(...Array.from(qValues.values()))
    }
} 