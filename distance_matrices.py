import numpy as np
import helperfuncs
import MySQL_DB
import Amazon
import Flipkart
import streamlit as st


def GetData(KEYWORD, include_features=False):
    Amazon.ScrappingAmazon(KEYWORD, include_features=include_features)
    Flipkart.ScrappingFlipkart(KEYWORD)
    #print(f'\nShowing results for {KEYWORD}:')
    st.info(f'Showing results for {KEYWORD}:')


def textformat(text):
    formatter = helperfuncs.TextFormatting(text)
    formatter.RemoveTagsAndPunctuations()
    formatter.ToLower()
    formatter.RemoveStopWords()
    return formatter.text


def distance_calc(shape):
    amazon = MySQL_DB.getamazon(shape)
    dist_matrix = np.zeros((shape, shape))
    i = 0
    try:
        for amazon_product in amazon:
            words1 = textformat(amazon_product)
            words1 = words1.split(" ")
            len1 = len(words1)
            flipkart = MySQL_DB.getflipkart(shape)
            temp_score = []
            for flipkart_product in flipkart:
                counter = 0
                words2 = textformat(flipkart_product)
                words2 = words2.split(" ")
                len2 = len(words2)
                for word in words2:
                    if word in words1:
                        counter += 1
                if len1 >= len2:
                    counter /= len2
                else:
                    counter /= len1

                temp_score.append(counter)

            dist_matrix[i] = temp_score
            i += 1
    except Exception as e:
        pass
        #print(e)
        #print(f'{shape} record(s) are not available to compare')

    return dist_matrix


def compare(matrix, info, confidence_score=0.5, omit=False):
    #print('')
    sl = np.argwhere(matrix[:, :] > confidence_score)
    product_id = sl[:, 0]
    try1 = np.unique(product_id)
    max_dict = dict.fromkeys(product_id, [0.49, None])
    con_dict = dict.fromkeys(product_id, [])
    sl = sl.tolist()

    for indices in sl:
        val = matrix[indices[0], indices[1]]
        if max_dict[indices[0]][0] < val:
            max_dict[indices[0]] = [val, indices[1]]

    for indices in try1:
        temp = []
        flag = False
        for indices1 in sl:
            if indices == indices1[0]:
                temp.append(indices1)
                flag = True
            else:
                if not flag:
                    continue
                else:
                    break
        con_dict[indices] = temp

    pairs = np.ones((len(try1), 2)).astype('int32')
    i = 0
    for key, val in max_dict.items():
        pairs[i] = [key, val[1]]
        i += 1

    MySQL_DB.retrivedata(pairs, con_dict, info)


def db_disconnect():
    MySQL_DB.disconnect()


def num_entries():
    count = MySQL_DB.count()
    return count


def truncating():
    MySQL_DB.truncate()


def view_db(KEYWORD):
    MySQL_DB.view_db(KEYWORD, omit=False)