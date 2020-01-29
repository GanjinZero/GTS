import tensorflow as tf
from . import tokenization
from . import modeling
from time import time
from tqdm import tqdm
import math
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


class bert_predictor(object):
    def __init__(self, max_sequence_length, bert_config_file, model_path, vocab_file, batch_size=192):
        self.max_sequence_length = max_sequence_length
        self.batch_size = batch_size

        sess = tf.Session()
        tokenizer = tokenization.FullTokenizer(vocab_file=vocab_file, do_lower_case=True)
        bert_config = modeling.BertConfig.from_json_file(bert_config_file)

        input_ids = tf.placeholder(tf.int32, shape=[None, max_sequence_length], name='input_ids')
        input_mask = tf.placeholder(tf.int32, shape=[None, max_sequence_length], name='input_mask')
        segment_ids = tf.placeholder(tf.int32, shape=[None, max_sequence_length], name='segment_ids')

        with sess.as_default():
            model = modeling.BertModel(
                config=bert_config,
                is_training=False,
                input_ids=input_ids,
                input_mask=input_mask,
                token_type_ids=segment_ids,
                use_one_hot_embeddings=False)

            output_layer = model.get_pooled_output()

            hidden_size = output_layer.shape[-1].value

            output_weights = tf.get_variable(
                "output_weights", [2, hidden_size],
                initializer=tf.truncated_normal_initializer(stddev=0.02))

            output_bias = tf.get_variable(
                "output_bias", [2], initializer=tf.zeros_initializer())
    
            with tf.variable_scope("loss"):
                logits = tf.matmul(output_layer, output_weights, transpose_b=True)
                logits = tf.nn.bias_add(logits, output_bias)
                probabilities = tf.nn.softmax(logits, axis=-1)
                log_probs = tf.nn.log_softmax(logits, axis=-1)

            saver = tf.train.Saver()
            sess.run(tf.global_variables_initializer())
            saver.restore(sess, model_path)

        self.sess = sess
        self.tokenizer = tokenizer

    def text_process(self, text):
        tokens_1 = self.tokenizer.tokenize(text)
        tokens = []
        tokens.append("[CLS]")
        for token in tokens_1[0:min(self.max_sequence_length - 2, len(tokens_1))]:
            tokens.append(token)
        tokens.append("[SEP]")

        input_ids = self.tokenizer.convert_tokens_to_ids(tokens)
        input_mask = [1] * len(input_ids)

        append_part = [0] * max(0, self.max_sequence_length - len(input_ids))
        input_ids += append_part
        input_mask += append_part
        segment_ids = [0] * self.max_sequence_length

        return input_ids, input_mask, segment_ids

    def text_process_list(self, text_list):
        input_id_list = []
        input_mask_list = []
        segment_id_list = []
        for text in text_list:
            input_ids, input_mask, segment_ids = self.text_process(text)
            input_id_list.append(input_ids)
            input_mask_list.append(input_mask)
            segment_id_list.append(segment_ids)
        return input_id_list, input_mask_list, segment_id_list

    def predict_tensor(self, input_id_list, input_mask_list, segment_id_list, verbose=0):
        input_ids_tensor = self.sess.graph.get_tensor_by_name('input_ids:0')
        input_mask_tensor = self.sess.graph.get_tensor_by_name('input_mask:0')
        segment_ids_tensor = self.sess.graph.get_tensor_by_name('segment_ids:0')
        output_tensor = self.sess.graph.get_tensor_by_name('loss/Softmax:0')

        output = []
        if verbose == 0:
            for i in range(math.ceil(len(input_id_list) / self.batch_size)):
                input_ids = input_id_list[i * self.batch_size: min((i + 1) * self.batch_size, len(input_id_list))]
                input_mask = input_mask_list[i * self.batch_size: min((i + 1) * self.batch_size, len(input_id_list))]
                segment_ids = segment_id_list[i * self.batch_size: min((i + 1) * self.batch_size, len(input_id_list))]
        
                fd = {input_ids_tensor: input_ids, input_mask_tensor: input_mask, segment_ids_tensor: segment_ids}
                result = self.sess.run([output_tensor], feed_dict=fd)[0][:,0].tolist()
                output += result
        else:
            for i in tqdm(range(math.ceil(len(input_id_list) / self.batch_size))):
                input_ids = input_id_list[i * self.batch_size: min((i + 1) * self.batch_size, len(input_id_list))]
                input_mask = input_mask_list[i * self.batch_size: min((i + 1) * self.batch_size, len(input_id_list))]
                segment_ids = segment_id_list[i * self.batch_size: min((i + 1) * self.batch_size, len(input_id_list))]
        
                fd = {input_ids_tensor: input_ids, input_mask_tensor: input_mask, segment_ids_tensor: segment_ids}
                result = self.sess.run([output_tensor], feed_dict=fd)[0][:,0].tolist()
                output += result
    
        return output

    def predict(self, text_list, verbose=0):
        input_id_list, input_mask_list, segment_id_list = self.text_process_list(text_list)
        return self.predict_tensor(input_id_list, input_mask_list, segment_id_list, verbose)

if __name__ == "__main__":
    vocab_file = '/media/sdc/GanjinZero/context/1280000_output/vocab.txt'
    bert_config_file = '/media/sdc/GanjinZero/context/1280000_output/bert_config.json'
    model_path = '/media/sdc/GanjinZero/context/1280000_output/model.ckpt-30000'
    max_sequence_length = 32

    text1 = '___，患者2008'

    # init model
    t1 = time()
    predictor = bert_predictor(max_sequence_length, bert_config_file, model_path, vocab_file)
    print("init time: %.4f s" % (time() - t1))

    # predict
    t2 = time()
    predictor.predict([text1] * 2048)
    print("predict time: %.4f s" % (time() - t2))
