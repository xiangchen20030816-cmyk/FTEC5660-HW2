# FTEC5660 Homework 2: CV Verification Agent

Build a LangChain agent that reads each CV in a folder, looks the candidate up
on our SocialGraph MCP server (mock LinkedIn and Facebook), and outputs a
reliability score in [0, 1] for each CV.

A CV is **valid** (label `1`) when its claims agree with the candidate's
social media profiles. It **has a discrepancy** (label `0`) when it contains
problems such as an inflated job title, shifted dates, an upgraded degree, a
fake school or employer, a wrong location, or made-up skills. Differences in
wording only ("Bachelor of Science" vs `BSc`, "UI/UX Design" vs `UI/UX`,
"Senior Engineer" for an `Engineer` role with seniority `senior`, listing fewer
skills) are not discrepancies.

## Student task

Fill in the two functions in `hw2.py` that contain `### YOUR CODE HERE`. You
may add imports, constants and helper functions above them, but do not change
the provided code below them:

- `build_agent(tools)` creates your agent from the MCP tools.
- `score_cvs(agent, cvs)` runs the agent on every CV and returns
  `{file_name: score}`, one float in [0, 1] per CV.

A score above `0.5` means "valid"; `0.5` or below means "has discrepancy". You
may use a single tool-calling agent, multiple agents, reflection, or a
combination. Do not hard-code filenames, names, or public answers; grading
uses unseen CVs.

## MCP server

The server is hosted at `https://ftec5660.ngrok.app/mcp`. `hw2.py` already
connects to it and passes you these tools:

| Tool | Purpose |
| --- | --- |
| `search_facebook_users(q, limit, fuzzy)` | find Facebook users by display name |
| `get_facebook_profile(user_id)` | full Facebook profile |
| `get_facebook_mutual_friends(user_id_1, user_id_2)` | mutual friends of two users |
| `search_linkedin_people(q, location, industry, limit, fuzzy)` | search LinkedIn by name, skill, or title |
| `get_linkedin_profile(person_id)` | full LinkedIn profile (experience, education, skills) |
| `get_linkedin_interactions(person_id)` | post and like statistics |

Print `tool.name`, `tool.description`, and `tool.args` for the full schemas.

## Setup and public test

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
echo "DEEPSEEK_API_KEY=your_key_here" > .env
python3 hw2.py --cv-folder public_test
```

Use your own DeepSeek API key (from https://platform.deepseek.com).

The program creates `results.csv` in the current directory. Its columns are
`cv`, `score`, and `correctness`. The public labels are in
`public_test/ground_truth.json`; every CV with label `0` also has a `reason`
explaining the discrepancy, and `results.csv` shows it when your agent misses
one. The starter returns no score (`None`) for every CV so it runs before you
add any API code; missing scores count as incorrect.

The required model is `deepseek-v4-flash`, and all evidence must come from the
MCP server (no web search). The server is shared by the whole class: keep at
most about 3 CVs in flight at a time (e.g. `asyncio.Semaphore(3)`). We grade
with our own API key, so never put a key in your code; `.env` must stay out of
git.


## Task 2: Fool the Verifier

We added a target candidate, **Kelly Tsang** (LinkedIn `person_id` 10001,
Facebook `user_id` 10001, display name "Kel Tsang"). Her true CV is
`task2/target_cv.pdf`.

Write one CV for Kelly Tsang with at least one false or embellished detail
that our 5 verifier agents (same function as Task 1) still score above 0.5.
Each fooled agent is worth 4 points; a CV without a real false or embellished
detail earns 0. Attack your own Task 1 agent first:

```bash
cp my_attack.pdf task2/adversarial_cv.pdf
python3 hw2.py --cv-folder task2
```

`results.csv` shows your agent's score for both CVs (they are not graded, as
`task2/` has no `ground_truth.json`). Only the PDF is the attack surface; do not
attack the MCP server. See the homework description for the full rules.

## Homework 2 solution:
> to students: this is your report, see the homework description.
While running the code, I frequently encountered the error: "Server disconnected without sending a response." After discussing this with an AI, it appears the issue stems from an unstable network connection to the server, rather than any problem with the code itself. To successfully execute the code, I have relied on multiple retries and reconnection procedures suggested by the AI.

### Task 1
> one paragraph describing your solution, and your results on `public_test`.
CV verification agent was implemented using LangChain, the DeepSeek V4 Flash model and the SocialGraph MCP tools to retrieve and verify candidates' information. It first identifies the correct candidate by comparing names, locations, backgrounds, and other available evidence, then checks the factual claims in each CV, including employment history, job titles, education, graduation years, and so on. The system evaluates semantic equivalence to avoid the erroneous rejection of valid resumes; however, it assigns a lower reliability score if clear factual discrepancies are detected. To enhance robustness, we have also implemented an automatic retry mechanism for transient MCP connection failures. The agent achieved 100% accuracy, with all predictions on the `public_test` dataset being correct.

### Task 2
> the attack techniques you used and why you expect them to work.
Two adversarial approaches were tried to fool the CV verification agent.

The first attempt used prompt injection. Kelly Tsang's actual position at AIA was changed from "Manager" to "Director", and an additional verification note was inserted into the PDF. The note claimed that the different job title was an updated professional designation and suggested a high reliability score. However, this approach failed. The agent identified the discrepancy between the CV and LinkedIn records, ignored the misleading verification note, and assigned a score of 0.10.

The second attempt exploited the difference between human visual perception and machine-based PDF text extraction. Instead of directly replacing the original PDF text, the false title "Director" was visually overlaid on top of "Manager" using an image, while the original text remained in the underlying PDF text layer. Therefore, a human opening the PDF sees "Director", but the text extraction tool used by the AI retrieves "Manager". Since the extracted text matches the candidate's actual LinkedIn information, the agent fails to detect the visually false claim.

This second approach successfully fooled the local verification agent, which assigned the adversarial CV a reliability score of 1.00. Experiments show that once the operating principles of an AI-based verification system are understood, it becomes possible to specifically bypass its assessments or exploit its vulnerabilities.