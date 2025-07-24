export interface Competitor {
    id: string
    name: string
    marketShare: number
    strengths: string[]
    weaknesses: string[]
}

export interface PatentModule {
    id: string
    name: string
    description: string
    status: 'pending' | 'approved' | 'rejected'
}

export class CompetitiveAnnihilation {
    private competitors: Map<string, Competitor> = new Map()
    private patents: Map<string, PatentModule> = new Map()

    public benchmarkCompetitors(competitorList: string[]): any {
        const benchmarks = competitorList.map(name => ({
            id: `benchmark-${Date.now()}`,
            name,
            performance: Math.random() * 100,
            ranking: Math.floor(Math.random() * 10) + 1
        }))

        return {
            id: `benchmark-${Date.now()}`,
            competitors: benchmarks,
            analysis: 'comprehensive',
            advantage: 'significant'
        }
    }

    public triggerOneUpmanship(context: string, feature: string): any {
        return {
            id: `oneup-${Date.now()}`,
            context,
            feature,
            response: 'superior',
            impact: 'annihilating'
        }
    }

    public registerPatentModule(name: string, description: string): PatentModule {
        const patent: PatentModule = {
            id: `patent-${Date.now()}`,
            name,
            description,
            status: 'pending'
        }
        this.patents.set(patent.id, patent)
        return patent
    }

    public triggerImpossibleDemo(context: string, feature: string): any {
        return {
            id: `demo-${Date.now()}`,
            context,
            feature,
            performance: 'impossible',
            reaction: 'shock'
        }
    }

    public addCompetitor(id: string, competitor: Competitor): void {
        this.competitors.set(id, competitor)
    }

    public getCompetitor(id: string): Competitor | undefined {
        return this.competitors.get(id)
    }

    public getPatent(id: string): PatentModule | undefined {
        return this.patents.get(id)
    }
} 