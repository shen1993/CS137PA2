from nltk.corpus import wordnet as wn


class MentionPair(object):
    def __init__(self, antecedent, anaphor):
        self.antecedent = antecedent
        self.anaphor = anaphor

        if antecedent.label == anaphor.label:
            self.label = True
        else:
            self.label = False

    def features(self):
        antecedent_features = self.antecedent.get_features()
        anaphor_features = self.anaphor.get_features()
        f = {'antecedent_' + x: antecedent_features[x] for x in antecedent_features if
             x != 'text' and antecedent_features[x] != None}

        for x in anaphor_features:
            if x != 'text' and anaphor_features[x] != None:
                f['anaphor_' + x] = anaphor_features[x]

        ant_extent, ana_extent = self.ne_finder(antecedent_features, anaphor_features)

        f['string_match'] = 1 if antecedent_features['text'] == anaphor_features['text'] else 0
        f['NE_match'] = 1 if f['antecedent_NE'] == f['anaphor_NE'] and f['antecedent_NE'] != '' else 0
        distance = anaphor_features['sentenceID'] - antecedent_features['sentenceID']
        f['distance'] = distance if distance < 5 else 5
        f['same_sent'] = 1 if distance == 0 else 0
        # f['head_match'] = 1 if ant_extent and ana_extent and ant_extent[0].split(' ')[0] == ana_extent[0].split(' ')[
        #     0] else 0
        # f['extent_match'] = 1 if ant_extent and ana_extent and (
        #     ant_extent[0] in ana_extent or ana_extent[0] in ant_extent) else 0
        #
        # f['modifier_match'] = 1 if f['antecedent_modifier'] == f['anaphor_modifier'] == 1 \
        #                            and antecedent_features['text'].split(' ')[0] == anaphor_features['text'].split(' ')[
        #     0] else 0
        #
        # f['substring_match'] = 1 if antecedent_features['text'] in anaphor_features['text'] \
        #                             or anaphor_features['text'] in antecedent_features['text'] else 0
        #
        # f['number_match'] = 1 if f['antecedent_singular'] == f['anaphor_singular'] == 1 \
        #                          or f['antecedent_plural'] == f['anaphor_plural'] == 1 else 0
        # f['gender_match'] = 1 if f['antecedent_male'] == f['anaphor_male'] == 1 \
        #                          or f['antecedent_female'] == f['anaphor_female'] == 1 else 0
        #
        # f['similarity'] = self.similarity(antecedent_features, anaphor_features)
        # f['hypernym_match'] = self.common_hypernym(antecedent_features, anaphor_features)

        f_return_me = {'string_match': f['string_match'],
                       'distance': f['distance'],
                       'same_sent': f['same_sent'],
                       'NE_match': f['NE_match'],

                       # 'head_match': f['head_match'],
                       # 'extent_match': f['extent_match'],
                       # 'modifier_match': f['modifier_match'],
                       # 'substring_match': f['substring_match'],
                       #
                       # 'gender_match': f['gender_match'],
                       # 'number_match': f['number_match'],
                       #
                       # 'similarity': f['similarity'],
                       # 'hypernym_match': f['hypernym_match']
                       }

        return f_return_me

    def similarity(self, antecedent_features, anaphor_features):
        ant_synset = wn.synsets(antecedent_features['text'].split(' ')[0])
        ana_synset = wn.synsets(anaphor_features['text'].split(' ')[0])
        if ant_synset and ana_synset:
            sim = ant_synset[0].path_similarity(ana_synset[0])
            if sim != None:
                return sim
            else:
                return 0
        else:
            return 0

    root_hypernyms = []
    root_hypernyms.extend(wn.synsets('entity'))
    root_hypernyms.extend(wn.synsets('abstraction'))
    root_hypernyms.extend(wn.synsets('physical_entity'))
    root_hypernyms.extend(wn.synsets('object'))
    root_hypernyms.extend(wn.synsets('whole'))
    root_hypernyms.extend(wn.synsets('artifact'))
    root_hypernyms.extend(wn.synsets('group'))

    def common_hypernym(self, antecedent_features, anaphor_features):
        ant_synset = wn.synsets(antecedent_features['text'].split(' ')[0])
        ana_synset = wn.synsets(anaphor_features['text'].split(' ')[0])
        if ant_synset and ana_synset:
            ch = ant_synset[0].lowest_common_hypernyms(ana_synset[0])
            if ch:
                if ch[0] not in self.root_hypernyms:
                    return 1
                else:
                    return 0
            else:
                return 0
        else:
            return 0

    def ne_finder(self, antecedent_features, anaphor_features):
        ant_extent = []
        ana_extent = []

        found_head = False
        for token in antecedent_features['text'].split(' '):
            if not found_head and token[0].isupper():
                found_head = True
                ext = token
            elif found_head and token[0].isupper():
                ext = ext + " " + token
            elif found_head and token[0].islower():
                found_head = False
                ant_extent.append(ext)

        found_head = False
        for token in anaphor_features['text'].split(' '):
            if not found_head and token[0].isupper():
                found_head = True
                ext = token
            elif found_head and token[0].isupper():
                ext = ext + " " + token
            elif found_head and token[0].islower():
                found_head = False
                ana_extent.append(ext)

        return ant_extent, ana_extent
