export class ShowdownClient {
  // Placeholder skeleton for future WebSocket integration with Pokemon Showdown
  async connect(serverUrl: string, username: string, password?: string): Promise<void> {
    console.log(`Connecting to Showdown at ${serverUrl} as ${username}...`);
    // TODO: implement WebSocket protocol and login flow
  }

  async sendAction(action: unknown): Promise<void> {
    console.log('Sending action to Showdown', action);
  }

  async disconnect(): Promise<void> {
    console.log('Disconnecting from Showdown...');
  }
}
