from collections import defaultdict
from mention import Mention


class Sentence(object):
    def __init__(self, tokens, sentenceID):
        self.tokens = tokens
        self.sentenceID = sentenceID
        self.mentions = []

    def collect_mentions(self):
        mention_ids = defaultdict(list)

        def get_start_ids(cr):
            return [int(x.replace(')', '').replace('(', '')) for x in cr.split('|') if x.startswith('(')]

        def get_end_ids(cr):
            return [int(x.replace(')', '').replace('(', '')) for x in cr.split('|') if x.endswith(')')]

        starts = [(i, t) for (i, t) in enumerate(self.tokens) if t.coref.find('(') > -1]
        starts.reverse()
        ends = [(i, t) for (i, t) in enumerate(self.tokens) if t.coref.find(')') > -1]

        for s in starts:
            ids = get_start_ids(s[1].coref)
            for i in ids:
                mention_ids[i].append(s)

        for e in ends:
            ids = get_end_ids(e[1].coref)
            for i in ids:
                s = mention_ids[i].pop()
                self.mentions.append(Mention(self.tokens[s[0]:e[0] + 1], self.sentenceID, (s[0], e[0]), i))
