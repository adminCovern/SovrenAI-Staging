export interface WebhookEvent {
    id: string
    type: string
    payload: any
    timestamp: Date
    source: string
}

export interface WebhookResponse {
    success: boolean
    message: string
    data?: any
}

export class RevolutionaryCRMWebhookHandler {
    private eventHandlers: Map<string, (event: WebhookEvent) => Promise<WebhookResponse>> = new Map()
    private eventHistory: WebhookEvent[] = []

    public registerHandler(eventType: string, handler: (event: WebhookEvent) => Promise<WebhookResponse>): void {
        this.eventHandlers.set(eventType, handler)
    }

    public async handleWebhook(event: WebhookEvent): Promise<WebhookResponse> {
        this.eventHistory.push(event)

        const handler = this.eventHandlers.get(event.type)
        if (handler) {
            try {
                return await handler(event)
            } catch (error) {
                return {
                    success: false,
                    message: `Error handling webhook: ${error}`
                }
            }
        }

        return {
            success: false,
            message: `No handler registered for event type: ${event.type}`
        }
    }

    public getEventHistory(): WebhookEvent[] {
        return [...this.eventHistory]
    }

    public clearEventHistory(): void {
        this.eventHistory = []
    }

    public getRegisteredHandlers(): string[] {
        return Array.from(this.eventHandlers.keys())
    }
} 