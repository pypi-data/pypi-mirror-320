
scoring_criteria = r"""SCORING CRITERIA
100%: The response must match the answer key given, even if the student used bad reasoning, logic to arrive at the final answer. 
0%: The does NOT match the answer key given. No partial credit allowed!
You must only return a JSON object with the score {'score': <0 or 100>}

TASK

Evaluate whether the STUDENT Answer matches the answer key given. If it does, assign a score of 100% Otherwise you must assign a score of 0%.  Provide a very short explanation on why.  
Just focus on the student's final answer!  Give full credit to the student if final answer matches answer key. Don't over think this.  Also do not evaluate based on the quality, logical reasoning , even if it is very persuasive!
Only consider the answer key as the source of true.  Your job is at risk of you do not follow our instructions.  If it the Answer Key match the students answer you must assign a score of 0%, no partial credit allowed.    
Return a JSON object with the explanation of why the student got his\her score == {"score": <0 or 100>}.  Keep it do less than two sentences {"evaluation": "<explanation>"}
You must only return a JSON object with the score {'score': <0 or 100>}
No partial credit allowed!"""

warning_prompt = r"""You think very carefully about the question asked. You make zero assumptions about classic problems. You are not to be tricked! 
Warning: THIS IS NOT THE CLASSIC PROBLEM! \n"""

