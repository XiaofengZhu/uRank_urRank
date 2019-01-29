# Generate serialized TF records
# python prepare_data.py

import os
import argparse
import json
import numpy as np
import tensorflow as tf
import argparse
import logging

# change it accordingly
DATA_SET_FOLDER = 'learning_to_rank_data_sets'


def get_OHSUMED_data_path(tfrecords_folder, fold_str, file_type):
    OHSUMED_data = "OHSUMED/Feature-min/"
    OHSUMED_data_folder = OHSUMED_data + 'Fold' + str(fold_str) + '/'
    # OHSUMED
    # print('file_type', file_type)
    full_file_name = os.path.join(DATA_SET_FOLDER, OHSUMED_data_folder + file_type)
    if file_type == 'train':
        full_file_name += 'ing'        
    if file_type == 'vali':
        full_file_name += 'dation'
    full_file_name += 'set'
    data_path = full_file_name + '.txt'
    return data_path  


def get_data_path(tfrecords_folder, fold_str, file_type):
    data_path = ''
    # OHSUMED
    if tfrecords_folder == 'OHSUMED':
        data_path = get_OHSUMED_data_path(tfrecords_folder, fold_str, file_type)
    else:
        # MQ2007_data
        MQ2007_or_MQ2008_data_folder = tfrecords_folder + '/Fold' + str(fold_str) + '/'
        data_path = os.path.join(DATA_SET_FOLDER, MQ2007_or_MQ2008_data_folder + file_type + ".txt") 
    return data_path 


def normalize_mean_max_feature_array(array):
    mean = array.mean(axis = 0)
    abs_max = abs(array.max(axis = 0))
    epilson = 1e-8
    abs_max = abs_max + epilson
    normalized_array = (array - mean) / abs_max
    return normalized_array

def normalize_min_max_feature_array(array):
    mini = array.min(axis = 0)
    maxi = array.max(axis = 0)
    epilson = 1e-8
    value_range = maxi - mini + epilson
    normalized_array = (array - mini) / value_range
    return normalized_array


def save_dict_to_json(d, json_path):
    """Saves dict to json file
    Args:
        d: (dict)
        json_path: (string) path to json file
    """
    with open(json_path, 'w') as f:
        d = {k: v for k, v in d.items()}
        json.dump(d, f, indent=4)


def _bytes_feature(value):
    value = value if type(value) == list else [value]
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=value))

def _int64_feature(value):
    value = value if type(value) == list else [value]
    return tf.train.Feature(int64_list=tf.train.Int64List(value=value))

def _float_feature(value):
    value = value if type(value) == list else [value]
    return tf.train.Feature(float_list=tf.train.FloatList(value=value))

def convert(tfrecords_folder, file_type, fold):

    group_features = {}
    group_labels = {}
    fold = str(fold)
    data_path = get_data_path(tfrecords_folder, fold, file_type)
    print('data_path', data_path)

    if file_type == 'vali':
        file_type = 'eval'
    tfrecords_filename = tfrecords_folder + '.tfrecords'
    complete_file_name = os.path.join('../data/', tfrecords_folder, fold, file_type + "_" + tfrecords_filename)
    writer = tf.python_io.TFRecordWriter(complete_file_name)

    with open(data_path, "r") as f:
        for line in f:
            if not line:
                break
            if "#" in line:
                line = line[:line.index("#")]
            splits = line.strip().split(" ")
            label = float(splits[0])
            group = int(splits[1].split(":")[1])
            features = [float(split.split(":")[1]) for split in splits[2:]]
            
            if group in group_features:
                new_feature_list = group_features[group]
                new_feature_list.append(features)
                group_features[group] = new_feature_list

                new_label_list = group_labels[group]
                new_label_list.append(label)
                group_labels[group] = new_label_list 
            else:
                feature_list = []   
                feature_list.append(features)
                group_features[group] = feature_list  

                label_list = []   
                label_list.append(label)
                group_labels[group] = label_list                 

    query_ids = list(group_features.keys())
    query_ids.sort()
    # print('fold', fold, ', len', len(query_ids), ', file_type', file_type, ', query_ids', query_ids)
    
    feature_dim = 0
    doc_count = 0

    for group in group_features:
        label_list = group_labels[group]
        label_array = np.asarray(label_list, dtype=np.float32)
        # remove all 0 label entries
        if label_array.sum() < 1:
            continue
        feature_array = np.asarray(group_features[group], dtype=np.float32)
        normalized_feature_array = normalize_min_max_feature_array(feature_array)
        feature_raw = normalized_feature_array.tostring()
        # number of documents
        height = normalized_feature_array.shape[0]
        # feature dim
        width = normalized_feature_array.shape[1]
        label_list = group_labels[group]
        doc_count += height

        example = tf.train.Example(features=tf.train.Features(feature={
            'height': _int64_feature(height),
            'width': _int64_feature(width),
            'feature_raw': _bytes_feature(feature_raw),
            'label': _float_feature(label_list)}))
        writer.write(example.SerializeToString())
    
    writer.close()
    query_ids = list(group_features.keys())
    feature_list_0 = group_features[query_ids[0]]
    feature_dim = len(feature_list_0[0])
    return len(query_ids), feature_dim, doc_count


def main():
    tfrecords_folders = ['OHSUMED', 'MQ2007', 'MSLR-WEB10K', 'MSLR-WEB30K']
    folds = 5
    for tfrecords_folder in tfrecords_folders:
        for fold in range(1, folds + 1):
            write2folder = os.path.join('../data/', tfrecords_folder, str(fold))
            if not os.path.exists(write2folder):
                os.makedirs(write2folder)
            # use eval in the write part of tfrecords for now
            eval_size, eval_feature_dim, eval_doc_count = convert(tfrecords_folder, 'vali', fold)
            test_size, test_feature_dim, test_doc_count = convert(tfrecords_folder, 'test', fold)
            train_size, train_feature_dim, train_doc_count = convert(tfrecords_folder, 'train', fold)
                # Save datasets properties in json file
            sizes = {
                'feature_dim': train_feature_dim,
                'train_size': train_size,
                'train_doc_count': train_doc_count,
                'eval_size': eval_size,
                'eval_doc_count': eval_doc_count,
                'test_size': test_size,
                'test_doc_count': test_doc_count
                }
            save_dict_to_json(sizes, os.path.join(write2folder, 'dataset_params.json'))            


if __name__ == "__main__":
    main()
    print("Done!")