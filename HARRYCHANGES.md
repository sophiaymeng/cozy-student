# Harry's Changes

## What I built

I added a small Node.js agent framework prototype using Hack Club AI.

- `Actor 1` is a strict beginner student:
  - Starts with no topic knowledge.
  - Only uses what the user explicitly teaches in-chat.
  - Does not assume or import outside facts.
  - Asks follow-up questions if something is vague or missing.

- `Actor 3` is a truthfulness verifier for Actor 1:
  - Reviews the User <-> Actor 1 conversation.
  - Returns a binary result:
    - `{"is_truthful": true, "verdict": true}`
    - `{"is_truthful": false, "verdict": false, "wrong": [...]}` (concise error list only)
  - Uses lenient/good-faith checking and avoids nitpicky feedback.

## Files added/updated

- Added: `src/lib/hackclubClient.js`
- Added: `src/framework/agentSession.js`
- Added: `src/actors/llmActor1.js`
- Added: `src/actors/llmActor3Verifier.js`
- Added: `src/index.js`
- Added: `package.json`
- Added: `.env.example`
- Added: `.gitignore`
- Updated: `README.md`

## Environment setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env` from example:
```powershell
Copy-Item .env.example .env
```

3. Fill in API key in `.env`:
```env
HACKCLUB_AI_API_KEY=your_api_key_here
HACKCLUB_AI_BASE_URL=https://ai.hackclub.com/proxy/v1
ACTOR1_MODEL=qwen/qwen3-32b
ACTOR3_MODEL=qwen/qwen3-32b
```

## Run commands

- Single prompt:
```bash
npm start -- "Teach Actor 1 something here"
```

- Demo:
```bash
npm run demo
```

## Expected output shape from Actor 3

```json
{"is_truthful": true, "verdict": true}
```

or

```json
{"is_truthful": false, "verdict": false, "wrong": ["short issue 1", "short issue 2"]}
```
