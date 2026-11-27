# Lesson 04. Learn from labeled questions

**Goal.** Follow the path from text features to a predicted fact and compute one gradient yourself. Use this lesson after you can explain retrieval and data splits.

## 1. Start with next-token counts

A bigram language model predicts the next token from the previous token. Count only training events and include an end-of-sequence token in the output vocabulary when you want to predict where examples end. With add-one smoothing, for $V$ possible next tokens,

$$
P(w\mid c)=\frac{C(c,w)+1}{C(c)+V}.
$$

If three occurrences of a context lead to A and one leads to B, with vocabulary $\{A,B\}$, the two probabilities are $4/6$ and $2/6$. The log-loss for observing A next is $-\log(4/6)\approx0.405$. Mean this loss across held-out tokens and exponentiate it to get perplexity. Compare perplexity for the same set of tokenized prediction events. QA accuracy is measured separately on fact predictions.

## 2. Understand embeddings

An embedding is a learned vector for a token. In Skip-gram, choose neighboring context tokens from a fixed window around each center token. The model uses an input embedding for the center and output embeddings for candidate context tokens. One simple training objective uses full softmax:

$$
P(o\mid c)=\frac{\exp(v_o^\top u_c)}
{\sum_{j=1}^{V}\exp(v_j^\top u_c)}.
$$

Here $u_c$ is the center embedding and $v_o$ is the candidate context embedding. If context scores are $[2,0]$, the probability of the first context is $e^2/(e^2+1)\approx0.881$. The observed context determines which negative log probability enters the loss. A two-sentence example is enough to inspect the gradients. Learn meaningful word relationships on a larger, documented corpus. [Mikolov et al. 2013](https://arxiv.org/abs/1301.3781)

For glossary QA, start with character n-gram features. Later compare them with a sentence vector built by averaging token embeddings. Mean pooling discards word order, which gives you a specific limitation to investigate.

## 3. Train a classifier

Given a vector of features for each question, a linear classifier computes logits $S=XW+b$. Each row of logits contains one score per available answer. Softmax converts the scores for example $i$ into probabilities. Use a rowwise maximum $m_i$ for numerical stability:

$$
m_i=\max_k S_{ik},\qquad
P_{ik}=\frac{\exp(S_{ik}-m_i)}{\sum_j\exp(S_{ij}-m_i)}.
$$

The mean cross-entropy for $B$ questions with gold class $y_i$ is

$$
L=-\frac{1}{B}\sum_{i=1}^{B}\log P_{i,y_i}.
$$

A linear model maps features directly to the output. An FFN (feedforward neural network) first creates a hidden representation. With $D$ input features, $H$ hidden units, and $K$ fact classes, the shapes are

| Symbol | Meaning | Shape |
| --- | --- | --- |
| $X$ | Input batch | $B\times D$ |
| $W_1,b_1$ | Hidden weights and bias | $D\times H$, $H$ |
| $W_2,b_2$ | Output weights and bias | $H\times K$, $K$ |
| $S,P$ | Logits and probabilities | $B\times K$ |

$$
Z=XW_1+b_1,\qquad A=\max(0,Z),\qquad S=AW_2+b_2.
$$

## 4. Derive the backward pass

For one question, cross-entropy equals the log of the sum of exponentials of the logits minus the gold logit. The derivative of the first term is the softmax probability, and the derivative of the second is 1 on the gold class. For a batch with one-hot labels $Y$, this gives

$$
G=\frac{P-Y}{B}.
$$

Working backward through the two matrices and the ReLU gives

$$
\nabla_{W_2}L=A^\top G,\qquad
\nabla_{b_2}L=\sum_i G_{i,:},\qquad
D_Z=(GW_2^\top)\odot \mathbf 1[Z>0],
$$

$$
\nabla_{W_1}L=X^\top D_Z,\qquad
\nabla_{b_1}L=\sum_i (D_Z)_{i,:}.
$$

After computing all gradients, update each parameter using learning rate $\eta$:

$$
W\leftarrow W-\eta\nabla_WL.
$$

**Worked example.** Let $X=[1,-1]$, both weight matrices be the $2\times2$ identity, both biases be zero, and the second class be correct. Then $A=[1,0]$, $S=[1,0]$, and $P\approx[0.731,0.269]$. Cross-entropy is about $1.313$. The first row of the output-weight gradient is $[0.731,-0.731]$. The second row is zero because the second hidden activation is zero. A gradient descent step lowers the first logit and raises the second for this example. [Goodfellow, Bengio, and Courville, Chapter 6](https://www.deeplearningbook.org/contents/mlp.html)

## 5. Exit exercise

1. Recalculate the cross-entropy with the first class as the gold label. Explain which term changed.
2. Multiply out $D_Z$ in the worked example with the original label.
3. When you implement the FFN, compare one analytical gradient with a numerical gradient. Perturb one weight at a time, restore it after each check, and stay away from the ReLU corner.

$$
\frac{\partial L}{\partial w}\approx
\frac{L(w+\epsilon)-L(w-\epsilon)}{2\epsilon}.
$$

**Self-check.** You can state the output shape at every stage, repeat one hand calculation in NumPy, and explain why the probabilities alone do not guarantee a reliable unknown detector.

Continue to [Lesson 05](05-sequence-models.md).
