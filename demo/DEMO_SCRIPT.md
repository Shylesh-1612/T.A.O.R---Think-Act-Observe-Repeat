# NEXUS Agent Demo Script (3-5 minutes)

## 0:00 — Problem
"Welcome. For Track 2 'Build the Brain, Not the Puppet', our goal was to build a fully autonomous agent logic loop entirely from scratch, without hiding behind LangChain or AutoGen. We present NEXUS, an autonomous research and decision agent."

## 0:30 — NEXUS Solution
"NEXUS doesn't just call APIs. It dynamically decides which tools to use, interprets raw observations, structures unstructured data, and corrects itself when things go wrong."

## 1:00 — Architecture
"Our agent runs a custom DECISION -> ACT -> OBSERVE loop. 
The LLM acts strictly as a decision engine. Our Python code manages state, tool registry, execution, safety formatting, and error handling."

## 1:30 — Normal Live Run
*Run the Streamlit UI (Mock Mode).*
"Let's ask the agent to research tech events and calculate the budget. Watch the Execution Trace unfold. Notice how it dynamically formulates a highly specific search query, uses the extractor to parse raw text, calculates the cost, and then verifies the data. We explicitly instructed the agent to verify claims, and you can see it using the verifier tool organically."

## 2:30 — Failure Recovery
*Check 'Enable Demo Failure Mode' in UI and re-run.*
"Now watch what happens when a tool fails. We use an `unreliable_demo_tool` which acts as a chaotic environment. It throws a network error on attempt 1, and returns malformed data on attempt 2. 
Notice that NEXUS doesn't crash or follow a hardcoded 'if error then retry' path. The error is normalized into an 'observation', fed back to the LLM, and the LLM explicitly *decides* to adapt and try again."

## 3:15 — Show Custom Core Loop
*Switch to `agent/core.py` on screen.*
"If you look at our core execution loop, you will see zero hardcoded tasks. There are no if-else statements routing 'search' keywords to search tools. Everything is dynamically injected into the system prompt context window via our Tool Registry."

## 4:00 — Explain Dynamic Tool Selection
"Because the agent relies solely on JSON schemas, adding a new tool is as simple as defining an input schema. The LLM understands the tool and orchestrates it perfectly."

## 4:30 — Closing
"NEXUS proves that a robust, failure-resistant agent can be built with a simple, transparent loop. We didn't build a puppet; we built the brain. Thank you."
