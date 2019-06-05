class Token(object):
    def __init__(self, line):
        self.text = line
        self.get_annotations()
        self.predicted_coref = {'start': set(), 'end': set()}

    def get_annotations(self):
        fields = self.text.split()
        self.annotations = {'Document ID': fields[0], 'Part number': fields[1], 'Word number': fields[2],
                            'Word itself': fields[3], 'POS': fields[4], 'Parse bit': fields[5],
                            'Predicate lemma': fields[6], 'Predicate Frameset ID': fields[7], 'Word sense': fields[8],
                            'Speaker/Author': fields[9], 'Named Entities': fields[10],
                            'Predicate Arguments': [x for x in fields[11:-1]], 'Coreference': fields[-1]}
        self.coref = self.annotations['Coreference']

    def change_label(self, label):
        coref_chars = len(self.annotations['Coreference'])
        self.text = self.text[:-coref_chars - 1] + label + '\n'

    def write_results(self):

        start = ['(' + str(c) for c in self.predicted_coref['start'] if c not in self.predicted_coref['end']]
        end = [str(c) + ')' for c in self.predicted_coref['end'] if c not in self.predicted_coref['start']]
        complete = ['(' + str(c) + ')' for c in self.predicted_coref['start'].intersection(self.predicted_coref['end'])]
        parts = ['|'.join(start), '|'.join(complete), '|'.join(end)]
        s = '|'.join([part for part in parts if part])
        if s:
            self.change_label(s)
        else:
            self.change_label('-')
