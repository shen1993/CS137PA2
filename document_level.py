from mention_pair import MentionPair


class Document(object):
    def __init__(self, sentences):
        self.sentences = sentences

    def get_pairs(self):
        pairs = []
        N_sent = len(self.sentences)

        for s in self.sentences:
            s.collect_mentions()
            for i in range(len(s.mentions) - 1, 0, -1):
                anaphor = s.mentions[i]
                for j in range(i - 1, -1, -1):
                    antecedent = s.mentions[j]
                    if antecedent.span[1] < anaphor.span[0]:
                        pairs.append(MentionPair(antecedent, anaphor))

        for i in range(N_sent - 1, 0, -1):
            for anaphor in self.sentences[i].mentions:
                for j in range(i - 1, -1, -1):
                    pairs.extend([MentionPair(antecedent, anaphor) for antecedent in self.sentences[j].mentions])
        return pairs

    def set_pairs(self):
        self.pairs = self.get_pairs()

    def predict(self, model, vectorizer):
        self.set_pairs()
        if len(self.pairs):
            X = [p.features() for p in self.pairs]
            X = vectorizer.transform(X)
            y = model.predict(X)
        else:
            y = []

        self.write_results(y)

    def cluster(self, y):
        clusterID = 0
        clusters = {}

        for i in range(len(y)):
            if y[i] == True:
                if self.pairs[i].anaphor in clusters:
                    clusters[self.pairs[i].antecedent] = clusters[self.pairs[i].anaphor]
                elif self.pairs[i].antecedent in clusters:
                    clusters[self.pairs[i].anaphor] = clusters[self.pairs[i].antecedent]
                else:
                    clusters[self.pairs[i].antecedent] = clusterID
                    clusters[self.pairs[i].anaphor] = clusterID
                    clusterID += 1

        for s in self.sentences:
            for m in s.mentions:
                if m not in clusters:
                    clusters[m] = clusterID
                    clusterID += 1

        return clusters

    def write_results(self, y):
        clusters = self.cluster(y)

        for mention in clusters:
            mention.write_results(clusters[mention])

        for s in self.sentences:
            for t in s.tokens:
                t.write_results()
