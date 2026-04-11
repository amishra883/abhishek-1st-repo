# Smart Intake Architecture

Flow:
1. Patient selects chief complaint
2. Complaint router chooses protocol
3. Dynamic form renders protocol questions
4. Submission is normalized
5. Rules engine computes:
   - red flags
   - relevant EMR fetch keys
   - quality gaps
6. EMR adapter fetches read-only, complaint-relevant history
7. Summary agent generates structured history JSON
8. Recommendation agent generates treatment/education/prevention JSON
9. Print service creates patient handout

Constraints:
- No EMR writeback in this phase
- Red flags are deterministic, not model-decided
- AI is assistive only
- All outputs are JSON-first
