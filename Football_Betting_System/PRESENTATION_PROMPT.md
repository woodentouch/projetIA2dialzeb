# PROMPT FOR PRESENTATION GENERATION

**Copy and paste the text below into NotebookLLM (or ChatGPT) along with the `AI_EXPLANATION_WHITEPAPER.md` file I just created.**

---

**PROMPT START**

Act as a Computer Science student presenting their final major project. I need you to generate a **Slide Deck Outline and Script** for a presentation about my "Football Betting AI System".

**Target Audience:** My professors and classmates.
**Tone:** Enthusiastic, proud, accessible, but technically accurate. Use simple analogies for complex math.
**Goal:** Prove that I understand the full stack (Back to Front) and the math, but keep it engaging.

Please create content for **10 Slides**. For each slide, provide:
1.  **Slide Title** (Catchy)
2.  **Visual Idea** (What should be on the screen? e.g., "Diagram of 10,000 simulations", "Snippet of Python code")
3.  **Speaker Script** (What I should say - use "I" and "We", sound natural).

**Key Concepts to Cover (Simplify these):**
*   **The Hook:** Why I built this? (To beat the bookies / solve the "luck" factor in football).
*   **The Ranking (TrueSkill):** Explain it as "Skill + Uncertainty" (like in the Halo video game) rather than complex Gaussian math. Contrast it with Elo (which is too simple).
*   **The Simulation (Monte Carlo):** Use the "Dr. Strange" analogy: "We don't predict the future once; we simulate it 10,000 times to see every possibility."
*   **The "Opta" Engine:** Mention we track detailed stats like "Expected Goals" (xG) to spot lucky wins.
*   **The Tech Stack:** Show off the architecture (Docker, Python FastAPI, React, SQLModel). Mention `docker-compose` orchestrating everything.
*   **The User Experience:** How the React frontend prevents "layout shift" and makes it look professional.

**Structure the presentation like this:**
1.  **Intro:** The connection between Data Science and Football.
2.  **The Problem:** Why is betting hard? (Randomness/Luck).
3.  **The Solution:** My Hybrid AI Approach.
4.  **Under the Hood (Math):** TrueSkill & Bayesian Logic (simplified).
5.  **The "Multiverse" Engine:** 10,000 Simulations explanation.
6.  **Advanced Metrics:** Handling 'Form' and 'Venue Advantage' (Home vs Away).
7.  **System Architecture:** How the containers talk to each other (Backend/Frontend/DB).
8.  **The Code:** Briefly flash the `BayesianFootballModel` class or `models.py`.
9.  **Demo Flow:** Walkthrough of a user placing a bet.
10. **Conclusion:** What I learned & Success Rate.

**Use the provided source document (`AI_EXPLANATION_WHITEPAPER.md`) to pull the correct technical facts.**

**PROMPT END**
