# cozy-student

Agent framework prototype with:
- `LLM Actor 1`: a strict beginner student that only uses what the user explicitly taught.
- `LLM Actor 3`: verifies Actor 1's truthfulness and returns binary output.

Uses Hack Club AI chat completions API:
- Docs: https://docs.ai.hackclub.com/
- Endpoint: `https://ai.hackclub.com/proxy/v1/chat/completions`

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create your environment file:
```bash
cp .env.example .env
```
On Windows PowerShell:
```powershell
Copy-Item .env.example .env
```

3. Edit `.env` and add your API key:
```env
HACKCLUB_AI_API_KEY=your_api_key_here
HACKCLUB_AI_BASE_URL=https://ai.hackclub.com/proxy/v1
ACTOR1_MODEL=qwen/qwen3-32b
ACTOR3_MODEL=qwen/qwen3-32b
```

## Run

Single message flow:
```bash
npm start -- "The moon is made of cheese."
```

Demo flow:
```bash
npm run demo
```

## How the flow works

1. User sends a teaching message.
2. Actor 1 replies with an LLM response.
3. Actor 3 receives the full User <-> Actor 1 conversation.
4. Actor 3 returns:
   - `{"is_truthful": true, "verdict": true}` if Actor 1 is good enough
   - `{"is_truthful": false, "verdict": false, "wrong": [...]}` when Actor 1 likely said something incorrect
   - no mention of what is correct when returning `false`
