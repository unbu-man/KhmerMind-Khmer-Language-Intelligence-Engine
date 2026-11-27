# Lesson 05. Read sequences

**Goal.** See how a model can use the order of tokens and compare that with the feature-based baseline. Work through this lesson once you can trace an FFN.

## 1. Recurrence

At token position $t$, a recurrent neural network combines the current token vector $x_t$ with its previous hidden state $h_{t-1}$:

$$
h_t=\tanh(x_tW_x+h_{t-1}W_h+b).
$$

For a scalar example with $W_x=W_h=1$, zero bias and initial state zero, input $[1,0]$ gives $h_1\approx0.762$ and $h_2\approx0.642$. Reverse it to $[0,1]$ and the final state is about $0.762$. An order-insensitive average gives the same result for both inputs. In a question classifier, pass the last **valid** state to the classifier. Mask padding so it cannot update that state. With backpropagation through time, accumulate gradient contributions to the shared weights across positions.

## 2. LSTM and GRU

An LSTM has a cell state $c_t$ as well as a hidden state. Its input, forget, and output gates $i_t,f_t,o_t$ are sigmoid outputs calculated from the current input and prior hidden state. The candidate $\tilde c_t$ usually uses tanh:

$$
c_t=f_t\odot c_{t-1}+i_t\odot\tilde c_t,\qquad
h_t=o_t\odot\tanh(c_t).
$$

With scalar cell state $0.6$, forget gate $0.9$, input gate $0.2$, and candidate $0.5$, the next cell state is $0.64$.

A GRU has reset and update gates. One convention defines $z_t$ as how much of the **candidate** to use. Then

$$
\tilde h_t=\tanh(x_tW_x+(r_t\odot h_{t-1})W_h+b),\qquad
h_t=(1-z_t)\odot h_{t-1}+z_t\odot\tilde h_t.
$$

Under this convention, $z_t=0$ preserves the previous state. Document the convention before comparing two implementations. [Hochreiter and Schmidhuber 1997](https://doi.org/10.1162/neco.1997.9.8.1735) · [Cho et al. 2014](https://aclanthology.org/D14-1179/)

## 3. Attention

Project the input sequence to queries $Q$, keys $K$, and values $V$. For each query, measure its affinity to the keys and use those weights to combine values:

$$
\operatorname{Attention}(Q,K,V)=
\operatorname{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}+M\right)V.
$$

$d_k$ is the key width. $M$ adds a negative-infinity mask to keys that should receive zero attention, such as padding. The softmax is applied across the keys for each query. Handle an all-masked sequence explicitly.

**Worked example.** One scalar query is $1$. The two scalar keys are $1$ and $0$, and their values are $2$ and $4$. With $d_k=1$, the scores are $[1,0]$ and the weights are about $[0.731,0.269]$. The weighted value is about $2.538$. If the second key is padding, it receives zero weight and the output becomes $2$.

## 4. Put attention in an encoder

A first Transformer encoder for fact classification can use a token embedding and a position embedding, an attention block, residual connections and normalization, and a positionwise feedforward block. Pool the valid outputs and score the candidate fact IDs. In multi-head attention, each head has its own input projections. Test one head on a toy example before stacking blocks. [Vaswani et al. 2017](https://arxiv.org/abs/1706.03762)

## 5. Exit exercise

- Change the second key in the worked example from $0$ to $2$. Calculate the new weights and weighted value.
- Explain how an RNN classifier and a Transformer encoder each treat padding.
- Design one Khmer query pair where changing the position of words could change meaning. Decide whether the character baseline, mean embedding, or sequence model can represent that difference.

**Self-check.** You can trace a recurrent state on paper, compute the attention weights before reading code, and name a check that verifies padding does not change a prediction.

Continue to [Lesson 06](06-continual-learning.md).
