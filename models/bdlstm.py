import tensorflow as tf
import sys
sys.path.append('..')
from flags import FLAGS


class RecurrentModel:
    def __init__(self):
        pass

    def construct_model(self, x, x_len, output_mask, y, embed, kp_emb, kp_lstm):
        yhat, asdf = self.build_lstm(x, x_len, output_mask, embed, kp_emb, kp_lstm)
        return yhat, self.compute_loss(y, yhat), asdf

    def build_lstm(self, x, x_len, output_mask, embed, kp_emb, kp_lstm):
        x = tf.unstack(x, axis=1)
        for i in range(len(x)):
            x[i] = tf.nn.embedding_lookup(embed, x[i])
        x = tf.stack(x, axis=1)

        x = tf.nn.dropout(x, keep_prob=kp_emb)

        lstm = tf.nn.rnn_cell.MultiRNNCell([self.get_lstm(kp_lstm) for _ in range(FLAGS.rnn_num_layers)])
        output, state = tf.nn.dynamic_rnn(cell=lstm, inputs=x, sequence_length=x_len, dtype=tf.float32)

        add_weight = tf.get_variable('post_lstm_weight', shape=(FLAGS.rnn_cell_size, FLAGS.num_classes),
                                     initializer=tf.contrib.layers.xavier_initializer())
        add_bias = tf.get_variable('post_lstm_bias', shape=FLAGS.num_classes,
                                   initializer=tf.contrib.layers.xavier_initializer())

        return tf.matmul(tf.boolean_mask(output, output_mask), add_weight) + add_bias, output

    @staticmethod
    def get_lstm(kp_lstm):
        return tf.nn.rnn_cell.DropoutWrapper(
            tf.nn.rnn_cell.LSTMCell(FLAGS.rnn_cell_size),
            input_keep_prob=kp_lstm,
            state_keep_prob=kp_lstm,
            output_keep_prob=kp_lstm
        )

    @staticmethod
    def compute_loss(y, yhat):
        return tf.nn.softmax_cross_entropy_with_logits_v2(labels=y, logits=yhat)
