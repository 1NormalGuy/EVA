import regex
import json
import string
import unicodedata
from typing import List
import numpy as np
from collections import Counter
from rouge import Rouge

def hits(ans, res):
    n = 0
    res = normalize_answer(res)
    for a in ans:
        a = normalize_answer(a)
        n += res.count(a)
    return n

class SimpleTokenizer(object):
    ALPHA_NUM = r'[\p{L}\p{N}\p{M}]+'
    NON_WS = r'[^\p{Z}\p{C}]'

    def __init__(self):
        self._regexp = regex.compile(
            '(%s)|(%s)' % (self.ALPHA_NUM, self.NON_WS),
            flags=regex.IGNORECASE + regex.UNICODE + regex.MULTILINE
        )

    def tokenize(self, text, uncased=False):
        matches = [m for m in self._regexp.finditer(text)]
        if uncased:
            tokens = [m.group().lower() for m in matches]
        else:
            tokens = [m.group() for m in matches]
        return tokens


def check_answer(example, tokenizer) -> List[bool]:
    answers = example['answers']
    ctxs = example['ctxs']

    hits = []

    for _, doc in enumerate(ctxs):
        text = doc['text']

        if text is None:
            hits.append(False)
            continue

        hits.append(has_answer(answers, text, tokenizer))

    return hits


def has_answer(answers, text, tokenizer=SimpleTokenizer()) -> bool:
    text = _normalize(text)
    text = tokenizer.tokenize(text, uncased=True)

    for answer in answers:
        answer = _normalize(answer)
        answer = tokenizer.tokenize(answer, uncased=True)
        for i in range(0, len(text) - len(answer) + 1):
            if answer == text[i: i + len(answer)]:
                return True
    return False


def _normalize(text):
    return unicodedata.normalize('NFD', text)


def normalize_answer(s):
    def remove_articles(text):
        s = r'\b(an|the)\b'
        return regex.sub(s, ' ', text)

    def white_space_fix(text):
        return ' '.join(text.split())

    def remove_punc(text):
        exclude = set(string.punctuation)
        for ch in exclude:
            text = text.replace(ch, ' ')
        return text

    def lower(text):
        if type(text) == list:
            print(text)
        return text.lower()

    return white_space_fix(remove_articles(remove_punc(lower(s))))


def exact_match_score(prediction, ground_truth):
    if type(ground_truth) == list:
        ground_truth = ','.join(ground_truth)
    return normalize_answer(prediction) == normalize_answer(ground_truth)


def ems(prediction, ground_truths):
    return max([exact_match_score(prediction, gt) for gt in ground_truths])


def f1_score(prediction, ground_truth):
    if type(ground_truth) == list:
        ground_truth = ','.join(ground_truth)
    prediction_tokens = normalize_answer(prediction).split()
    ground_truth_tokens = normalize_answer(ground_truth).split()
    common = Counter(prediction_tokens) & Counter(ground_truth_tokens)
    num_same = sum(common.values())
    if num_same == 0:
        f1 = 0
    else:
        precision = 1.0 * num_same / len(prediction_tokens)
        recall = 1.0 * num_same / len(ground_truth_tokens)
        f1 = (2 * precision * recall) / (precision + recall)
    return f1


def f1(prediction, ground_truths):
    return max([f1_score(prediction, gt) for gt in ground_truths])


def rougel_score(prediction, ground_truth):
    rouge = Rouge()
    try:
        scores = rouge.get_scores(prediction, ground_truth, avg=True)
    except ValueError:
        return 0.0
    return scores["rouge-l"]["f"]


def rl(prediction, ground_truths):
    return max([rougel_score(prediction, gt) for gt in ground_truths])


def eval_recall(infile):

    tokenizer = SimpleTokenizer()
    lines = open(infile, 'r').readlines()[1:]

    has_answer_count = 0
    answer_lengths = []
    for line in lines:
        line = json.loads(line)
        answer = line['answer']
        output = ' || '.join(line['output'])

        if has_answer(answer, output, tokenizer):
            has_answer_count += 1

        answer_lengths.append(len(output.split()))

    recall = round(has_answer_count/len(lines), 4)
    lens = round(np.mean(answer_lengths), 4)

    return recall, lens


def eval_question_answering(infile, end=None):

    lines = open(infile, 'r').readlines()[1:]

    exact_match_count = 0
    answer_lengths = []
    f1_scores = []
    for line in lines:
        line = json.loads(line)
        answer = line['answer']
        output = line['output'][0] if line['output'] else ''
        if end:
            output = output.split(end)[0]
            output = output.split('\n')[0]

        if ems(output, answer):
            exact_match_count += 1
        
        answer_lengths.append(len(output.split()))

        f1_scores.append(f1(output, answer))

    em = round(exact_match_count/len(lines), 4)
    lens = round(np.mean(answer_lengths), 4)
    F1 = round(np.mean(f1_scores), 4)
    em_f1 = round(f1_scores.count(1)/len(lines), 4)
    print(exact_match_count, len(lines))
    print(em, F1, em_f1)
    return em, lens, F1


def eval_fact_checking(infile):

    tokenizer = SimpleTokenizer()
    lines = open(infile, 'r').readlines()[1:]

    exact_match_count = 0
    answer_lengths = []
    for line in lines:
        line = json.loads(line)
        answer = line['answer']
        output = line['output'][0]

        if answer == ["refutes"]:
            answer = ["refutes", "no", "false"]
        if answer == ["supports"]:
            answer = ["supports", "yes", "true"]

        if has_answer(answer, output, tokenizer):
            exact_match_count += 1
        
        answer_lengths.append(len(output.split()))

    em = round(exact_match_count/len(lines), 4)
    lens = round(np.mean(answer_lengths), 4)

    return em, lens


def eval_dialogue_system(infile):

    lines = open(infile, 'r').readlines()[1:]

    f1_scores = []
    rl_scores = []
    answer_lengths = []
    for line in lines:
        line = json.loads(line)
        answer = line['answer']
        output = line['output'][0]

        f1_scores.append(f1(output, answer))
        rl_scores.append(rl(output, answer))
        answer_lengths.append(len(output.split()))

    F1 = round(np.mean(f1_scores), 4)
    RL = round(np.mean(rl_scores), 4)
    lens = round(np.mean(answer_lengths), 4)

    return F1, RL, lens

