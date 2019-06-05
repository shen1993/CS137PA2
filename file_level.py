from token_level import Token
from sentence_level import Sentence
from document_level import Document


class File(object):
    def __init__(self, path):
        self.path = path
        self.docs = []
        self.read()

    def read(self):
        with open(self.path, 'r') as f:
            for l in f:
                if l.startswith('#begin document'):
                    sentenceID = 0
                    begin = l
                    doc = []
                    sent = []
                elif l == '#end document\n':
                    self.docs.append((begin, Document(doc)))
                elif l == '\n':
                    if sent:
                        doc.append(Sentence(sent, sentenceID))
                        sent = []
                        sentenceID += 1
                else:
                    sent.append(Token(l))

    def write(self, file_name):
        with open(file_name, 'w') as f:
            for d in self.docs:
                f.write(d[0])
                for sent in d[1].sentences:
                    for tok in sent.tokens:
                        f.write(tok.text)
                    f.write('\n')
                f.write('#end document\n')

    def get_features(self):
        X_y = []
        for d in self.docs:
            pairs = d[1].get_pairs()
            X_y.extend([(p.features(), p.label) for p in pairs])
        return X_y

    def predict(self, model, vectorizer, file_name):
        for d in self.docs:
            d[1].predict(model, vectorizer)
        self.write(file_name)
