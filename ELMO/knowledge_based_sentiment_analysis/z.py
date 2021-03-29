#from allennlp.commands import ElmoEmbedder
import tensorflow_hub as hub
import tensorflow as tf
#elmo = hub.Module("https://tfhub.dev/google/elmo/1",trainable = True)
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
	# Currently, memory growth needs to be the same across GPU
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        logical_gpus = tf.config.experimental.list_logical_devices('GPU')
    except RuntimeError as e:
        print(e)
    # Memory growth must be set before GPUs have been initialize

file = open("./input.txt", "r")
stop_list = file.read().split(' ')
print(len(stop_list))
tokens = ''
for w in stop_list:
    tokens+= w+' '
    '''
    if '\n' in w:
        add=''
        for a in w:
            if a == '\n':
                break
            add += a
        tokens.append(add)
    else:
        tokens.append(w)
    '''
print(tokens)

for i in range(0,1):
    tf_tokens = tf.constant([tokens])
    embed = hub.load("https://tfhub.dev/google/elmo/3")
    keyword_output = embed.signatures['default'](tf_tokens)
    print(keyword_output['word_emb'])

