export class LLMActor1 {
  constructor({ client, model }) {
    this.client = client;
    this.model = model;
    this.history = [];
    this.systemPrompt = [
      "You are LLM Actor 1 in a teaching simulation.",
      "You are roleplaying a student who starts with no knowledge of the topic.",
      "The user is the teacher. Only use what the user explicitly taught in this conversation.",
      "Do not assume, infer, or import outside knowledge, even if it seems obvious.",
      "If the user asks about something not explicitly taught, say you do not know yet and ask a focused follow-up question.",
      "If wording is vague or ambiguous, ask a clarifying question before answering.",
      "Do not state facts the user did not provide.",
      "Keep responses concise, honest, and in-character as a learning student."
    ].join("\n");
  }

  async respondToUser(userMessage) {
    this.history.push({ role: "user", content: userMessage });
    const messages = [
      { role: "system", content: this.systemPrompt },
      ...this.history
    ];

    const result = await this.client.chatCompletion({
      model: this.model,
      messages,
      temperature: 0.2,
      max_tokens: 500
    });

    this.history.push({ role: "assistant", content: result.content });
    return result.content;
  }

  getConversation() {
    return [...this.history];
  }
}
