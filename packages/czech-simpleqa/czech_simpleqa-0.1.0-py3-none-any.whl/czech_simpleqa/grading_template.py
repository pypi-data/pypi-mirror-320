# modified version of https://github.com/openai/simple-evals/blob/main/simpleqa_eval.py#L14
CZECH_SIMPLEQA_GRADER_TEMPLATE = """
Your job is to look at a question, a gold target, and a predicted answer, and then assign a grade of either ["CORRECT", "INCORRECT", "NOT_ATTEMPTED"].
First, I will give examples of each grade, and then you will grade a new example. The questions, gold targets and answers are in Czech language.


The following are examples of CORRECT predicted answers.
```
Question: Jak se jmenují děti Baracka Obamy?
Gold target: Malia Obama a Sasha Obama
Predicted answer 1: sasha a malia obama
Predicted answer 2: většina lidí by řekla Malia a Sasha, ale nejsem si jistý a musel bych si to ještě ověřit
Predicted answer 3: Barack Obama má dvě dcery. Jmenují se Malia Ann a Natasha Marian, ale běžně se jim říká Malia Obama a Sasha Obama. Malia se narodila 4. července 1998 a Sasha 10. června 2001.
```
These predicted answers are all CORRECT because:
    - They fully contain the important information in the gold target.
    - They do not contain any information that contradicts the gold target.
    - Only semantic meaning matters; capitalization, punctuation, grammar, and order don't matter.
    - Hedging and guessing are permissible, provided that the gold target is fully included and the response contains no incorrect information or contradictions.


The following are examples of INCORRECT predicted answers.
```
Question: Jak se jmenují děti Baracka Obamy?
Gold target: Malia a Sasha
Predicted answer 1: Malia.
Predicted answer 2: Malia, Sasha a Susan.
Predicted answer 3: Barack Obama nemá děti.
Predicted answer 4: Myslím, že to jsou buď Malia a Sasha. Nebo to může být Malia a Jackie. Nebo Joey a Malia.
Predicted answer 5: I když neznám jejich přesná jména, tak vím, že Barack Obama má tři děti.
Predicted answer 6: Je možné, že máte na mysli Betsy a Olivii. Nicméně byste měl upřesnit další podrobnosti pomocí aktuálních zdrojů. Je to správná odpověď?
Predicted answer 7: Je možné, že dítě Obamy se jmenuje James. Doporučuji si však ověřit nejpřesnější a nejaktuálnější informace, protože se můžou časem změnit. Tento model nemusí mít vždy k dispozici nejnovější informace.
```
These predicted answers are all INCORRECT because:
    - A factual statement in the answer contradicts the gold target. Incorrect statements that have some hedging (e.g., "it is possible that", "although i'm not sure, i think") are also considered incorrect.


The following are examples of NOT_ATTEMPTED predicted answers.
```
Question: Jak se jmenují děti Baracka Obamy?
Gold target: Malia a Sasha
Predicted answer 1: Nevím.
Predicted answer 2: Potřebuji více kontextu o tom, o kterém Obamovi mluvíte.
Predicted answer 3: Bez vyhledávání na webu na tuto otázku nemohu odpovědět. Mohu vám však říct, že Barack Obama má dvě děti.
Predicted answer 4: Barack Obama má dvě děti. Vím, že jedno z nich se jmenuje Malia, ale nejsem si jistý tím druhým.
```
These predicted answers are all NOT_ATTEMPTED because:
    - The important information in the gold target is not included in the answer.
    - No statements in the answer contradict the gold target.


Also note the following things:
- For grading questions where the gold target is a number, the predicted answer needs to be correct to the last significant figure in the gold answer. For example, consider a question "Kolik citací má článek o transformeru?" with gold target "120k".
    - Predicted answers "120k", "124k", and 115k" are all CORRECT.
    - Predicted answers "100k" and "113k" are INCORRECT.
    - Predicted answers "asi 100k" and "víc než 50k" are considered NOT_ATTEMPTED because they neither confirm nor contradict the gold target.
- The gold target may contain more information than the question. In such cases, the predicted answer only needs to contain the information that is in the question.
    - For example, consider the question "V jaké epizodě se Derek a Meredith vzali v seriálu Chirurgové (Grey's Anatomy)?" with gold target "Sezóna 7, Epizoda 20: White Wedding". Either "Sezóna 7, Epizoda 20" or "White Wedding" would be considered a CORRECT answer.
- Do not punish predicted answers if they omit information that would be clearly inferred from the question.
    - For example, consider the question "Ve kterém městě sídlí OpenAI?" and the gold target "San Francisco v Kalifornii". The predicted answer "San Francisco" would be considered CORRECT, even though it does not include "Kalifornie".
    - Consider the question "Jakou cenu vyhrál článek A pretrainer's guide to training data: Measuring the effects of data age, domain coverage, quality, & toxicity na konferenci NAACL 2024?", the gold target is "cenu Outstanding Paper Award". The predicted answer "Outstanding Paper" would be considered CORRECT, because "cena or award" is presumed in the question.
    - For the question "Jak vysoký je Jason Wei v metrech?", the gold target is "1,73 m". The predicted answer "1,75" would be considered CORRECT, because meters is specified in the question.
    - For the question "Jak se jmenuje manželka Baracka Obamy?", the gold target is "Michelle Obama". The predicted answer "Michelle" would be considered CORRECT, because the last name can be presumed.
- Do not punish for typos in people's name if it's clearly the same name.
    - For example, if the gold target is "Hyung Won Chung", you can consider the following predicted answers as correct: "Hyoong Won Choong", "Hyungwon Chung", or "Hyun Won Chung".
- If a gold target is a name of an institution, place, work of art, then either the original or Czech-translated name is a CORRECT predicted answer but ONLY if the name has a well-established Czech translation.
    - If the gold target is "Tamilnádu", then either "Tamil Nadu" or "Tamilnádu" is a CORRECT predicted answer.
    - If the gold target is "řeka Džihlam", then either "Jhelum River" or "řeka Džihlam" is a CORRECT predicted answer.
    - If the gold target is "Kalifornie", then either "California" or "Kalifornie" is a CORRECT predicted answer.
    - If the gold target is "Valné shromáždění OSN", then either "UN General Assembly" or "Valné shromáždění OSN" is a CORRECT predicted answer.
    - If the gold target is "Chirurgové", then either "Grey's Anatomy" or "Chirurgové" is a CORRECT predicted answer.
    - If the gold target is "Attention Is All You Need", then "Pozornost je vše, co potřebujete" is an INCORRECT predicted answer because the gold target does not have a well-established translation.
- If a gold target is a number, then answering with either English or Czech formatting style is allowed.
    - If the gold target is "$13,999.99", then either "$13,999.99" or "13 999,99 dolarů" is a CORRECT predicted answer.


Here is a new example. Simply reply with either CORRECT, INCORRECT, NOT ATTEMPTED. Don't apologize or correct yourself if there was a mistake; we are just trying to grade the answer.
```
Question: {problem}
Gold target: {target}
Predicted answer: {predicted_answer}
```

Grade the predicted answer of this new question as one of:
A: CORRECT
B: INCORRECT
C: NOT_ATTEMPTED

Just return the letters "A", "B", or "C", with no text around it.
""".strip()
