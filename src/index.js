import { config, assertConfig } from "./config.js";
import { HackClubAIClient } from "./lib/hackclubClient.js";
import { LLMActor1 } from "./actors/llmActor1.js";
import { LLMActor3Verifier } from "./actors/llmActor3Verifier.js";
import { AgentSession } from "./framework/agentSession.js";

function printReview(review) {
  console.log("\n=== ACTOR 3 REVIEW ===");
  const payload = review.is_truthful === true
    ? { is_truthful: true, verdict: true }
    : { is_truthful: false, verdict: false, wrong: review.wrong ?? [] };
  console.log(JSON.stringify(payload));
}

async function run() {
  assertConfig();

  const userInput = process.argv.slice(2).join(" ").trim();
  const demoMode = process.argv.includes("--demo");

  const client = new HackClubAIClient({
    apiKey: config.hackclubApiKey,
    baseUrl: config.hackclubBaseUrl
  });

  const actor1 = new LLMActor1({
    client,
    model: config.actor1Model
  });

  const actor3 = new LLMActor3Verifier({
    client,
    model: config.actor3Model
  });

  const session = new AgentSession({ actor1, actor3 });

  const prompt = demoMode
    ? "The capital of Australia is Sydney. Also, water boils at 100 C at sea level."
    : userInput;

  if (!prompt) {
    console.log("Usage:");
    console.log('  npm start -- "your teaching message here"');
    console.log("  npm run demo");
    return;
  }

  const { actor1Response, actor3Review } = await session.runTurn(prompt);

  console.log("=== USER INPUT ===");
  console.log(prompt);

  console.log("\n=== ACTOR 1 RESPONSE ===");
  console.log(actor1Response);

  printReview(actor3Review);
}

run().catch((error) => {
  console.error("Error running agent session:");
  console.error(error.message);
  process.exit(1);
});
