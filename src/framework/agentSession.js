export class AgentSession {
  constructor({ actor1, actor3 }) {
    this.actor1 = actor1;
    this.actor3 = actor3;
  }

  async runTurn(userInput) {
    const actor1Response = await this.actor1.respondToUser(userInput);
    const conversation = this.actor1.getConversation();
    const actor3Review = await this.actor3.verifyConversation(conversation);

    return {
      actor1Response,
      actor3Review,
      conversation
    };
  }
}
