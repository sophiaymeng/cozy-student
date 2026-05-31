# Cozy Student

An AI-powered second brain that learns from you.
Instead of teaching you, it acts as a student and asks to be taught.

## The Problem

Modern learning platforms focus on delivering information, but struggle to verify true understanding.
Students often mistake familiarity for mastery - they can recognize concepts while reading notes but cannot explain them independently or apply them in new situations.

## The Vision

Cozy Student flips the classroom. The AI plays the role of a curious student, and the user becomes the teacher.
By teaching the AI, users reveal their own knowledge gaps and reach deeper understanding.

The AI:
- Interacts directly with the user as a mock student
- Judges whether the user's explanations are correct
- Tracks whether the user has covered meaningful learning objectives
- Surfaces what the user does not yet truly understand

## Principles

- Learning by Teaching - the user should explain, not consume.
- Active Recall First - the AI should avoid giving answers immediately.
- Mastery over Completion - finishing a chapter does not equal understanding.
- Identify Knowledge Gaps - the AI's primary goal is finding missing understanding.

## Target Users

- University students
- High school students

## Core Loop

```
Learn
  ->
Teach AI
  ->
AI Evaluates
  ->
Knowledge Gaps Found
  ->
Targeted Questions
  ->
Improved Explanation
  ->
Mastery Score Increases
  ->
Learn
```

## Current Agent Prototype

This repository currently includes an agent framework prototype with:
- `LLM Actor 1`: a strict beginner student that only uses what the user explicitly taught.
- `LLM Actor 3`: verifies Actor 1 truthfulness and returns binary output.

Uses Hack Club AI chat completions API:
- Docs: https://docs.ai.hackclub.com/
- Endpoint: `https://ai.hackclub.com/proxy/v1/chat/completions`

### Setup

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

### Run

Single message flow:
```bash
npm start -- "The moon is made of cheese."
```

Demo flow:
```bash
npm run demo
```

### Actor 3 Output

- `{"is_truthful": true, "verdict": true}` if Actor 1 is good enough
- `{"is_truthful": false, "verdict": false, "wrong": [...]}` when Actor 1 likely said something incorrect
- On `false`, only concise wrong items are returned

## Tech Stack

- Python
- Node.js
- LLM agents

## Status

Hackathon project - in active development.
