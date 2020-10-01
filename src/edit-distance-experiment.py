from strsimpy.normalized_levenshtein import NormalizedLevenshtein
from strsimpy.jaro_winkler import JaroWinkler
from strsimpy.cosine import Cosine
from strsimpy.jaccard import Jaccard
from strsimpy.sorensen_dice import SorensenDice
from strsimpy.overlap_coefficient import OverlapCoefficient

test_cases = [
    ['Eyexpert The Volume Expert Mascara', 'Eyexpertvolume Expert Mascara'],
    ['Cheek Lit Pressed Blush', 'Cheek Lit Cream Blush'],
    ['Color Trend 2018 Lip Cream', 'Matte Lip Cream'],
    ['Bedak Jerawat Energizing Aromatic', 'Masker Jerawat'],
    ['Duo Make Up', 'Duo Eye Make Up'],
    ['3.5 g', '3.7 g'],
    ['Autocantik Package Natglow', 'Tinted Moisturizer'],
    ['SariayuTrendWarna2011MoistpomeEyeShadow', 'SariayuColorTrendWarna2011MoistpomeEyeShadowPalette'],
    ['SariayuColorTrend2017LiquidEyeShadow', 'SariayuColorTrend2016EyeShadow'],
    ['0.2 g', '0.20 g'],
    ['Blush On', 'On Blush']
]

normalized_levenshtein = NormalizedLevenshtein()
jarowinkler = JaroWinkler()
cosine = Cosine(1)
jaccard = Jaccard(1)
sorensen = SorensenDice()
overlap = OverlapCoefficient()

functions = [normalized_levenshtein, jarowinkler, cosine, jaccard, sorensen, overlap]

function_name = {
    0 : "Normalized Levenshtein",
    1 : "Jaro Winkler",
    2 : "Cosine",
    3 : "Jaccard",
    4 : "Sorensen Dice",
    5 : "Overlap Coefficient"
}

for test_case in test_cases :
    print (test_case)
    max_name = ""
    max_similarity = 0
    for idx, function in enumerate(functions) :
        name = function_name[idx]
        similarity = function.similarity(test_case[0], test_case[1])
        if (similarity > max_similarity) :
            max_similarity = similarity
            max_name = name
        print (name, similarity)
    print ("MAXIMUM", max_name, max_similarity)
    print ()