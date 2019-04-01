# Listwise Learning to Rank by Exploring Unique Ratings
SIGIR2019 Paper Submission

- This is a temporary repo for our paper submission during the review period. 

- All files including test cases will be released from the official repo.

- We do not suggest that you fork this repo as it will not be maintained and it might be deleted afterward. 

- 5-fold results on the OHSUMED dataset (tested on a CPU) can be found in OHSUMED_uRank.txt and OHSUMED_urRank.txt


Feature, label serialization code: prepare_data.py

- An example of serialized data addressed in the paper can be found in folder: data/OHSUMED/2/ (Fold 2 of the OHSUMED dataset)
- The original OHSUMED dataset is in folder: learning_to_rank_data_sets_OHSUMED

Training code: main.py

Evaluation code: evaluate.py

Notices
- uRank_urRank/src/experiments/base_model/params.json defines hyper-parameters such as learning rate, batch_size, netowrk layer sizes, etc.
- "batch_size": 1 means one serialized instance obtained from prepare_data.py. One instance contains the feature vectors of all candidate documents that belong to the same query.
- There was a typo for $f(d)$ in Section 3.2 in the submission. We experimented two ways of calculating $f(d)$. $f(d) = \tilde{h}_t(d) w$, which corresponds to "rnn": "C1" in .../params.json works better with average-pooling. $f(d) = (\tilde{h}_t(d), \tilde{x}(d)) w$ works better with max-pooling. The two methods and better-tuned hyper-paramters will be explained in our next version of the paper.



This project is licensed under the terms of the MIT license.
