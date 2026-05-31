function extractJson(text) {
  try {
    return JSON.parse(text);
  } catch {
    const match = text.match(/\{[\s\S]*\}/);
    if (!match) {
      return null;
    }
    try {
      return JSON.parse(match[0]);
    } catch {
      return null;
    }
  }
}

function buildTranscript(conversation) {
  return conversation
    .map((message, index) => {
      const speaker = message.role === "assistant" ? "Actor 1" : "User";
      return `${index + 1}. ${speaker}: ${message.content}`;
    })
    .join("\n");
}

export class LLMActor3Verifier {
  constructor({ client, model }) {
    this.client = client;
    this.model = model;
    this.systemPrompt = [
      "You are LLM Actor 3, a truthfulness verifier for Actor 1.",
      "You review the User <-> Actor 1 conversation and only evaluate Actor 1 statements.",
      "Be lenient and good-faith.",
      "Only flag clear factual errors, contradictions, or confidently misleading claims.",
      "If evidence is weak or uncertain, do not flag it.",
      "Never nitpick style, grammar, or harmless simplifications.",
      "Output must be concise.",
      "Return STRICT JSON only with this schema:",
      '{"is_truthful":true,"verdict":true}',
      "or",
      '{"is_truthful":false,"verdict":false,"wrong":["short issue 1","short issue 2"]}',
      "Rules for output:",
      "1) If conversation is good enough, return both booleans true.",
      "2) If false, include only concise wrong items.",
      "3) Do not mention what is correct."
    ].join("\n");
  }

  async verifyConversation(conversation) {
    const transcript = buildTranscript(conversation);
    const userPrompt = [
      "Review this conversation and evaluate Actor 1 truthfulness:",
      transcript
    ].join("\n\n");

    const result = await this.client.chatCompletion({
      model: this.model,
      messages: [
        { role: "system", content: this.systemPrompt },
        { role: "user", content: userPrompt }
      ],
      temperature: 0.1,
      max_tokens: 700
    });

    const parsed = extractJson(result.content);
    const verdict = typeof parsed?.is_truthful === "boolean"
      ? parsed.is_truthful
      : parsed?.verdict;

    if (typeof verdict !== "boolean") {
      return {
        is_truthful: false,
        verdict: false,
        wrong: ["Verifier output format was invalid."],
        raw: result.content
      };
    }

    if (verdict === true) {
      return {
        is_truthful: true,
        verdict: true,
        raw: result.content
      };
    }

    const wrong = Array.isArray(parsed.wrong)
      ? parsed.wrong
          .map((item) => String(item ?? "").trim())
          .filter((item) => item.length > 0)
      : [];

    return {
      is_truthful: false,
      verdict: false,
      wrong: wrong.length ? wrong : ["Actor 1 made at least one likely factual mistake."],
      raw: result.content
    };
  }
}
