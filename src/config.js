import "dotenv/config";

const defaultBaseUrl = "https://ai.hackclub.com/proxy/v1";
const defaultModel = "qwen/qwen3-32b";

export const config = {
  hackclubApiKey: process.env.HACKCLUB_AI_API_KEY ?? "",
  hackclubBaseUrl: process.env.HACKCLUB_AI_BASE_URL ?? defaultBaseUrl,
  actor1Model: process.env.ACTOR1_MODEL ?? defaultModel,
  actor3Model: process.env.ACTOR3_MODEL ?? defaultModel
};

export function assertConfig() {
  if (!config.hackclubApiKey) {
    throw new Error(
      "Missing HACKCLUB_AI_API_KEY in .env. Copy .env.example to .env and add your key."
    );
  }
}
