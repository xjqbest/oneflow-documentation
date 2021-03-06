import oneflow as flow
from mnist_util import load_data
import oneflow.typing as oft

BATCH_SIZE = 100


def get_train_config():
    config = flow.function_config()
    config.default_data_type(flow.float)
    config.train.primary_lr(0.1)
    config.train.model_update_conf({"naive_conf": {}})
    return config


@flow.global_function(get_train_config())
def train_job(images:oft.Numpy.Placeholder((BATCH_SIZE, 1, 28, 28), dtype=flow.float),
              labels:oft.Numpy.Placeholder((BATCH_SIZE,), dtype=flow.int32)):
    # mlp
    initializer = flow.truncated_normal(0.1)
    reshape = flow.reshape(images, [images.shape[0], -1])
    hidden = flow.layers.dense(reshape, 512, activation=flow.nn.relu, kernel_initializer=initializer)
    logits = flow.layers.dense(hidden, 10, kernel_initializer=initializer)

    loss = flow.nn.sparse_softmax_cross_entropy_with_logits(labels, logits, name="softmax_loss")

    flow.losses.add_loss(loss)
    return loss


g_i = 0


def cb_print_loss(result):
    global g_i
    if g_i % 20 == 0:
        print(result.mean())
    g_i += 1


def main_train():
    # flow.config.enable_debug_mode(True)
    check_point = flow.train.CheckPoint()
    check_point.init()

    (train_images, train_labels), (test_images, test_labels) = load_data(BATCH_SIZE)
    for epoch in range(50):
        for i, (images, labels) in enumerate(zip(train_images, train_labels)):
            train_job(images, labels).async_get(cb_print_loss)

    check_point.save('./mlp_models_1')  # need remove the existed folder


if __name__ == '__main__':
    main_train()



