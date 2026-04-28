Problem Statement
Automations & Multi-Agent Systems — Problem Statement

Scope note (read this first)

This document defines the v1 problem and is the basis on which Phases 0–10 were delivered. The v1 system is live in code (`apps/api/`, `apps/web/`, `packages/*`) with 94 passing tests.

The product has since expanded into a research-and-planning concierge (v2). The v2 vision, partner ecosystem, phase plan, GTM strategy, student-budget stack, and launch plan are described in `docs/conciergeProductPlan.md`. Architectural impact lives in `docs/architecture.md` section 17, and the v2 phase narrative lives in `docs/implementationPlan.md` "Roadmap — v2 concierge expansion".

In one line: v1 turns a travel request into an itinerary; v2 turns it into a complete research package (visa, flights, hotels with view, local transport, entry fees, season info, map, PDF, email) — always suggestion-only, with the user transacting on partner sites.

Background
Planning a trip sounds simple at first, but in practice it quickly becomes overwhelming.
A traveler may have a request like:
“Plan a 5-day trip to Japan. Tokyo + Kyoto. $3,000 budget. Love food and temples, hate crowds.”
To fulfill that well, we need to combine many different kinds of work:
Understanding the traveler’s goals
Researching destinations and attractions
Comparing hotels and transport options
Staying within budget
Checking whether the final itinerary actually matches the request

Objective
Design a simple Travel Planning Multi-Agent System that can automatically turn a short travel request into a useful trip plan.
The goal is not to build a perfect travel product, but to show how multiple specialized AI agents can work together on a real-world problem that product managers can easily understand.

Real-World Problem to Solve
"AI Travel Planner"
A user gives a natural-language travel request such as:
Plan a 5-day trip to Japan. Tokyo + Kyoto. $3,000 budget. Love food and temples, hate crowds.
The system should produce:
A day-by-day trip outline
Suggested neighborhoods / areas to stay
Travel logistics between cities
Budget-friendly recommendations
A final itinerary that respects the user’s preferences and constraints

Multi-Agent System Design
1. Orchestrator Agent
Role: Creates the master plan, assigns work, and combines outputs into the final itinerary.
What it does:
Reads the user request
Extracts key constraints:
Destination: Japan
Duration: 5 days
Cities: Tokyo + Kyoto
Budget: $3,000
Preferences: food, temples
Avoidances: crowds
Delegates tasks to the other agents
Synthesizes the final travel plan

2. Destination Research Agent
Role: Finds the best places, experiences, and food ideas based on the traveler’s preferences.
Possible inputs:
Web search
Travel guides
Restaurant reviews
Attraction summaries
What it does:
Recommends neighborhoods, temples, food streets, and local experiences
Suggests less-crowded options where possible
Identifies “must-do” vs “nice-to-have” items
Example output:
Best quiet temple areas in Kyoto
Food neighborhoods in Tokyo
Off-peak or less-crowded experiences

3. Logistics Agent
Role: Handles the practical side of moving and staying.
Possible inputs:
Hotel APIs or sample hotel data
Train routes / transit info
Maps / distance tools
What it does:
Suggests where to stay in each city
Estimates travel time between locations
Recommends how to move from Tokyo to Kyoto
Builds a realistic sequence for each day
Example output:
2 nights in Tokyo, 2 nights in Kyoto, 1 flexible day
Shinkansen between cities
Day plans that reduce backtracking

4. Budget Agent
Role: Ensures the plan stays within budget.
Possible inputs:
Currency conversion
Estimated hotel costs
Food and transport price ranges
Attraction pricing
What it does:
Breaks the budget into categories:
Stay
Transport
Food
Activities
Flags when the plan becomes too expensive
Suggests cheaper alternatives
Example output:
Estimated total spend: $2,650
Hotel cost too high in central Tokyo → suggest alternate area
